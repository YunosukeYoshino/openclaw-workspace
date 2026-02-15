# HEARTBEAT — ops/coach only

## Hard rules
- If nothing actionable: output exactly `HEARTBEAT_OK`.
- Do not execute tasks. Do not change configs. Propose only.
- At most ONE improvements entry per heartbeat.

## Process
1) Review latest actions + handshake notes (if any).
2) Detect repeated friction: same error twice, missing prerequisite,
   unclear prompt, risky step, excessive verbosity.
3) If found: append ONE entry to memory/improvements.md using the template.
4) If requires config/tool install: status must be `proposed`
   and include rollback.

## Output
- If logged: `HEARTBEAT: logged 1 improvement`
- Else: `HEARTBEAT_OK`
