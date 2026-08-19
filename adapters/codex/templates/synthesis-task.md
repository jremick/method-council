<!--
Adapter source template: codex/synthesis-task
Generator: method-council-adapter-compiler 0.1.0
Generated artifacts must record the canonical input digest and generator version.
-->

# Traceable synthesis

Synthesize run `{{run_id}}` from checked artifacts only. The deterministic
aggregation is authoritative for primary status, side conditions, and ledger.

<question>
{{question}}
</question>

<deterministic-aggregation>
{{aggregation}}
</deterministic-aggregation>

<checked-method-results>
{{checked_method_results}}
</checked-method-results>

Return one `report.schema.json` object at `{{output_path}}`. Lead with the useful
judgment, decision boundary, and next action. Retain the strongest alternative,
assumptions, unknowns, dissent, checkpoint indicators, routing limitations, and
all non-passing conditions. Bind judgments only to existing finding IDs. Do not
change derived status, invent evidence, force consensus, or expose hidden
chain-of-thought. The report is provisional until `method-council verify-run
{{run_dir}}` validates exact method coverage, content digests, ledger parity,
derived status, and correlation labelling.
