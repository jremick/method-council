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
| `sep-carnap-methodology` | Stanford Encyclopedia of Philosophy, *Rudolf Carnap: Methodology — Explication* | Clarifying an inexact concept and evaluating a purpose-fit explicatum | [SEP entry](https://plato.stanford.edu/entries/carnap/methodology.html), accessed 2026-08-20. Expert reference synthesis, not a primary-text edition or certification of this adaptation. |
| `sep-analysis-conceptual-engineering` | Stanford Encyclopedia of Philosophy, *Analysis: Conceptions of Analysis in Analytic Philosophy — Conceptual Engineering* | Evaluating and improving concepts while exposing the value choices in revision | [SEP entry](https://plato.stanford.edu/entries/analysis/s6.html), accessed 2026-08-20. Used to bound revisionary risks rather than claim one correct analysis. |
| `sep-hermeneutics-2025` | Stanford Encyclopedia of Philosophy, *Hermeneutics* | Interpretation through parts and whole, presuppositions, context, history, and plural readings | [SEP entry](https://plato.stanford.edu/entries/hermeneutics/), accessed 2026-08-20. Hermeneutics contains diverse and contested traditions; the project does not present one standard algorithm. |
| `sep-reflective-equilibrium-2023` | Stanford Encyclopedia of Philosophy, *Reflective Equilibrium* | Mutual adjustment of considered judgments, principles, arguments, and background theories | [SEP entry](https://plato.stanford.edu/entries/reflective-equilibrium/), accessed 2026-08-20. Coherence does not establish moral truth, legitimacy, or consent. |
| `sep-pragmatism-2024` | Stanford Encyclopedia of Philosophy, *Pragmatism* | Clarifying a concept through conceivable practical consequences and inquiry contexts | [SEP entry](https://plato.stanford.edu/entries/pragmatism/), accessed 2026-08-20. The project does not reduce truth or all meaning to immediate usefulness. |
| `vsd-lab-methodology` | Value Sensitive Design Lab, *About Value Sensitive Design* | Iterative conceptual, empirical, and technical investigation of stakeholders and values | [VSD Lab overview](https://vsdesign.org/vsd/), accessed 2026-08-20. The project adaptation cannot substitute generated stakeholder views for empirical participation. |
| `braun-clarke-reflexive-ta` | Braun and Clarke, *Doing Reflexive TA* | Recursive familiarisation, coding, theme development, review, definition, and reporting with researcher reflexivity | [Author-maintained guidance](https://www.thematicanalysis.net/doing-reflexive-ta/), accessed 2026-08-20. The model can assist with candidate codes and themes but cannot make an interpretation objective or replace an accountable researcher. |
| `braun-clarke-quality-ta` | Braun and Clarke, *Quality in TA* | Methodological coherence, reflexive practice, and warnings against themes-as-emergent-facts or reliability-as-quality | [Author-maintained guidance](https://www.thematicanalysis.net/quality-in-ta/), accessed 2026-08-20. The project does not reproduce training content or claim full method fidelity. |
| `sep-speech-acts-2023` | Stanford Encyclopedia of Philosophy, *Speech Acts* | Language as action; communicative force, context, conditions, commitments, uptake, and effects | [Archived SEP entry](https://plato.stanford.edu/archives/sum2023/entries/speech-acts/index.html), accessed 2026-08-20. Speech-act theory contains contested classifications and does not reveal private speaker intent. |
| `justice-canada-oakes` | Department of Justice Canada, *Charterpedia — Section 1, Reasonable Limits* | Important objective, rational connection, minimal impairment, final balancing, and evidence needs | [Official guidance](https://www.justice.gc.ca/eng/csj-sjc/rfc-dlc/ccrf-ccdl/check/art1.html), accessed 2026-08-20. The catalogue generalises the questions and does not provide Canadian or other legal advice. |
| `sep-capability-approach-2025` | Stanford Encyclopedia of Philosophy, *The Capability Approach* | Substantive opportunities and functionings, means and ends, conversion factors, agency, diversity, and distribution | [SEP entry](https://plato.stanford.edu/entries/capability-approach/), accessed 2026-08-20. The framework does not supply one universal capability list or complete theory of justice. |
| `uk-magenta-book-toc` | HM Treasury and Evaluation Task Force, *Magenta Book* | Inputs, activities, causal mechanisms, outputs, outcomes, impacts, evidence, assumptions, context, and stakeholder involvement | [Official HTML guidance](https://www.gov.uk/government/publications/the-magenta-book/magenta-book-central-government-guidance-on-evaluation-html), accessed 2026-08-20. A Theory of Change is not causal proof. |
| `uk-analysis-function-toc-toolkit` | UK Government Analysis Function, *The Theory of Change Process* | Problem, impacts, outcomes, outputs, inputs, assumptions, risks, indicators, stakeholder participation, quality assurance, and iteration | [Official toolkit](https://analysisfunction.civilservice.gov.uk/policy-store/the-analysis-function-theory-of-change-toolkit/), accessed 2026-08-20. The project does not claim government evaluation compliance. |
| `usdoi-adaptive-management-policy` | U.S. Department of the Interior, *522 DM 1 — Adaptive Management Implementation Policy* | Adjustable decisions under uncertainty through monitored outcomes and iterative learning | [Official PDF](https://www.doi.gov/sites/default/files/elips/documents/522-dm-1_0.pdf), accessed 2026-08-20. The cross-domain project record does not claim department or resource-management compliance. |
| `usdoi-adaptive-management-guide` | U.S. Department of the Interior, *Adaptive Management Technical Guide* | Objectives, alternatives, models, monitoring, assessment, learning, adjustment, stakeholders, and institutional commitment | [Official PDF](https://www.doi.gov/sites/doi.gov/files/uploads/TechGuide-WebOptimized-2.pdf), accessed 2026-08-20. A plan or dashboard is not evidence of a completed learning cycle. |
| `iso-9241-210-2019` | International Organization for Standardization, *ISO 9241-210:2019* | Public high-level lifecycle scope for human-centred design principles and activities for interactive systems | [ISO abstract and metadata](https://www.iso.org/standard/77520.html), accessed 2026-08-20. The full standard is not reproduced and the project makes no conformance claim. |
| `govuk-understand-user-needs` | UK Government Digital Service, *Understand users and their needs* | Actual user research, whole-context understanding, hypothesis testing, prototypes, and iteration | [GOV.UK Service Manual](https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs), accessed 2026-08-20. Public service guidance is adapted without claiming GDS assessment or compliance. |
| `govuk-user-needs-research` | UK Government Digital Service, *Learning about users and their needs* | Continuous research, actual-user interviews and observation, service evidence, diverse users, and assumption handling | [GOV.UK Service Manual](https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs), accessed 2026-08-20. Generated personas and non-user opinions remain assumptions. |
| `rand-delphi-guidance-2024` | RAND Corporation, *Methodological Guidance for Conducting and Critically Appraising Delphi Panels* | Real expert-panel design, anonymity, iteration, feedback, statistical summary, consensus rules, attrition, and reporting | [Public PDF](https://www.rand.org/content/dam/rand/pubs/tools/TLA3000/TLA3082-1/RAND_TLA3082-1.pdf), accessed 2026-08-20. Model agents are not counted as expert participants and the project does not reproduce appraisal tools. |

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
| `concept-clarification` | SEP Carnap methodology; SEP conceptual engineering | Bounded explication and concept-revision record; not a claim of one correct ordinary meaning. |
| `contextual-interpretation` | SEP hermeneutics | Source-bound comparison of interpretations through text, context, presuppositions, and reception; not one mechanical hermeneutic algorithm. |
| `reflective-equilibrium` | SEP reflective equilibrium | Bounded record of judgments, principles, revisions, and tensions; coherence is not moral truth or legitimacy. |
| `pragmatic-clarification` | SEP pragmatism | Practical-consequence clarification across goals and contexts; usefulness is not treated as truth. |
| `value-sensitive-inquiry` | Value Sensitive Design Lab overview | Conceptual, empirical, and technical inquiry into stakeholders and values; generated personas are not participation. |
| `reflexive-thematic-analysis` | Braun and Clarke reflexive TA and quality guidance | Recursive source-bound qualitative interpretation; generated themes are analyst-mediated interpretations, not objective discoveries or prevalence estimates. |
| `speech-act-analysis` | SEP speech acts | Contextual analysis of communicative force, conditions, commitments, uptake, and effects; no private-intention or legal-validity claim. |
| `rights-proportionality-review` | Department of Justice Canada Charterpedia | Generalised proportionality questions for rights-limiting decisions; not jurisdiction-specific legal advice or adjudication. |
| `capability-distribution-review` | SEP capability approach | Bounded comparison of means, substantive opportunities, conversion factors, functionings, agency, and distribution; not a complete theory of justice. |
| `theory-of-change` | UK Magenta Book; Government Analysis Function toolkit | Testable intervention pathway with mechanisms, assumptions, evidence, context, alternatives, and indicators; map coherence is not causal proof. |
| `adaptive-management` | U.S. Department of the Interior policy and technical guide | Governed decision-learning cycle with explicit uncertainty, monitoring, review rules, and adjustment; planning alone is not completed adaptation. |
| `human-centred-design-inquiry` | ISO public abstract; GOV.UK Service Manual | Actual-user evidence connected to context, needs, requirements, prototypes, and iteration; no ISO, usability, or accessibility conformance claim. |
| `structured-expert-elicitation` | RAND Delphi methodological guidance | Real-expert, multi-round, controlled-feedback elicitation with dissent and attrition preserved; model agents are not a panel. |

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
