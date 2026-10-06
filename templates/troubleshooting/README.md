# Troubleshooting template (method 1.33.13)

Copy into a vault:

1. Vault level (arch seat): `troubleshooting/troubleshooting-log.md` from
   `troubleshooting-log.md`; create `troubleshooting/reports/`.
2. Component level (component seat, optional, in its own scope):
   `components/<name>/troubleshooting/troubleshooting-log.md`; reports in
   `components/<name>/troubleshooting/reports/`.
3. New incident: add a row to your log. If it took more than one attempt to fix,
   copy `report-template.md` to `reports/<YYYY-MM-DD>-<topic>.md` and fill it.
4. Arch collates: for every component report, one row in the vault log linking it.
   The validator warns when a component report has no vault-log row.
