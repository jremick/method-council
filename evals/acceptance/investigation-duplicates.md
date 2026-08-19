# Investigation task: duplicate run summaries

A local CLI occasionally shows the same run twice in `list --latest`, but direct
lookup by run ID returns one record. Identify the leading hypotheses and the
next discriminating diagnostic.

Observed evidence:

- The defect appeared after concurrent acceptance runs were enabled.
- Each worker writes a temporary summary file, renames it into a shared
  directory, then appends one line to `index.jsonl`.
- Duplicate list entries have the same run ID and identical summary digest.
- The artifact directory contains only one final summary for the affected run.
- Logs show two successful append messages within 12 milliseconds for one
  affected run.
- No corrupted or partial JSON line has been observed.

Unknowns:

- Whether the append helper is invoked once per worker or retried by a caller.
- Whether advisory file locking is enabled on every supported platform.
- Whether the list command performs any cache merge.

Decision boundary: select the first diagnostic or instrumentation change, not a
permanent fix. Preserve plausible alternatives.
