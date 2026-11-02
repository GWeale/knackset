# Validation and provenance

Status: **offline-reviewed**. Scope: the synthetic `capture-tentative-lesson-and-counterexample` case only.
The [dated execution record](https://github.com/GWeale/knackset/blob/main/evals/results/refactor-retests-20261101.json)
records actual actions, saved-state checks, separate semantic response review,
and the versioned package fingerprint. Match that fingerprint before applying
this status to a modified copy. Earlier records remain historical at their original fingerprints. The refactor
retest covers this named case only; new authored boundary cases are not implied
to have passed by this record.

No live service or browser compatibility, broader branch coverage, implicit
routing accuracy, or performance improvement follows from this scoped test.
Automated checks cover typed facts and operation order; prose meaning requires
the recorded manual review. Other [authored cases](evals/evals.json) remain outside
this execution claim.

Independently written by Knackset contributors; basis: `session-derived`, `authored`. No proprietary
product prompts or upstream skill files were copied. The [MIT license](LICENSE.txt)
covers this package; linked external sources retain their own terms.
[Provenance at the audit baseline](https://github.com/GWeale/knackset/blob/d54f5a7ddf4a80ea23ba31e1f386af4d887b354c/docs/provenance.md)
describes the bounded, sanitized session lessons and public research.

Validation notes are part of the package. Update this note and rerun the relevant
evaluation when changing the workflow; an old successful run does not validate
new package contents.
