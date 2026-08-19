# Architecture task: local run history

Design the storage approach for a local-first CLI that keeps Method Council run
metadata. Compare append-only JSONL with SQLite and recommend one initial
architecture.

Constraints and observations:

- A run may produce 4–8 structured JSON artifacts totalling under 1 MB.
- The CLI must support exact lookup by run ID and list the latest 100 runs.
- Two CLI processes may finish at nearly the same time.
- Raw prompts and secrets must not be stored.
- Users should be able to inspect or export their own data without a server.
- Schema evolution is expected during alpha.
- The first release targets macOS and Linux with Python 3.12.

Decision boundary: choose the alpha storage architecture and name the trigger
that would justify migrating to the other option. Do not implement it.
