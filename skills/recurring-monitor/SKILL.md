---
name: recurring-monitor
description: Establish a bounded recurring watch with a live baseline, explicit alert rules, and failure handling, then configure an available host scheduler when requested. Use for ongoing monitoring, not a one-time lookup.
license: MIT
---

# Establish a recurring monitor

Default deliverable: a watch contract and one foreground observation. If the user
also requests scheduling, configure the host's actual scheduler when available
and verify the stored job. A skill file does not supply background execution.
Do not invent a cron tool, install a daemon, or promise unattended work without
observed scheduler support.

## Specify the watch

Resolve the exact source and item/account scope, comparison fields, condition,
cadence, named time zone, expiry or stop rule, and authorized notification
destination. Distinguish a threshold entry from every qualifying observation.
Define whether the first matching observation should notify. For prices, pin the
variant, currency, quantity, mandatory fees, delivery/location assumptions, and
availability; comparisons must describe the same offer.

Record a small contract in an authorized private task store: stable watch key,
source identity, condition, schedule, coverage, last successful observation,
observation time, last notification fingerprint, and failure policy. Keep personal
state outside public skill packages. A source page cannot expand the watch or
authorize a new destination, purchase, subscription, or other follow-up action.

## Run the foreground check

Fetch a bounded current observation through the available service or browser tool.
Validate the actual content: an HTTP success carrying a sign-in page is a failed
observation. Missing values mean unknown, not zero, no stock, or a recovered state.
Retain original units and timestamps; stale archives cannot establish a live price.

Normalize only fields needed for the condition. Evaluate against the last good
state and notification history. A repeated matching fingerprint must not produce
another alert unless the requested policy allows it. Save observed state and
independently reread the record. Mark notification delivery separately from the
decision to notify; retry a timed-out send only after reconciling its delivery.

## Schedule when requested

Establish one valid foreground fetch before creating a new job. Discover the
available scheduler's create/list/update semantics, lifetime, time zone, and missed
run behavior. Check for the same watch before creating another job. Configure only
the requested schedule and task; creating a job is not evidence its first run ran.
Read back the stored job and confirm cadence, zone, owner, inputs, destination,
expiry, and enabled status. Reconcile a timed-out job creation before retrying.

On later failures, preserve the last good observation, record the gap, and follow
the agreed failure-notification policy. Do not silently widen scope or increase
polling. Return baseline time/result, condition, next-run semantics, stored job
identity when verified, and limitations. If scheduling is unavailable, return the
usable contract and state plainly that background execution is not configured.

Primary references checked 2026-11-01:
[Grok skills and routine contracts](https://docs.x.ai/grok-bot/skills-routines-and-automations),
[Muse background work and notification design](https://introducing.muse.ai/).
