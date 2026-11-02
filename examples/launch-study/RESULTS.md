# What the three pairs showed

All six outputs were judged usable for local review, with no critical errors.
Both variants received 8/8 on the four common dimensions in every case. Small
qualitative preferences remained under the case-specific criteria:

| Task | Anonymous review after revealing labels | Difference that mattered |
| --- | --- | --- |
| Rabbit Hole | Slight preference for with-skill | More explicit testing of rival explanations for the evidence mismatch. |
| Reference Remix | Tie | Both original cards met the brief. A choice between their compositions needs taste or placement context. |
| Unstick Project | Slight preference for baseline | One offline entrypoint and a complete new reference exercise reduced review friction. |

This pilot did **not** show a consistent advantage from loading a skill. Common
scores reached their ceiling, so those scores did not distinguish the variants.
The small preferences identify concrete differences, not a win-rate benchmark
or evidence of general efficacy. We kept the methods draft and did not append
new universal instructions based on one usable alternative.

The practical lesson is to make a demo's first entrypoint complete and usable.
The preview links both original packets, and its own captioned deck presents both
launch cards rather than hiding the unassisted result.

[Readable frozen review](review.md) · [Original judge JSON](judgment.json) ·
[Original review text](judgment-original.md.txt) · [Variant key and hashes](unblinding.json).

## Limits that affect the decision

There is one pair per distinct task, on one project's actual launch work, with
one producer model and one model judge. No human taste, audience usefulness,
agent-host activation or live-service reliability was tested. Billing cost,
complete token usage and comparable execution timing are unknown. Baselines
were instructed not to read package bodies; shared-filesystem isolation was not
enforced. The judge noted process metadata in one Unstick packet as a possible
chronology clue and reported no arm inference.

The record supports selecting usable examples and planning better trials.
A broader claim needs repeated, varied tasks and independent user reports.
[Execution setup and deviations](README.md).
