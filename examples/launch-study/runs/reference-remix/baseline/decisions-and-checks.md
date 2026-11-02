# Knackset launch card

Finished deliverable: `card.svg`, an editable 1200×630 SVG. `card.png` is the full-size local preview; `card-small.png` checks the 600×315 reading size.

## Decisions

- Inspected the supplied SVG geometry and locally rendered both actual references. Night Orchard uses a 297×420 portrait field: very large, left-aligned type above a small open contour and a dotted route, followed by a pale information band. Held Between uses a 356×408 overview with four separated square compositions; repeated horizontal strokes form masses, deliberate gaps separate them, and warm interruptions create emphasis.
- Retained those relationships—generous dark space, a clear type hierarchy, dense repeated lines against a sparse wandering route, a restrained warm accent—while making a new horizontal composition. The striped question and folded terminal are newly drawn geometry. No orchard outline, individual listening-card shape, reference title, event, date, or fictional content was reused.
- The question makes the invitation visible. The route suggests following it; its folded terminal relates to making something tangible and to the supplied icon's folded corner. The three named methods and source URL sit together in a pale information band.
- Used the icon's exact four colors throughout. The supplied icon is embedded as editable vectors at 64×64, with its original paths, viewBox, corner radius, fills and proportions. The invitation and supporting text remain editable text in DejaVu Sans.

## Checks performed

- Rendered Night Orchard at 594×840 and Held Between at 712×816 using installed librsvg/Cairo, then inspected both PNGs visually.
- Rendered the final card at 1200×630 and 600×315 using the same libraries. Inspected both sizes for hierarchy, legibility, cropping, spacing, artwork/text collisions and icon appearance. Re-inspected the final full-size render after the text-spacing cleanup.
- `python3 check_card.py` passed: parseable SVG; exact width/height/viewBox; all five required text strings; five editable text objects; no images, scripts or linked assets; exact equality of the embedded icon children and source viewBox; both PNG dimensions and decode integrity; measured headline clearance and 281.7px between footer text blocks.
- `build_card.py` reproduces the SVG, and `render_svg.py` provides the local renderer. Source input hashes are recorded in `input-sha256.txt`; the supplied inputs were only read, never edited. All generated files are inside this output directory.

## Remaining gaps

No blocking gaps. Font substitution can change text metrics on a machine without DejaVu Sans; the PNG preserves the checked appearance. No browser, other SVG editor, or separate rendering engine was used. No network access or publication occurred.
