# Forecast task: provider plugin ecosystem

Assess whether Method Council should freeze and publicly support a third-party
provider-plugin API in its next release or keep the adapter boundary internal
for the next 12 months. Explore materially different futures over an 18-month
horizon and define observable indicators that would trigger reassessment.

Current observations:

- Forty synthetic pilot workflows cover six recurring analysis activities.
- Three provider CLIs are evolving independently; their authentication and
  non-interactive execution contracts have changed during the last year.
- Two prospective contributors asked for custom-adapter documentation, but no
  external adapter has been implemented or maintained.
- The internal preview interface already separates probe, render, launch,
  collect, timeout/retry, model observation, cancellation, and error
  normalization.
- Only the Codex path has live functional evidence. Claude and Gemini launch and
  collection remain disabled and unverified.
- A public plugin API would create a compatibility and security-support promise.
  The project currently has no public support channel or remote settings
  read-back.
- Waiting increases the chance of internal interface churn but preserves the
  ability to learn from the first two provider integrations.

Current working strategy: keep the interface internal until at least two
provider adapters complete authenticated critical-path runs and the project has
an accountable compatibility policy.

Decision boundary: do not make the final product decision. Produce plausible
futures, cross-scenario implications, observable and discriminating indicators,
collection ownership/cadence, and an explicit review checkpoint. Do not assign
unsupported probabilities, treat scenario counts as evidence, or claim that
the listed futures are exhaustive.
