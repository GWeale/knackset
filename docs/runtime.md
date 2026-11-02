# Local workflow runner MVP

Authored 2026-11-01. This is a bounded, standard-library implementation of local
synthetic execution, separate from the portable skill packages. It has no model,
service account, browser, shell adapter, background daemon, or notification sender.
It does not establish live service validation or promote catalog entries.

The supported interface is `python3 scripts/run_workflow.py --db PATH COMMAND`.
Keep the database and its adjacent `.lock`, `-wal`, and `-shm` files together on a
local filesystem. Use synthetic, non-sensitive payloads: `show` and mutation
commands output the complete saved state. The state is plain SQLite, not encrypted.
Do not delete the lock file while any runner is active.

```sh
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite capabilities
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite add example --payload 'synthetic draft' --due 0 --approval-required --mode timeout-after-write
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite approve example
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite tick
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite tick
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite show
python3 scripts/run_workflow.py --db /tmp/knackset-demo.sqlite ack task:example:verified
```

The first tick leaves an uncertain outcome after a synthetic write. The second
process independently reads the saved effect and verifies it without resubmission.
The local outbox contains exactly one verification notification. `ack` records
local acknowledgement; nothing is delivered to a person or service.

`add` requires a unique immutable task ID, payload and UTC Unix due timestamp.
`--approval-required` holds execution until an explicit `approve ID` command;
this local gate is not a substitute for host authorization or account permissions.
Only the declared `synthetic` adapter is accepted. `capabilities` states its read,
write, reconciliation and idempotency support and scope. There is no dynamic plugin
loading. Each tick handles at most 10 due jobs by default (`--limit 1..100`), selected fairly by least recent execution/reconciliation attempt,
then due time and task ID. `--now` supports deterministic offline checks. An external
scheduler may invoke ticks only within separately authorized scope; this MVP does
not install one. Recurrence, cancellation and task editing are not implemented.

A durable `intent` event and task state precede each effect. An interrupted intent
or uncertain outcome is reconciled on the next tick. A matching independent read
marks `verified`; a conflicting result blocks. Confirmed absence makes a task
eligible for a later tick, with an audit event before any retry. Unavailable reads
leave `uncertain` and never submit again. The synthetic `timeout-before-write`,
`timeout-after-write` and `unreadable` modes exercise these paths. Synthetic effects
have a unique operation key as an additional duplicate guard. Intent and effect
are separate durable transactions in the same local database; a real service
boundary is deliberately not implemented.

The CLI holds an OS advisory lock over each entire command, including separate
intent/effect commits, so cooperating CLI processes cannot overlap writers. A
second runner fails promptly. Linux/local-filesystem semantics are assumed; the
internal Python `Runner` class is not a concurrent public API. Do not access or
mutate its database concurrently through another tool. Failed CLI validation exits
2; operational filesystem/SQLite failures may also exit nonzero. There is no
schema migration framework, retention policy or protection against disk loss.

Verification: `python3 -m unittest discover -s tests -p test_runtime.py -v` exercises
the public CLI across fresh processes, approval/due gates, bounded selection,
ambiguous outcomes, absent-before-retry ordering, unavailable reads, outbox
acknowledgement/deduplication and process exclusion. These are isolated synthetic
regressions, not remote execution or live validation.
