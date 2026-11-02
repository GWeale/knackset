"""Rebuild the fictional Pocket Radio proof using only Python's standard library."""
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
import json

OUT = Path(__file__).resolve().parent
WIDTH_PT = 150 * 72 / 25.4
HEIGHT_PT = 100 * 72 / 25.4
INK = '#272720'
CREAM = '#f5f0e6'
BODY = ('I kept this by the kitchen window. The signal was clearest just before the '
        'weather forecast. My brother would call afterward to ask whether it would rain.')
BODY_LINES = [
    'I kept this by the kitchen window.',
    'The signal was clearest just before the',
    'weather forecast. My brother would call',
    'afterward to ask whether it would rain.',
]
# With the physical page and viewBox below, one coordinate unit equals one point.
# Every entry is (text, baseline from top, point size, bold).
LAYOUT = [
    ('Small Hours', 34, 12, False),
    ('Pocket Radio', 84, 28, True),
    ('Loaned by E. Vale', 108, 13, False),
] + [(line, 151 + index * 21, 14, False) for index, line in enumerate(BODY_LINES)]
LEFT = 10 * 72 / 25.4

svg_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<svg xmlns="http://www.w3.org/2000/svg" width="150mm" height="100mm" '
    f'viewBox="0 0 {WIDTH_PT:.8f} {HEIGHT_PT:.8f}" role="img" '
    'aria-labelledby="proof-title proof-description">',
    '<title id="proof-title">Pocket Radio</title>',
    '<desc id="proof-description">Small Hours label proof. '
    '150 by 100 millimetres, landscape. Approved text only; no photograph.</desc>',
    f'<rect x="0" y="0" width="{WIDTH_PT:.8f}" height="{HEIGHT_PT:.8f}" fill="{CREAM}"/>',
    f'<g fill="{INK}" font-family="Arial, Helvetica, sans-serif">',
]
for text, baseline, size, bold in LAYOUT:
    weight = '700' if bold else '400'
    svg_lines.append(f'<text x="{LEFT:.8f}" y="{baseline}" font-size="{size}" '
                     f'font-weight="{weight}">{escape(text)}</text>')
svg_lines += ['</g>', '</svg>']
svg_path = OUT / 'pocket-radio-proof.svg'
svg_path.write_text('\n'.join(svg_lines) + '\n', encoding='utf-8')

# A supplementary PDF uses the same point positions and standard PDF fonts.
# It enables local rendering without an SVG renderer; it does not certify how an
# SVG viewer will resolve the SVG's system-font fallback.
def rgb(colour):
    return ' '.join(f'{int(colour[i:i+2], 16) / 255:.7f}' for i in (1, 3, 5))

def pdf_string(text):
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

commands = [f'{rgb(CREAM)} rg 0 0 {WIDTH_PT:.8f} {HEIGHT_PT:.8f} re f', f'{rgb(INK)} rg']
for text, baseline, size, bold in LAYOUT:
    font = 'F2' if bold else 'F1'
    commands.append(f'BT /{font} {size} Tf 1 0 0 1 {LEFT:.8f} '
                    f'{HEIGHT_PT-baseline:.8f} Tm ({pdf_string(text)}) Tj ET')
stream = ('\n'.join(commands) + '\n').encode('ascii')
objects = [
    b'<< /Type /Catalog /Pages 2 0 R >>',
    b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    (f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {WIDTH_PT:.8f} {HEIGHT_PT:.8f}] '
     '/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>').encode('ascii'),
    b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
    b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
    f'<< /Length {len(stream)} >>\nstream\n'.encode('ascii') + stream + b'endstream',
]
pdf = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
offsets = [0]
for number, obj in enumerate(objects, 1):
    offsets.append(len(pdf))
    pdf.extend(f'{number} 0 obj\n'.encode('ascii') + obj + b'\nendobj\n')
xref = len(pdf)
pdf.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode('ascii'))
for offset in offsets[1:]:
    pdf.extend(f'{offset:010d} 00000 n \n'.encode('ascii'))
pdf.extend((f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n').encode('ascii'))
(OUT / 'pocket-radio-proof.pdf').write_bytes(pdf)

# Inspect saved SVG, rather than trusting only generation-time variables.
ns = {'s': 'http://www.w3.org/2000/svg'}
root = ET.parse(svg_path).getroot()
texts = root.findall('.//s:text', ns)
visible = [node.text for node in texts]
viewbox = [float(value) for value in root.attrib['viewBox'].split()]
physical_pt_per_unit = (150 * 72 / 25.4) / viewbox[2]
font_sizes_pt = [float(node.attrib['font-size']) * physical_pt_per_unit for node in texts]
checks = {
    'status': 'passed',
    'page_mm': [150, 100],
    'checks': {
        'svg_parses': True,
        'landscape_dimensions': root.attrib['width'] == '150mm' and root.attrib['height'] == '100mm',
        'physical_scale_is_one_point_per_unit': abs(physical_pt_per_unit - 1) < 1e-8,
        'approved_heading_and_attribution': visible[:3] == ['Small Hours', 'Pocket Radio', 'Loaned by E. Vale'],
        'approved_body_unchanged': ' '.join(visible[3:]) == BODY,
        'all_visible_text_at_least_12pt': min(font_sizes_pt) >= 12 - 1e-6,
        'body_size_14pt': all(abs(size - 14) < 1e-6 for size in font_sizes_pt[3:]),
        'cream_background': root.find('s:rect', ns).attrib['fill'] == CREAM,
        'dark_ink': root.find('s:g', ns).attrib['fill'] == INK,
        'no_image_or_script_or_external_reference': all(
            node.tag.rsplit('}', 1)[-1] not in ('image', 'script', 'foreignObject')
            and not any(key.rsplit('}', 1)[-1] == 'href' for key in node.attrib)
            for node in root.iter()),
        'pdf_same_layout_and_text_source': True,
    },
    'body_size_pt': 14,
    'body_leading_pt': 21,
    'minimum_visible_text_pt': round(min(font_sizes_pt), 6),
    'svg_visual_inspection': 'Not performed: no non-browser SVG renderer was found.',
    'pdf_visual_inspection': 'Pending local rendering and inspection.',
    'print_test': 'Not performed.',
}
if not all(checks['checks'].values()):
    checks['status'] = 'failed'
(OUT / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
assert checks['status'] == 'passed', checks
print('Created SVG, supplementary PDF, and checks.json. Saved SVG checks passed.')
