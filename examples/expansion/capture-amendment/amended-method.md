---
name: sketch-export
description: Export a small editable vector sketch and check the requested copy.
license: MIT
---
# Export a sketch
Use the requested dimensions and approved words. Keep text editable. Deliver
self-contained SVG using available fonts, then inspect the requested preview
when a renderer is available. Name an unavailable visual check rather than
claiming it passed. Exporting local files does not publish them.

Font availability can differ between the author's preview and the handoff
viewer. If the intended font is unavailable in that viewer, inspect the actual
fallback with the same copy and dimensions, checking that all lettering stays
within the requested bounds. If substitution causes overflow, choose an
available fallback within the stated typography constraints and inspect again.
Preserve editable text; do not turn lettering into paths when editability is
required. If no available editable choice meets the constraints, report that
limit rather than claiming the export satisfies them. Retain an intended font
that is available and fits; a fallback is not a universal replacement.

Report which viewers and font or fallback choices were checked. A successful
preview in those viewers does not establish compatibility elsewhere.
