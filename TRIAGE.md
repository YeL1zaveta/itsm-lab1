---
lab5_triage:
  image: ghcr.io/yel1zaveta/itsm-lab1@sha256:8aff4e9a79eb284c829e15264f4f64ee91f83498d551a3ba37542d839fa0c3b9
  sarif_receipt: 0
---
<!-- ai-generated: 50% - szkic i analiza CVE przygotowane z Claude na podstawie logów Trivy z mojego CI, decyzje i weryfikacja moje -->
# Triage

What the gates and the reporting scanners found on my service, and what I did about each (CI-SPEC.md P-11, P-12).
One row per rule of one tool; a row may cover several locations, and the Reason says which. Tool is the tool id of
P-15 (`trivy`, `grype`, `osv-scanner`, `gitleaks`, `semgrep`). Decision is one of `fix`, `ignore`,
`false-positive`, `accept`.

| Tool | Rule | Decision | Reason |
|---|---|---|---|
| trivy | CVE-2024-47874 | fix | starlette podbite do 1.10.0 razem z fastapi 0.163.1 w src/requirements.txt |
| trivy | CVE-2026-48818 | fix | starlette podbite do 1.10.0 razem z fastapi 0.163.1 w src/requirements.txt |
| trivy | CVE-2026-54283 | fix | starlette podbite do 1.10.0 razem z fastapi 0.163.1 w src/requirements.txt |
| trivy | CVE-2026-85091 | fix | zlib1g zaktualizowany w Dockerfile przez apt-get install --only-upgrade |
| trivy | CVE-2026-76844 | fix | zlib1g zaktualizowany w Dockerfile przez apt-get install --only-upgrade |
| trivy | CVE-2026-97687 | fix | wbudowany urllib3 z pip usunięty: pip uninstall po instalacji zależności w Dockerfile |
| trivy | CVE-2026-97689 | fix | wbudowany urllib3 z pip usunięty: pip uninstall po instalacji zależności w Dockerfile |
| trivy | CVE-2026-114613 | fix | wbudowany msgpack z pip usunięty: pip uninstall po instalacji zależności w Dockerfile |
| trivy | CVE-2025-47273 | fix | wbudowany setuptools z pip usunięty: pip uninstall po instalacji zależności w Dockerfile |

## Bake-off

TODO
