# Synthetic product record export

These are fictional records supplied for an offline task. Titles and paths are
source locators within this bundle; they are not live services.

## Issue 74 — Filter during a workshop

Opened 2024-08-08. Closed 2024-08-21.

Request: Help a facilitator find a card by phrase while sharing a board. Filtering
must work with a board arranged into groups. The current prototype opens every
group with a match.

Trial note, 2024-08-15: The facilitator had collapsed the previous exercise and
kept the next activity open. Searching for a phrase brought the earlier exercise
back into view. Clearing search restored the old group choices, but the presenter
lost their place and had to scroll back. Two participants thought the session was
returning to that exercise. The trial used 46 cards across six groups.

Product comment, 2024-08-16: Do not make a search action change the presenter's
chosen group state. A collapsed matching group still needs a visible match count
and the facilitator can open it. We can revisit finding hidden matches after this
interaction settles.

Closure, 2024-08-21: Group-state change merged in 6a1c098. Header counts merged
in 85f03ab. No additional workshop trial is attached to this issue.

## notes/board-filter-review.md

Created 2024-08-16. Last modified 2024-08-16.

Options discussed:

1. Temporarily open every matching group, returning to saved group state on clear.
2. Leave group choices alone, hide groups with no matches, and show the number
   of matching cards in remaining headers.
3. Show results in a separate panel without changing the board.

For this release, use option 2. The live board should remain under the
facilitator's control; searching is a way to locate material within the current
session arrangement. Option 1 is what we trialled. Option 3 needs an interaction
for locating a result back on the board, which we have not designed.

Large-board rendering is a separate open item. This interaction decision uses the
small workshop trial. We have no large-board timing attached. Performance review
is scheduled after the filter work.

## Handbook — Board UX notes

Created 2025-03-03. Last modified 2025-09-25. Page owner: UI maintenance group.
No version before creation is present in this export.

Filters narrow the board by group. Groups stay collapsed for rendering
performance: avoid mounting a card collection until someone opens its group.
The filter displays counts so a match can still be found.

Links: component naming guide; card keyboard shortcuts. No decision or timing
study is linked in this section.

## Performance task 203 — Filter timing

Record dated 2026-02-11. Local development laptop; static fixture; no concurrent
collaborators. 1,200 cards, 40 groups, short text only.

Filter to 18 matching groups, all forced open for this measurement:
median update 19 ms across 20 samples, largest 28 ms.

Same query with saved group states (three groups open):
median update 12 ms across 20 samples, largest 17 ms.

Notes: no touch device, long card bodies, images, remote cursors, or screen-share
measurement in this task. No interaction recommendation recorded.
