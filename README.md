<p align="center">
  <img src="assets/exported/method-datum-mark.svg" width="104" height="104" alt="Method Council datum mark: three separate method paths converge at a shared review point">
</p>

<h1 align="center">Method Council</h1>

<p align="center">
  <strong>Structured methods. Separate analysis passes. One traceable report.</strong>
  <br>
  A provider-neutral methodology protocol with a Codex-subscription-first path.
</p>

> **Private build — not yet public alpha.** The contracts and first implementation
> are being assembled locally. Installation, the `$method-council` invocation,
> provider compatibility, and release eligibility have not yet been validated as
> an end-to-end user journey.

## What this is

Method Council applies documented analytical methods to a question in separate,
inspectable passes. It then preserves their evidence, assumptions, unknowns, and
disagreements in a report that a human can review.

The members are methods, not simulated people. A route might combine a key
assumptions check, evidence-quality assessment, and analysis of competing
hypotheses because those procedures contribute different checks—not because
fictional experts were assigned different personalities.

The intended first host is Codex used through an existing ChatGPT subscription.
The canonical method and report contracts remain host-neutral so other model
providers can be added later as separately tested adapters.

![Method Council workflow: scope, select, separate passes, challenge, synthesize, and checkpoint](assets/exported/method-council-workflow.svg)

## Why methods instead of personas

- **Inspect the procedure.** Each method records its source basis, adaptation,
  applicability, steps, failure modes, rigor variants, and claim limits.
- **Keep disagreement useful.** Synthesis reports convergence, divergence, and
  the evidence that could resolve a split. It does not manufacture consensus.
- **Separate kinds of diversity.** Method, model, provider, and source diversity
  are different claims. Same-model passes are labelled correlated.
- **Fail visibly.** Invalid, missing, failed, or simulated output cannot count as
  a successful method pass.
- **Keep hard gates in code.** Deterministic validation owns route limits,
  schemas, evidence binding, status precedence, and release eligibility.

## Intended Codex journey

The planned first interaction is deliberately small:

```text
$method-council <activity> --rigor <rapid|standard|intensive> "question"
```

This is a product preview, not a verified command. The intended sequence is:

1. Scope the question, decision owner, constraints, and evidence boundary.
2. Propose a complementary set of methods for the activity and rigor level.
3. Validate that route before any method pass starts.
4. Run method passes separately, using bounded Codex subagents where available.
5. Validate each structured artifact and retain failure or correlation states.
6. Challenge the emerging answer, synthesize without voting, and stop at a
   human checkpoint.

Codex subscription use should not require a separate provider API key. External
provider calls, persistence of raw prompts, and tool side effects are intended
to remain off by default. See the [Codex workflow preview](docs/CODEX_WORKFLOW.md)
and [architecture](docs/ARCHITECTURE.md).

## Report contract

The report leads with the decision-relevant result and preserves the reasoning
artifacts needed to inspect it:

1. Result, next action, and checkpoint.
2. Key judgments linked to evidence and calibrated confidence language.
3. Alternatives, dissent, and counterevidence.
4. Assumptions, unknowns, and collection gaps.
5. Indicators, signposts, or kill criteria when the activity requires them.
6. Method, provider, correlation, validation, and limitation ledger.

Findings are typed as `fact`, `inference`, `assumption`, or `unknown`. Weighted
votes are not part of the contract. Schema-valid output is necessary but does
not prove that a method was applied faithfully or that a conclusion is sound.

![Traceable report anatomy showing result, judgments and evidence, alternatives and dissent, assumptions and unknowns, indicators, and the run ledger](assets/exported/report-cutaway.svg)

Read the [report anatomy](docs/REPORT_ANATOMY.md) and
[canonical contracts](docs/CONTRACTS.md) for the detailed boundary.

## Current status

This repository is at **Stage 0 — Private Build**. The target for the next gate
is a pre-public candidate that a new reader can inspect without confusion or
private-state leakage.

Current foundations include:

- host-neutral schemas and architecture decisions;
- initial source-backed method records;
- a deterministic Python core under active development;
- a Codex skill surface under active development;
- Apache-2.0 licensing and clean-room notices;
- original code-native diagrams and visual system.

Not yet established:

- a tested clean-clone install and first-run journey;
- real Codex task-run evidence;
- independent method-fidelity, security, and usability review;
- validated compatibility with any non-Codex provider;
- public-alpha release eligibility;
- a GitHub remote, release, support channel, or public vulnerability channel.

No remote repository or public release is implied by this local source tree.

## Local development

The repository targets Python 3.12 and `uv`. These are the canonical development
checks; their presence here does not claim that the current integration passes
all of them yet.

```bash
uv sync --all-groups
uv run method-council validate
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

A user-facing installation path will be documented only after it succeeds from
a clean checkout without relying on maintainer-local state.

## Documentation

- [Delivery brief](docs/DELIVERY_BRIEF.md) — value, risk tier, gates, and non-goals
- [Architecture](docs/ARCHITECTURE.md) — components, data flow, and trust boundaries
- [Canonical contracts](docs/CONTRACTS.md) — status, rigor, findings, and evidence
- [Codex workflow preview](docs/CODEX_WORKFLOW.md) — intended subscription-first journey
- [Report anatomy](docs/REPORT_ANATOMY.md) — human-facing report structure
- [Design system](docs/DESIGN_SYSTEM.md) — visual language and asset rules
- [Source register](docs/SOURCES.md) — method provenance and claim boundaries
- [Threat model](docs/THREAT_MODEL.md) — security assumptions and abuse cases
- [GitHub settings plan](docs/GITHUB_SETTINGS.md) — pre-public and public-alpha posture
- [Architecture decisions](docs/decisions/) — accepted design choices

Some linked documents are being produced in parallel and may not yet exist in a
partial checkout. The pre-public link check must pass before publication.

## Contributing and support

There is no public issue tracker or monitored support channel while this remains
a local private build. The contribution policy describes the standards that will
apply when external contributions are opened; it does not imply that submissions
are currently accepted. See [CONTRIBUTING.md](CONTRIBUTING.md).

For security, do not publish suspected vulnerabilities in a future public issue.
The project plans to use GitHub private vulnerability reporting after a remote
exists and the feature is enabled and read back. There is currently no active
public reporting channel. See [SECURITY.md](SECURITY.md).

## License and attribution

Code and repository documentation are licensed under the
[Apache License 2.0](LICENSE). Method sources and conceptual inspiration are
recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the
[source register](docs/SOURCES.md). Citations identify provenance; they do not
imply endorsement by the cited institutions.
