# Method source register

Version: 0.1.0
Access baseline: 2026-08-20

This register records the public source basis for Method Council's preview catalog. A source entry
supports only the claims identified below. Inclusion does not claim affiliation, endorsement,
certification, comprehensive training equivalence, or compliance with the publisher's internal
processes.

The canonical claim details live in each `methods/<id>/method.yaml`. The adjacent `METHOD.md` is a
concise human guide. Where either conflicts with a schema-validated YAML record, the YAML record is
the method definition.

## Provenance-class semantics

The catalog's provenance class describes the project record's relationship to
its cited public sources. It is not an authority rank, publisher designation,
fidelity score, certification, or quality threshold.

- `established-primary-method` means a primary public source names and describes
  the approach and the project record retains a recognisable outline. The YAML
  wording, result contract, evidence rules, and rigor variants are still project
  adaptations and remain preview material.
- `project-adaptation` means the record combines sources or makes substantial
  domain-neutral, model-mediated, or control-oriented changes.
- Other schema classes are available for future records but do not confer
  validation merely by being selected.

These classifications are project judgments and have not received independent
method-fidelity review. A method can cite an authoritative publisher while the
project implementation remains unvalidated.

## Source register

| Source ID | Publisher and work | Supports in this catalog | Source and access notes |
|---|---|---|---|
| `cia-tradecraft-primer-2009` | CIA Center for the Study of Intelligence, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis* (2009) | Public descriptions, use conditions, and procedure shapes for Quality of Information Check, Key Assumptions Check, Indicators or Signposts of Change, Analysis of Competing Hypotheses, Devil's Advocacy, Alternative Futures Analysis, and Outside-In Thinking | [Public PDF](https://www.cia.gov/resources/csi/static/955180a45afe3f5013772c313b16face/Tradecraft-Primer-apr09.pdf), accessed 2026-08-20. Method Council paraphrases and adapts; it does not reproduce extended text, examples, or figures. |
| `cia-ask-molly-sats-2024` | Central Intelligence Agency, *Ask Molly: SATs Advice* | Current public-level descriptions of Key Assumptions Check, Devil's Advocacy, and Signposts and Indicators | [CIA webpage](https://www.cia.gov/stories/story/ask-molly-sats-advice/), accessed 2026-08-19. This is outreach material, not a full method specification. |
| `odni-icd-203-2022` | Office of the Director of National Intelligence, *ICD 203: Analytic Standards*, current public PDF incorporating the 2022 technical amendment | Quality anchors for describing sources and methodologies, explaining uncertainty, and distinguishing information, assumptions, and judgments | [Official PDF](https://www.odni.gov/files/documents/ICD/ICD-203.pdf), accessed 2026-08-19. Used as an anchor only; the project does not claim ICD 203 conformance. |
| `nasa-se-decision-analysis-2023` | NASA, *Systems Engineering Handbook, Section 6.8: Decision Analysis* | Decision framing, criteria, alternatives, evaluation, uncertainty and sensitivity, recommendation, and report content | [NASA reference page](https://www.nasa.gov/reference/6-8-decision-analysis/), accessed 2026-08-19. The portable trade-study method is a project adaptation, not a NASA process implementation. |
| `nasa-se-handbook-rev2-2017` | NASA, *NASA Systems Engineering Handbook, NASA/SP-2016-6105 Rev 2* | Broader systems-engineering context for decision analysis and trade studies | [NASA Technical Reports Server PDF](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20170001761.pdf), accessed 2026-08-19. The NTRS record states public use is permitted. |
| `nasa-gsfc-hdbk-8004-2024` | NASA GSFC, *Guideline for Failure Modes and Effects Analysis and Risk Assessment*, GSFC-HDBK-8004 | Public FMECA scope as a living development risk assessment | [NASA Technical Standards System record](https://standards.nasa.gov/node/12367), accessed 2026-08-19. NASA marks the document active and public, but not mandatory, not a core standard, and not NASA-endorsed. No source tables or scoring scales are reproduced. |
| `nasa-sw-fmea-2023` | NASA, *Software Engineering Handbook 8.05: Software Failure Modes and Effects Analysis* | Bottom-up software FMEA orientation, a public procedure outline, preliminary-use boundary, and limitations | [NASA Software Engineering Handbook](https://swehb.nasa.gov/spaces/SWEHBVC/pages/72024562/8.05%2B-%2BSW%2BFailure%2BModes%2Band%2BEffects%2BAnalysis), accessed 2026-08-19. Introductory guidance cannot replace domain expertise. |
| `nasa-swe-204-process-assessments` | NASA Software Engineering Handbook, *SWE-204: Process Assessments* | Closed-loop root cause analysis using event definition, evidence, timelines, causal factors, corrective actions, and effectiveness checks | [NASA Software Engineering Handbook](https://swehb.nasa.gov/spaces/SWEHBVD/pages/102695538/SWE-204%2B-%2BProcess%2BAssessments), accessed 2026-08-20. The project generalises the public guidance and does not claim NASA process compliance. |
| `homes-england-reference-class-forecasting-2024` | Homes England, *Optimism Bias and Contingency at Homes England* | Taking an outside view from completed comparable projects, establishing an outcome distribution, and adjusting an estimate | [GOV.UK accessible publication](https://www.gov.uk/government/publications/optimism-bias-and-contingency-at-homes-england/optimism-bias-and-contingency-at-homes-england-accessible-version), accessed 2026-08-20. The project does not reuse the workbook, figures, tables, or example values. |

## Method-to-source map

| Method | Source basis | Catalog claim |
|---|---|---|
| `evidence-quality` | CIA primer; ICD 203 | Project adaptation of public Quality of Information Check with evidence-ledger, correlation, retrieval, and claim-fidelity controls. |
| `key-assumptions` | CIA primer; Ask Molly | Project adaptation of the public outline with typed findings, evidence links, and change conditions. |
| `competing-hypotheses` | CIA primer | ACH-inspired project adaptation. It remains preview because formal ACH fidelity, corpus adequacy, and hypothesis completeness have not been independently assessed. |
| `alternative-futures` | CIA primer | Public two-axis scenario workflow adapted for typed assumptions, robustness implications, and checkpoints. Scenarios are not forecasts. |
| `indicators-signposts` | CIA primer; Ask Molly | Project adaptation of the public monitoring outline, adding observability, correlation checks, ownership, and unavailable-data treatment. |
| `devils-advocacy` | CIA primer; Ask Molly | Project adaptation of the public contrarian outline, adding a steelmanned case, evidence bindings, correlation labels, and a post-challenge disposition. |
| `systems-trade-study` | NASA decision-analysis page; NASA SE handbook | Portable project adaptation. It does not prescribe NASA programme process or one scoring algorithm. |
| `failure-modes` | GSFC-HDBK-8004 record; NASA software FMEA guidance | Preliminary cross-domain failure review only; not a validated FMEA/FMECA, safety case, or compliance artifact. |
| `causal-factors` | NASA SWE-204 process-assessment guidance | Domain-neutral causal-factors record for bounded retrospective investigations; not a regulated safety or mishap investigation. |
| `outside-view` | Homes England reference-class forecasting guidance | Bounded outside-view check; not a calibrated forecast without a reliable comparison class and suitable outcome data. |
| `outside-in` | CIA primer | Domain-neutral adaptation of Outside-In Thinking with evidence, materiality, and control/influence boundaries. |

## Catalog-wide claim limits

- All current methods and profiles are `preview`. Passing schema validation does not establish
  method fidelity, domain adequacy, user comprehension, or decision quality.
- Method names identify public approaches or project adaptations. They do not create a simulated
  member, institutional voice, government affiliation, or claim of privileged access.
- Model outputs remain untrusted. A result cannot count as a completed method pass unless it
  validates against the canonical contracts and required steps and evidence are present.
- Same-model and same-host passes are correlated. Method diversity is not model, provider, or
  source independence.
- No method requests hidden chain-of-thought. Only bounded artifacts, findings, evidence links,
  assumptions, unknowns, alternatives, dissent, and change conditions are retained.
- Public institutional sources can still be incomplete, dated, domain-specific, or unsuitable for
  a particular decision. Users must review source fit and currency.
- Catalog rigor variants, method-count bands, step selections, and numeric evidence minima are
  project-defined, unvalidated safeguards. They are not publisher procedures, calibrated quality
  thresholds, confidence scores, or evidence that an output is sufficiently rigorous for a domain.

## Licensing and reuse caution

Method Council's original descriptions and code are licensed under the repository license. Source
documents retain their own legal status and publisher terms. The project paraphrases small public
method descriptions and links to source material; it intentionally does not copy source tables,
figures, long passages, training packages, or proprietary scoring systems.

Before promoting a method from `preview`, an independent reviewer should check procedure fidelity,
scope, terminology, source currency, and any reuse obligations. Standards whose full text is
paywalled or proprietary may be cited for context but must not be reconstructed from secondary
summaries.
