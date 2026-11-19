# ai-generated: 90% - written by Claude from CI-SPEC.md P-14..P-23; I tested it on the practice set
"""bakeoff.py: SARIF + labels -> confusion matrix per tool (CI-SPEC.md section 3).

Usage: python3 -S -E bakeoff.py --labels <labels.json> <sarif> [<sarif> ...]
Standard library only.
"""
import json
import re
import sys
from urllib.parse import unquote

CLASSES = {
    "secret": {259, 260, 321, 798},
    "injection": {74, 77, 78, 79, 80, 88, 89, 90, 91, 94, 95, 96, 611, 776, 917, 943, 1336},
    "deserialization": {502},
    "weak-crypto": {261, 326, 327, 328, 330, 331, 338, 759, 760, 916},
    "insecure-transport": {295, 297, 319, 322, 757},
    "path-traversal": {22, 23, 35, 36, 73},
    "ssrf": {918},
    "vulnerable-dependency": {937, 1035, 1104, 1395},
    "misconfiguration": {16, 215, 250, 489, 668, 732, 1188},
    "access-control": {284, 285, 639, 862, 863},
}
SEMGREP_NAMES = {"semgrep", "semgrep oss", "semgrep ce", "semgrep community edition", "semgrep pro"}
CWE_RE = re.compile(r"(?<![A-Za-z0-9])cwe-(\d+)", re.IGNORECASE)
TOKEN_RE = re.compile(r"[A-Za-z0-9._-]+")


def as_dict(x):
    return x if isinstance(x, dict) else {}


def as_list(x):
    return x if isinstance(x, list) else []


def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


# ---- P-15 tool ids
def tool_id(run):
    name = as_dict(as_dict(run.get("tool")).get("driver")).get("name")
    if not isinstance(name, str):
        return "unknown"
    n = name.strip().lower()
    if n in SEMGREP_NAMES:
        return "semgrep"
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n or "unknown"


# ---- P-17 paths
def result_file(uri, root):
    p = unquote(uri)
    if p[:7].lower() == "file://":
        p = p[7:]
    if p.startswith("./"):
        p = p[2:]
    parts = p.split("/")
    idx = [i for i, c in enumerate(parts) if c == root]
    if not idx:
        return None
    return "/".join(parts[idx[-1]:])


# ---- P-18 lines
def result_lines(region):
    region = as_dict(region)
    s = region.get("startLine")
    if not is_int(s) or s < 1:
        return None, None
    e = region.get("endLine")
    if not is_int(e) or e < s:
        e = s
    return s, e


# ---- P-19 classes
def string_tags(props):
    return [t for t in as_list(as_dict(props).get("tags")) if isinstance(t, str)]


def result_classes(res, run, tid):
    props = as_dict(res.get("properties"))
    own = props.get("class")
    if isinstance(own, str) and own in CLASSES:
        return {own}
    rule_tags = []
    rid = res.get("ruleId")
    if isinstance(rid, str):
        for rule in as_list(as_dict(as_dict(run.get("tool")).get("driver")).get("rules")):
            if isinstance(rule, dict) and rule.get("id") == rid:
                rule_tags = string_tags(rule.get("properties"))
                break
    if tid == "gitleaks":
        return {"secret"}
    if tid in ("grype", "osv-scanner"):
        return {"vulnerable-dependency"}
    if tid == "trivy":
        got = set()
        for t in rule_tags:
            tl = t.lower()
            if tl == "vulnerability":
                got.add("vulnerable-dependency")
            elif tl == "secret":
                got.add("secret")
            elif tl == "misconfiguration":
                got.add("misconfiguration")
        if got:
            return got
    got = set()
    for t in string_tags(props) + rule_tags:
        for m in CWE_RE.finditer(t):
            n = int(m.group(1))
            for cls, nums in CLASSES.items():
                if n in nums:
                    got.add(cls)
    return got or {"other"}


# ---- P-20 package tokens
def norm_pkg(s):
    return re.sub(r"[-_.]+", "-", s.lower())


def names_package(text, package):
    want = norm_pkg(package)
    for tok in TOKEN_RE.findall(text):
        tok = tok.strip("._-")
        if tok and norm_pkg(tok) == want:
            return True
    return False


def matches(r, d):
    if r["file"] != d.get("file") or d.get("class") not in r["classes"]:
        return False
    if d.get("class") == "vulnerable-dependency":
        text = r["text"]
        pkg = d.get("package")
        return isinstance(text, str) and isinstance(pkg, str) and names_package(text, pkg)
    if r["start"] is None:
        return False
    ds, de = d.get("start_line"), d.get("end_line")
    if not is_int(ds) or not is_int(de):
        return False
    return r["start"] <= de and ds <= r["end"]


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def collect(sarif_paths, root):
    tools = {}
    for path in sarif_paths:
        try:
            doc = load_json(path)
        except Exception:
            continue
        for run in as_list(as_dict(doc).get("runs")):
            if not isinstance(run, dict):
                continue
            tid = tool_id(run)
            bucket = tools.setdefault(tid, [])
            for res in as_list(run.get("results")):
                if not isinstance(res, dict):
                    continue
                kind = res.get("kind")
                if kind is not None and kind != "fail":
                    continue
                if res.get("suppressions"):
                    continue
                locs = as_list(res.get("locations"))
                if not locs or not isinstance(locs[0], dict):
                    continue
                phys = as_dict(locs[0].get("physicalLocation"))
                uri = as_dict(phys.get("artifactLocation")).get("uri")
                if not isinstance(uri, str) or not uri:
                    continue
                f = result_file(uri, root)
                if f is None:
                    continue
                s, e = result_lines(phys.get("region"))
                rid = res.get("ruleId")
                text = as_dict(res.get("message")).get("text")
                bucket.append({
                    "file": f, "start": s, "end": e,
                    "rule": ("s", rid) if isinstance(rid, str) else ("n",),
                    "classes": result_classes(res, run, tid),
                    "text": text if isinstance(text, str) else None,
                })
    return tools


def r4(x):
    return None if x is None else round(x, 4)


def main(argv):
    labels_path = None
    files = []
    i = 0
    while i < len(argv):
        if argv[i] == "--labels" and i + 1 < len(argv):
            labels_path = argv[i + 1]
            i += 2
        else:
            files.append(argv[i])
            i += 1
    labels = as_dict(load_json(labels_path))
    root = labels.get("set")
    defects = [d for d in as_list(labels.get("defects")) if isinstance(d, dict)]
    tools = collect(files, root)
    out = {}
    for tid, results in tools.items():
        found = set()
        fps = set()
        for r in results:
            hit = False
            for k, d in enumerate(defects):
                if matches(r, d):
                    found.add(k)
                    hit = True
            if not hit:
                fps.add((r["rule"], r["file"], r["start"], r["end"]))
        tp = len(found)
        fn = len(defects) - tp
        fp = len(fps)
        out[tid] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": r4(tp / (tp + fp)) if tp + fp else None,
            "recall": r4(tp / (tp + fn)) if tp + fn else None,
            "f1": r4(2 * tp / (2 * tp + fp + fn)) if 2 * tp + fp + fn else None,
        }
    print(json.dumps({"set": root, "defects": len(defects), "tools": out}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))