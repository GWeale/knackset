# Research and upstream references

Checked **2026-11-01** against public primary sources. Repository paths and product
behavior can change; the observations below describe the material inspected on
that date. This library contains original procedures, with no upstream skill files
or proprietary prompts copied into it. See [provenance](provenance.md).

## Product names and scope

The uncertain names transcribed as “grockbot” or “Rockbot” plausibly mean
**Grok Bot**: its official documentation describes persistent computers, browsers,
skills, and routines. **Meta Muse** is another strong match for the stated personal
agent inspiration. These are likely identifications, not a confirmed reading of
the transcription. [Grok Bot overview](https://docs.x.ai/grok-bot/overview),
[Meta Muse overview](https://ai.meta.com/muse/)

Grok Bot documents saving a successful method as a skill, then automating it with
a routine. Where its teaching control is available, a user can demonstrate a
browser workflow, review the generated draft, and test a safe example before
scheduling it. One demonstration still needs decision rules, failure handling,
and approval boundaries. [Official skills and routines guide](https://docs.x.ai/grok-bot/skills-routines-and-automations)

The reviewed official consumer Muse pages do not establish native `SKILL.md`
import compatibility. Muse Code has separate skill documentation; support there
does not establish support in the consumer Muse app. Meta also describes a Muse
browser subagent without page JavaScript execution or DevTools access. Avoid
claiming compatibility based only on a shared skill format or product name.
[Muse overview](https://ai.meta.com/muse/),
[Muse Code skills](https://meta-models.github.io/muse-code-sdk/next/guides/extend/skills/),
[Meta's browser architecture](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse)

A **skill** packages procedural knowledge and optional supporting resources. A
**runtime or browser tool** provides execution, sessions, authentication, and
actions. A file format alone does not make tool commands portable. OpenClaw is a
useful open-source comparator, not evidence that the unclear name meant OpenClaw.
[Agent Skills specification](https://agentskills.io/specification),
[OpenClaw skills](https://docs.openclaw.ai/tools/skills)

## Eight useful open-source references

License notes are observations from upstream declarations, not conclusions about
every bundled file. Check the exact file and revision before adapting material.

| Repository | Concrete material to inspect | Observed license and use here |
| --- | --- | --- |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | `docs/` defines the format; `skills-ref/` provides reference tooling. | Code Apache-2.0; documentation CC-BY-4.0. Use the format as the interchange boundary. [License distinction](https://github.com/agentskills/agentskills#license) |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `skills/`, `optional-skills/`; `skills/productivity/product-price-monitor/SKILL.md` is a complete monitoring procedure. | Root MIT; the named example also declares MIT. Individual imported skills may differ. Its documented `/learn` flow can derive a skill from sources or a completed workflow. [Example](https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/product-price-monitor/SKILL.md), [learning flow](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills), [license](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | `skills/agent-browser/`, `skill-data/core/`, `skill-data/dogfood/`, `evals/`. | Apache-2.0. Browser runtime with packaged operating guidance, rather than a catalog of portable business procedures. The CLI can serve skill content matching its installed version. [Core skill](https://github.com/vercel-labs/agent-browser/blob/main/skill-data/core/SKILL.md), [license](https://github.com/vercel-labs/agent-browser/blob/main/LICENSE) |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | `skills/browser-use/`, `skills/open-source/`, `skills/qa/`, `examples/`. | MIT. Separates direct browser operation from Python library references; useful for a tool binding and QA patterns. Open-source library and hosted cloud services are distinct offerings. [Browser skill](https://github.com/browser-use/browser-use/blob/main/skills/browser-use/SKILL.md), [library reference](https://github.com/browser-use/browser-use/blob/main/skills/open-source/SKILL.md), [license](https://github.com/browser-use/browser-use/blob/main/LICENSE) |
| [Tencent/BrowserSkill](https://github.com/Tencent/BrowserSkill) | `crates/bsk-cli/skill/SKILL.md`, `packages/dsh-plugin-browserskill/skill/`, `evals/browser/`. | MIT. The skill requires the `bsk` CLI and browser extension; cross-agent availability is not independence from those tools. Useful for explicit session ownership and browser operation contracts. [Actual skill](https://github.com/Tencent/BrowserSkill/blob/main/crates/bsk-cli/skill/SKILL.md), [license](https://github.com/Tencent/BrowserSkill/blob/main/LICENSE) |
| [anthropics/skills](https://github.com/anthropics/skills) | `skills/webapp-testing/`, `skills/skill-creator/`, `template/`. | Many examples Apache-2.0; webapp-testing explicitly has that license. The repository identifies `docx`, `pdf`, `pptx`, and `xlsx` as source-available, not open source. Useful packaging and local verification examples. [Repository distinction](https://github.com/anthropics/skills#about-this-repository), [webapp-testing license](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/LICENSE.txt) |
| [ServiceNow/BrowserGym](https://github.com/ServiceNow/BrowserGym) | `browsergym/core/`, `browsergym/experiments/`, benchmark adapters, `tests/`. | Apache-2.0 for BrowserGym; benchmark and website assets require their own checks. Evaluation infrastructure, not a skill collection. Useful for repeatable browser tasks and outcome measurement. [License](https://github.com/ServiceNow/BrowserGym/blob/main/LICENSE) |
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | `skills/`, `extensions/browser/skills/browser-automation/`. | Root MIT; inspect individual third-party material separately. Its browser skill assumes the OpenClaw browser tool. Useful compatibility and recovery reference, not a drop-in portable binding. [Browser skill](https://github.com/openclaw/openclaw/blob/main/extensions/browser/skills/browser-automation/SKILL.md), [license](https://github.com/openclaw/openclaw/blob/main/LICENSE) |

## Secondary leads and limits

- [AutoSkill](https://github.com/ECNU-ICALK/AutoSkill) has offline conversation and
  trajectory extraction, `skills/autoskill/`, `SkillEvo/`, and `SkillBank/`. Its
  README displays an MIT badge, but no root license grant was found in the
  inspected tree and the root `LICENSE` path returned 404. Reuse status for its own
  implementation remains unverified; collected skills carry separate provenance.
  [Primary README](https://github.com/ECNU-ICALK/AutoSkill/blob/main/README.md)
- [WebXSkill](https://github.com/aiming-lab/WebXSkill) studies parameterized skills
  extracted from browser trajectories and URL-based retrieval. The inspected
  repository README says implementation is forthcoming; no usable implementation
  or license was established. Treat it as research inspiration.
  [Paper](https://arxiv.org/abs/2604.13318),
  [repository README](https://github.com/aiming-lab/WebXSkill/blob/main/README.md)

## Ranked next actions

These are project recommendations inferred from the references, not upstream
endorsements or evidence that this library has already passed live evaluation.

1. **Keep each original skill self-contained.** Package triggers, required inputs,
   access assumptions, branching, recovery, output, and verification in its folder.
   Keep tool commands in optional bindings so the procedure can survive a runtime
   change. Follow the [workflow contract](workflow-contract.md).
2. **Sanitize capture, then replay the draft.** Turn a successful session into a
   parameterized procedure; remove account data and incidental navigation. Review
   the draft, test harmless fixtures, and record observed evidence separately from
   proposed steps. See [provenance](provenance.md) and [evaluation](../evals/README.md).
3. **Require multiple real bindings before portability claims.** Exercise the same
   workflow with at least two supported browser or service interfaces. Record the
   runtime, revision, date, task variant, saved outcome, and unsupported operations.
   Structural validation and offline review do not establish host compatibility.
