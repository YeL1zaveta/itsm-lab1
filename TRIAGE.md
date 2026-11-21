---
lab5_triage:
  image: ghcr.io/yel1zaveta/itsm-lab1@sha256:TU_WKLEJ_DIGEST
  sarif_receipt: 0
---
<!-- ai-generated: 60% - Claude drafted the table and the bake-off reading from my matrix and per-defect output, I checked every number -->
# Triage

What the gates and the reporting scanners found on my service, and what I did about each.

| Tool | Rule | Decision | Reason |
|---|---|---|---|
| semgrep | dockerfile.security.missing-user.missing-user | accept | Dockerfile line 17 runs uvicorn as root; I accept it for now because a non-root user would need ownership changes on the /data volume that stores tickets.json, and I did not want to risk the build-test gate. |
| trivy | CVE-2020-14343 | accept | PyYAML 5.3.1 in lab5-canary/requirements.txt: a seeded defect of the canary set, not part of my service (src/requirements.txt is clean), kept so the bake-off can score it. |
| gitleaks | generic-api-key | accept | The planted key in lab5-canary/config/search.py is a seeded defect of the canary set, not a credential of my service; it stays so the bake-off can score it. |
| gitleaks | private-key | accept | The planted key in lab5-canary/config/signing_key.py is a seeded defect of the canary set, not a credential of my service; it stays so the bake-off can score it. |

## Bake-off

On the nine seeded defects of the canary set, no scanner found more than four. Trivy found three (both dependency pins and the private key) with no false positive, precision 1.0, recall 0.333, F1 0.5. Gitleaks found two secrets with precision 1.0 and recall 0.222. Grype and OSV-Scanner found exactly the same two vulnerable pins, so on dependencies they added nothing over Trivy. Semgrep had the best recall, 0.444 with four defects, but three false positives, precision 0.571 and F1 0.5. I would put Trivy in the gate: it never cried wolf here, it has the highest recall of the zero-false-positive tools, and it already covers both dependencies and secrets. Semgrep stays report-only, because a gate that is wrong in more than one finding in three teaches people to ignore it. What surprised me is that three scanners agreed perfectly on dependencies, while Semgrep also caught two of the three secrets. Six defects were found by at least one tool, a union recall of 0.667; three were found by none: the weak-crypto defect in reset_tokens.py, the access-control defect in ticket_access.py and the secret in mailer.py. The first two are weaknesses of logic, where no fixed pattern marks the line as wrong, and the secret was probably one that no gitleaks rule recognised; all three need context rather than a signature. Every recall here is an upper bound: the defects are seeded, deliberately plain, planted in files every tool scans, and surrounded by no real code, so a real codebase would be harder for every detector, and the defects nobody knows about are not counted at all.