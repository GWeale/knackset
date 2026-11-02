# Held Between — local edition

Four fictional 160 × 160 mm listening cards are in `selected/`. Open `overview.html` for the linked index, or `overview.svg` for a portable labeled contact sheet. The SVGs are the masters; `previews/` contains raster inspection aids.

| Selected master | Source session | Role in the four-piece set |
| --- | --- | --- |
| `selected/HB-01-b.svg` | HB-01 / Underpass | A continuous field with a moving central absence and passing cuts. |
| `selected/HB-02-c.svg` | HB-02 / Potting shed | Uneven small gatherings give way to one longer event; the right side stays open. |
| `selected/HB-03-b.svg` | HB-03 / Back stair | Two overlapping voices are separated by one consequential shared interruption. |
| `selected/HB-05-b.svg` | HB-05 / Empty basin | Separated, diminishing returns carry attention diagonally into more empty ground. |

## Governing rule

A sound is held as a group of narrow, cut-ended strips; a pause becomes an actual gap. The shared geometry, fixed line thickness, ground, two mark colors, vector lettering and placement establish the family. The records change the spatial relationship: continuity, clustering, overlap, or separation. Duration is retained in the input, but is not plotted. No audio or reference image existed; this is an authored response to the supplied observer notes, not acoustic analysis.

The `spacing` axis is 0.86, 1.00 or 1.14. It expands horizontal positions and widths around x=80 mm, and expands vertical positions at 55% of that strength around y=70 mm. Mark thickness stays fixed. Each session keeps its seed across the three settings so this is a controlled comparison rather than a random-seed hunt. Randomness only perturbs local strip edges and irregular small marks. The six recipes produce the larger compositional differences.

## Selection from 18 actual candidates

All six records were generated at all three spacing settings. The three `exploration-*.svg` sheets show every candidate at a common 160 mm scale, with its ID; the SVG in `exploration/` and the manifest make each traceable.

- **Underpass / b** keeps the winding gap continuous and lets the two short absences register without the outer field dominating the card. The expanded c setting crowds the sides; a is less bodily present.
- **Potting shed / c** extends the small upper gatherings far enough to counter the long narrow descent. Its right-hand emptiness gives the set a necessary uneven balance; a draws the action into a tighter cluster.
- **Back stair / b** places two substantial competing fields in tension. The shared blank band cuts both voices clearly, and their overlap stays visible as a changing color boundary. c makes the rust field press too hard toward the edge; a softens the confrontation.
- **Empty basin / b** contributes large spaces between isolated events. The largest group in the upper right and smaller returns below-left remain related through their strip construction. a is timid beside the dense cards; c makes the initial impact too wide relative to the returns.

Window ledge was rejected because its all-over tick field repeats Underpass's dense role while making the central red gathering feel more like a highlighted sample. Service yard's top band and scattered groups are coherent, but repeat portions of both Potting shed and Empty basin without the same clear large-scale movement. These are set-level decisions, not claims that the rejected records are inherently less valuable.

## Reproduce exact pieces

Run these commands from this folder. Python 3 and its standard library are sufficient for the SVG edition. The generator resolves all paths relative to itself.

```sh
python3 generate.py
python3 generate.py --check
```

`generate.py` rebuilds all 18 candidate SVGs, the four selected copies, three exploration sheets, selected overview and `manifest.json`. The selected IDs are declared in `SELECTED`. `field-records.csv` bundles every input row. `manifest.json` records the complete selected and unselected recipes' parameters, per-session seeds, Python version, random implementation, dimensions, palette, input hash, generator hash, output hash and file paths. Files are UTF-8 with a final newline. No image asset or font is needed: the small lettering is authored vector paths in `GLYPHS`.

For byte-identical generation use the recorded Python implementation/version. After an edit to source or input, regenerate and re-inspect: prior hashes no longer describe the edition. The source is intentionally ordinary named Python recipe methods; change a recipe relationship to extend the family rather than changing seeds until an attractive accident appears.

Optional local previews, using the already installed librsvg and Cairo shared libraries:

```sh
python3 render.py --pixels-per-mm 4
```

The preview helper uses only Python stdlib `ctypes`; it installs nothing. It writes eight PNGs and `render-settings.json`, recording the actual library versions, dimensions and hashes. It also checks that the selected raster renders leave the complete 8 mm edge border untouched. At 4 px/mm each individual is 640 × 640 px, approximately 101.6 pixels per inch. A display is not a calibrated physical print.

## Actual inspection and limits

On 2026-11-01, all 18 candidates were visually inspected in the three rendered exploration sheets, followed by all four selected 640 × 640 renders and the selected overview. The fine strips are visible at that render scale; the late Empty basin returns are deliberately close, and separate just enough to carry the diminishing rhythm. Title and session lettering remained legible in the individual renders.

Structural checks cover source/input/output hash agreement, four exact selected copies, XML parsing, 160 mm dimensions, the restricted palette, absence of external resources and transparency attributes, artwork bounds, and the complete rendered 8 mm blank border. A second generation was compared byte-for-byte with the first edition's SVGs and manifest. See `checks.txt` for the actual output.

No print, calibrated monitor inspection, physical 160 mm proof, paper/ink test, browser test, cross-renderer test or live installation test was performed. The RGB ground is included in the SVG; no bleed, crop marks, or unapproved identity was added. The data, commission and response are fictional. No network, account, browser, GUI, installation, external font or publication was used.
