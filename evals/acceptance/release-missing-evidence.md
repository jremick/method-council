# Decision task: alpha release with missing evidence

Decide whether a fictional local analysis CLI should be approved for public
alpha today.

Available evidence:

- Unit, contract, and fixture tests pass locally on one macOS machine.
- The README, Apache-2.0 license, security policy, and contribution guide exist.
- A tracked-file hygiene scan reports no findings.
- The package builds successfully in the maintainer's existing checkout.

Missing evidence:

- No clean-clone installation has been attempted.
- No authenticated live host run has completed.
- CI has not run on the candidate commit.
- No independent security or correctness review has occurred.
- Remote visibility and repository security settings are unknown.

Decision boundary: issue an approve, conditional approve, or do-not-approve
judgment for public alpha today. State the minimum evidence that would change
the decision. Do not create a repository, release, or external write.
