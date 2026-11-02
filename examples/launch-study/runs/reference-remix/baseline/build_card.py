#!/usr/bin/env python3
"""Build the editable Knackset launch card; no external assets or dependencies."""
from pathlib import Path
from xml.etree import ElementTree as ET
import math

OUT = Path(__file__).resolve().parent
INPUTS = OUT.parents[2] / 'inputs'
# Preserve the source icon verbatim as a nested, uniformly scaled SVG.
icon = (INPUTS / 'assets/knackset-mark.svg').read_text()
icon = icon.replace('viewBox="0 0 64 64"', 'id="knackset-icon" x="56" y="42" width="64" height="64" viewBox="0 0 64 64"')
lines = []
for i in range(65):
    y = 120 + i * 5.1
    # Subtle shared curvature makes a field of lines rather than a flat hatch fill.
    wobble = 2.6 * math.sin(i * .19)
    lines.append(f'<path d="M720 {y:.2f} C845 {y+wobble:.2f} 1000 {y-wobble:.2f} 1135 {y:.2f}"/>')
art = '\n      '.join(lines)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="card-title card-description">
  <title id="card-title">Knackset — Creative field kit preview</title>
  <desc id="card-description">Follow a question. Make something worth keeping. Rabbit Hole, Reference Remix and Unstick Project. An open question made of fine parallel lines sits beside the invitation. github.com/GWeale/knackset.</desc>
  <metadata>Editable vector launch card. Original composition using the supplied Night Orchard and Held Between SVGs as visual references. The supplied Knackset icon is preserved without geometry or color changes. Text remains editable. Local font: DejaVu Sans. No linked images, scripts, or external resources.</metadata>
  <defs>
    <clipPath id="question-shape" clipPathUnits="userSpaceOnUse">
      <path d="M739 191 C775 105 952 91 1047 151 C1142 212 1122 303 1041 339 L956 375 C935 384 934 403 941 424 L866 444 C837 379 859 332 919 308 L1000 274 C1041 256 1044 225 1011 203 C963 170 866 172 838 216 Z"/>
    </clipPath>
    <clipPath id="accent-patch"><path d="M1029 178L1109 203L1082 244L1005 219Z"/></clipPath>
  </defs>
  <rect id="dark-field" width="1200" height="630" fill="#152a23"/>
  <g id="brand">
    {icon}
    <text x="138" y="100" fill="#f4efe5" font-family="DejaVu Sans, sans-serif" font-size="78" font-weight="700" letter-spacing="-3.4">Knackset</text>
  </g>
  <text id="preview-label" x="1144" y="77" text-anchor="end" fill="#c4cfba" font-family="DejaVu Sans, sans-serif" font-size="18">Creative field kit — preview</text>
  <g id="invitation" fill="#f4efe5" font-family="DejaVu Sans, sans-serif" font-size="56" font-weight="400" letter-spacing="-1.6">
    <text x="56" y="242"><tspan x="56" dy="0">Follow a question.</tspan> <tspan x="56" dy="69">Make something</tspan> <tspan x="56" dy="69">worth keeping.</tspan></text>
  </g>
  <g id="inquiry-art" aria-label="An open question formed from interrupted parallel lines">
    <!-- A wandering route changes scale into a dense, finite object. -->
    <path id="route" d="M629 451 C670 451 725 418 737 373 S733 277 786 247" fill="none" stroke="#afc49c" stroke-width="2" stroke-linecap="round" stroke-dasharray=".1 9"/>
    <circle cx="629" cy="451" r="4" fill="#d5e953"/>
    <g id="striped-question" clip-path="url(#question-shape)" fill="none" stroke="#d5e953" stroke-width="2.2" stroke-linecap="round">
      {art}
    </g>
    <g id="warm-interruption" clip-path="url(#question-shape)">
      <g clip-path="url(#accent-patch)" fill="none" stroke="#e87842" stroke-width="2.8">
        {art}
      </g>
    </g>
    <!-- The terminal is a small folded square, relating the artwork to the icon. -->
    <g id="question-terminal" transform="translate(884 457) rotate(-8 22 20)">
      <path d="M0 0H30L43 13V40H0Z" fill="#e87842"/>
      <path d="M30 0V13H43Z" fill="#f4efe5"/>
    </g>
  </g>
  <g id="details">
    <rect x="0" y="520" width="1200" height="110" fill="#f4efe5"/>
    <text id="skills" x="56" y="584" fill="#152a23" font-family="DejaVu Sans, sans-serif" font-size="23">Rabbit Hole · Reference Remix · Unstick Project</text>
    <text id="source-link" x="1144" y="582" text-anchor="end" fill="#152a23" font-family="DejaVu Sans, sans-serif" font-size="18">github.com/GWeale/knackset</text>
  </g>
</svg>
'''
ET.fromstring(svg)
(OUT/'card.svg').write_text(svg)
print(f'Wrote {OUT / "card.svg"}')
