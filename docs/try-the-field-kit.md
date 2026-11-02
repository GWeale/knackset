# Try the creative field kit

Give one method a real job and tell us what you would keep or change. Allow
20–30 minutes. The current methods are previews; useful criticism matters more
than a favorable score.

## Pick a task with material you can share

- **Rabbit Hole:** a claim, story or question with a few sources that disagree.
  Ask for an explanation and a traceable source trail.
- **Reference Remix:** a visual brief and references you have permission to use.
  Ask for a finished artifact in a format your agent can make.
- **Unstick Project:** existing work, failed attempts and a concrete thing you
  need next. Ask for the smallest useful artifact that preserves your commitments.

Use a task you care about. Keep private inputs local. A public report can describe
the outcome and use a reduced made-up example instead of uploading those inputs.

## Install and observe loading

Follow [the project installation guide](installation.md) for one complete package.
Preview its destination, copy it, and use `--check` to verify the copy. Start a fresh
agent session in that project. Explicitly select the method using your host's
documented mechanism and confirm which installed `SKILL.md` it read. Record a
loading failure separately from a disappointing task result.

Give the agent your actual goal, inputs, fixed choices and desired output. Avoid
telling it what conclusion to reach. Keep the final artifact and note any repairs
you had to make before it was useful.

## Report the result

Use [the field-test form](https://github.com/GWeale/knackset/issues/new?template=field-test.yml).
A success, a tie with your usual approach, and a failure are all useful reports.
Include:

- Skill name, release or commit, agent and model.
- Whether loading was observed, and what the agent actually produced.
- What you kept, changed or discarded, and the first confusing instruction.
- Time spent, including manual corrections. Leave cost unknown unless metered.
- A sanitized artifact or reduced reproduction you have permission to share.

For a stronger comparison, run the same request in another fresh session without
the skill, using the same model, tools and inputs. Do not show either output to
the other agent. Compare the two artifacts before revealing which used the skill.
One comparison is feedback on that task, not proof of general improvement.

## Invite a tester

This text is ready to send to someone who already uses a coding agent:

> I'm testing Knackset, a small collection of methods for investigating questions,
> making things from references and getting stalled projects moving. Would you
> try one on a real task for about 20 minutes? I'd like to know what you kept,
> what you had to fix and where the instructions got in your way. Preview skills,
> examples and the test guide are at github.com/GWeale/knackset. Keep private
> material local; a short sanitized report is enough.

No invitations or independent user reports are implied by this packet. The first
feedback round closes when five people have submitted inspectable reports.
Triaging those reports and retesting supported fixes comes next.
