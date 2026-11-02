#!/usr/bin/env python3
"""Small structural and content checks for the finished launch artifact."""
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image, ImageFont
import hashlib

OUT=Path(__file__).resolve().parent
INPUTS=OUT.parents[2]/'inputs'
ns={'s':'http://www.w3.org/2000/svg'}
root=ET.parse(OUT/'card.svg').getroot()
assert (root.get('width'),root.get('height'),root.get('viewBox'))==('1200','630','0 0 1200 630')
text=' '.join(' '.join(root.itertext()).split())
for required in ['Knackset','Follow a question. Make something worth keeping.','Rabbit Hole · Reference Remix · Unstick Project','Creative field kit — preview','github.com/GWeale/knackset']:
    assert required in text, required
assert len(root.findall('.//s:text',ns))==5
assert not root.findall('.//s:image',ns)
assert not root.findall('.//s:script',ns)
assert all(not k.endswith('href') for e in root.iter() for k in e.attrib)
source_icon=ET.parse(INPUTS/'assets/knackset-mark.svg').getroot()
card_icon=root.find('.//s:svg[@id="knackset-icon"]',ns)
assert card_icon is not None
assert [ET.tostring(e) for e in source_icon]==[ET.tostring(e) for e in card_icon]
assert card_icon.get('viewBox')==source_icon.get('viewBox')
for name,size in [('card.png',(1200,630)),('card-small.png',(600,315))]:
    with Image.open(OUT/name) as img:
        assert img.size==size
        img.verify()
# Text width and row separation measured with the font used in the SVG.
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
skills=ImageFont.truetype(font,23).getlength('Rabbit Hole · Reference Remix · Unstick Project')
url=ImageFont.truetype(font,18).getlength('github.com/GWeale/knackset')
assert 56+skills+100 < 1144-url
assert 56+ImageFont.truetype(font,56).getlength('Follow a question.') < 629
# Document the sources as observed; all input access was read-only.
manifest={str(p.relative_to(INPUTS)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(INPUTS.rglob('*')) if p.is_file()}
(OUT/'input-sha256.txt').write_text('\n'.join(f'{digest}  {name}' for name,digest in manifest.items())+'\n')
print('PASS: SVG XML, 1200×630 dimensions, all five required strings, editable text, no linked assets/scripts, exact icon children and viewBox, both PNG dimensions/decode, measured footer gap and headline clearance.')
print(f'Footer gap: {1144-url-(56+skills):.1f}px. Recorded {len(manifest)} supplied input hashes.')
