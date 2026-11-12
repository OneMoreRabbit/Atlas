<!-- atlas:<role>-seat (written by atlas_init; it replaces what is between these two markers) -->
## Atlas <role> seat

Write scope: <scope>

A briefing that starts `<briefing>` should be in your context from session start.

If it is there, the Atlas hooks are live and nothing more is needed here.

If it is not there, the Atlas hooks did not run. Then:

1. Run `sh "<context>"` and read what it prints. Run it again after your context is compacted.
2. Keep the write scope above by hand. No guard is checking it.
3. Before you finish each turn, run `sh "<gate>" </dev/null`. If it exits 2, do what it prints first.
4. Tell the operator that the Atlas hooks are not live at <launch dir>.
<!-- /atlas:<role>-seat -->
