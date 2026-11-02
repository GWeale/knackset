# Supplied-record evidence trail

Locators below refer only to the fictional supplied bundle. No links were followed outside that bundle.

| Claim | Locator | Evidence class | Confidence / limit |
| --- | --- | --- | --- |
| Matching groups retain saved open/closed choices at the exported head. | `board-source.txt`: head `b41d620`; `ui/board/groupVisibility.ts` lines 01–13, especially 07 and 10. | Current exported implementation. | High for the export; not live execution. |
| Collapsed matching groups have counts and avoid rendering the card collection. | `board-source.txt`: selector lines 11–12; `BoardView.tsx` excerpt, `Header` and conditional `Cards`. | Current exported implementation. | High for the excerpt; no measured impact implied by code alone. |
| The old prototype already restored saved expansion on clearing search. | `board-history.txt`: `312bc40`, 2024-08-12, ternary `isOpen`; `board-records.md`: Issue 74, 2024-08-15 trial note. | Historical implementation and contemporaneous observation. | High; restoration alone did not prevent the observed disruption. |
| Automatic opening disrupted workshop continuity in the recorded trial. | `board-records.md`: Issue 74, 2024-08-15, 46 cards / six groups. | Contemporaneous observed trial account. | High that the supplied account reports it; one trial, not prevalence evidence. |
| Facilitator control was the recorded reason for adopting saved-state expansion. | `board-records.md`: Issue 74, 2024-08-16 product comment; `notes/board-filter-review.md`, created/modified 2024-08-16, option 2. | Contemporaneous rationale. | High; directly connects constraint and choice. Does not reveal every private consideration. |
| Performance was a separate open item at adoption. | `board-records.md`: final paragraph of `notes/board-filter-review.md`. | Contemporaneous scope statement. | High; explicitly no large-board timing attached and performance review scheduled later. |
| The choice was implemented, not left as a proposal. | `board-history.txt`: `6a1c098`, 2024-08-19, selector replacement, review reference, preservation test; `board-records.md`: Issue 74 closure, 2024-08-21. | Adoption evidence. | High; no additional workshop trial attached, so deployment is not proof of successful remedy. |
| Match counts were the accompanying discovery mitigation. | `board-records.md`: product comment and option 2; `board-history.txt`: `85f03ab`, 2024-08-21. | Contemporaneous rationale plus implementation change. | High; no supplied usability measurement of the mitigation. |
| Separate results were considered but needed a return-to-board interaction. | `board-records.md`: review options 1–3 and following paragraph. | Contemporaneous alternative/tradeoff. | High; not evidence the alternative is unsuitable today. |
| The handbook later gives a performance account. | `board-records.md`: Handbook — Board UX notes; created 2025-03-03, modified 2025-09-25, no prior versions or supporting decision/timing link. | Retrospective account. | High that it says this; exact wording date and basis unknown. Later page dates cannot date every statement. |
| The latest refactor did not introduce the behavior. | `board-history.txt`: `b41d620`, 2025-10-09; rename, no executable change, comment replacement; blame maps line 10 to `6a1c098`. | Historical attribution. | High; broadening the reference may obscure the original note for a reader, but intent behind that edit is unknown. |
| Saved-state expansion had a later measured performance benefit in one fixture. | `board-records.md`: Performance task 203, 2026-02-11: 1,200 cards / 40 groups / 18 matching; 20 samples per condition; all matching open 19 ms median / 28 ms largest, saved states with three open 12 ms / 17 ms. | Later measurement. | High within the reported setup; no touch, rich cards, collaborators, or screen-share coverage; no recommendation. |
| Performance does not explain the recorded origin, but may matter to the new decision. | Adoption notes and later handbook/task 203 together. | Inference from timing and direct adoption rationale. | High for the documented origin; not a claim that performance was never privately considered. |

## Inspection log

- Read `skills/decision-archaeology/SKILL.md` once.
- Read the three supplied exports: `skills/decision-archaeology/evals/files/board-source.txt`, `board-history.txt`, and `board-records.md`.
- Wrote and reviewed this trial's `explanation.md`, `evidence-trail.md`, and `final.txt`.
- No other source files, hidden case definitions, validation notes, tests outside the supplied excerpt, expected answers, or other trials inspected. No network, browser, installs, accounts, code changes, commits, or publication.
