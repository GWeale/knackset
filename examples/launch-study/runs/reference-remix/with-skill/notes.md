# Knackset launch card

Finished files: `card.svg` (editable 1200×630 source), `card.png` (1200×630), and `card-600.png` (600×315 inspection preview).

The governing idea is **loose observations gathered into a keeper**. The promise leads in three large lines; a single tilted sheet supplies the visual counterweight. Sparse marks become an open ring of repeated strokes on the sheet. The gap keeps the form unresolved, while the sheet gives it a durable boundary. The orange stroke marks a selected observation. The mark's lime, green, cream and orange control the palette.

I considered an equal three-card arrangement for the named skills and a centered oversized brand. The three-card arrangement would split attention between three subjects; the selected composition gives the kit one promise and one visual object. Native geometric strokes and plain type fit an editable, small-format launch asset.

I rendered and inspected the actual supplied sources: Night Orchard at 594×840, Held Between at 712×816, and the icon at 256×256. Night Orchard's oversized type, quiet field and small isolated marks make attention feel deliberate. Held Between's four spaced specimens use dense repeated bands, shaped gaps and localized orange to make relationships visible. This card uses that tension between spacious typography and dense linework in a new landscape composition. Excluded: the orchard crown, dotted walking route, listening-card silhouettes, reference titles and fictional content. The supplied icon's four shapes and colors are preserved exactly, with translation only.

Checks passed:

- SVG XML, 1200×630 dimensions, all five required strings including punctuation and case.
- Exact icon shape attributes and fills against the supplied source.
- No linked images, scripts, external asset references or font imports.
- PNG dimensions at full and half size.
- Visual inspection of both final renders: reading order, complete copy, edge space, linework and small-type legibility. All primary content clears the edges; the rotated sheet remains inside the same right margin.

Rendering used the installed librsvg and Cairo libraries through `render.py`. Reference inspection PNGs are retained as `reference-night-orchard.png`, `reference-held-between.png`, and `reference-icon.png`. Inputs were only read. No network, publication, dependencies or commits were used.

Remaining limit: text uses installed DejaVu Sans; another editor without that font may substitute it. The supplied PNG fixes the observed appearance. Cross-editor rendering was not checked. No content or export gap remains.
