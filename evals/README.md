# Evaluate a workflow skill

`scenarios.json` contains synthetic tasks and acceptance rubrics, not browser
recordings or measured results. Each skill starts with a success case and a
boundary/failure case. Add observed failures before expanding into a large suite.

The first [offline review record](offline-review-2026-11-01.md) contains seven
fixture decision checks and one executed local helper case, with content hashes.
It does not claim all scenarios or any live application workflow were executed.

## Three different checks

1. `python3 scripts/validate.py` checks package structure, links, catalog consistency,
   and scenario coverage. It does not judge instructions or perform a workflow.
2. `python3 -m unittest discover -s tests -v` executes local helper CLIs against
   temporary synthetic files. It does not test Gmail, Sheets, GitHub, or a browser.
3. Forward evaluation asks an independent agent to use a skill on a supplied task,
   then checks actual resulting artifacts/state against a withheld rubric. A plan
   review establishes decision behavior only; a live workflow requires real tool
   execution and observation of the relevant final state.

## Run a forward evaluation

Give a fresh evaluator only the skill folder, scenario prompt/context, permitted
tools, and synthetic inputs. Withhold expected/forbidden arrays until judging the
result. Use a temporary workspace, not the skill library's public tree. Do not give
the evaluator author conclusions, a suggested solution, or private session logs.

If no browser/test account is available or authorized, request a decision trace
against the supplied observed state. Record that limitation; never call it a
browser replay. For a real execution, supply an explicitly authorized disposable
account/site fixture and verify resulting records and duplicate counts.

Record date, skill revision or content hash, runtime/model and available tools,
prompt/context, actual output/action trace or artifact, checked assertions, result,
and limits. Keep private execution evidence local. Publish only synthetic or
independently sanitized evidence. Compare the same tasks without the skill before
making a claim that the skill improves performance.

Promote a catalog entry only when its evidence supports the declared scope:
`offline-reviewed` requires recorded fixture evaluation; `live-tested` requires
dated execution evidence for that exact site/task/runtime. Format checks and an
assistant's success claim alone are insufficient. No benchmark score or live
compatibility claim is implied by this starter suite.

Approach informed by [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills)
and [Anthropic's outcome-based agent evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
