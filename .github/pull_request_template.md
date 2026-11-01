## Behavior

Describe the concrete request and resulting behavior. Explain the existing-skill
gap when adding a package rather than extending one.

## Evidence

- Source/provenance and applicable license:
- Success, boundary, and neighboring-task cases:
- Actual executions or artifacts, with revision and limitations:

## Checks

- [ ] `python3 scripts/validate.py`
- [ ] `python3 scripts/catalog.py render --check`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] No private histories, account data, credentials, or unlicensed upstream files
- [ ] Package license included; catalog status matches execution evidence

State unavailable checks explicitly. A new scenario is not a completed execution.
