#!/usr/bin/env python3
"""Held Between — editable, deterministic SVG edition; Python standard library only.

The recipes describe spatial relationships, not a plot of acoustic measurements.
Change one recipe or the SPACING axis to extend the family.  Regenerate all files
and update selection after a source change: the manifest hashes this source.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import platform
import random
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
GROUND, INK, RUST = '#F2E9D8', '#202A32', '#A84C37'
SPACING = {'a': 0.86, 'b': 1.00, 'c': 1.14}
# Final choices are recorded here after inspection. IDs never change meaning.
SELECTED = ['HB-01-b', 'HB-02-c', 'HB-03-b', 'HB-05-b']
SEEDS = {f'HB-{n:02d}': 7300 + n * 173 for n in range(1, 7)}

# Original single-line vector alphabet: no font files or system font dependency.
# Coordinates are in a 0.65 x 1 em box. Curves are deliberately plain and open.
GLYPHS = {
'A': 'M0,1 L.325,0 L.65,1 M.13,.62 H.52',
'B': 'M0,1 V0 H.32 Q.65,0 .65,.25 Q.65,.48 .32,.48 H0 M.32,.48 Q.68,.48 .68,.75 Q.68,1 .32,1 H0',
'C': 'M.65,.12 Q.52,0 .32,0 Q0,0 0,.5 Q0,1 .32,1 Q.52,1 .65,.88',
'D': 'M0,1 V0 H.24 Q.68,0 .68,.5 Q.68,1 .24,1 H0',
'E': 'M.65,0 H0 V1 H.65 M0,.48 H.52',
'F': 'M.65,0 H0 V1 M0,.48 H.52',
'G': 'M.65,.14 Q.52,0 .32,0 Q0,0 0,.5 Q0,1 .32,1 Q.52,1 .65,.86 V.54 H.36',
'H': 'M0,0 V1 M.65,0 V1 M0,.48 H.65',
'I': 'M.10,0 H.55 M.325,0 V1 M.10,1 H.55',
'J': 'M.65,0 V.72 Q.65,1 .32,1 Q0,1 0,.75',
'K': 'M0,0 V1 M.65,0 L0,.55 M.22,.36 L.68,1',
'L': 'M0,0 V1 H.65',
'M': 'M0,1 V0 L.34,.57 L.68,0 V1',
'N': 'M0,1 V0 L.65,1 V0',
'O': 'M.325,0 Q0,0 0,.5 Q0,1 .325,1 Q.65,1 .65,.5 Q.65,0 .325,0 Z',
'P': 'M0,1 V0 H.32 Q.65,0 .65,.27 Q.65,.54 .32,.54 H0',
'Q': 'M.325,0 Q0,0 0,.5 Q0,1 .325,1 Q.65,1 .65,.5 Q.65,0 .325,0 Z M.40,.75 L.75,1.08',
'R': 'M0,1 V0 H.32 Q.65,0 .65,.27 Q.65,.54 .32,.54 H0 M.32,.54 L.68,1',
'S': 'M.65,.12 Q.52,0 .32,0 Q0,0 0,.25 Q0,.44 .32,.5 Q.65,.56 .65,.76 Q.65,1 .32,1 Q.12,1 0,.88',
'T': 'M0,0 H.65 M.325,0 V1',
'U': 'M0,0 V.68 Q0,1 .325,1 Q.65,1 .65,.68 V0',
'V': 'M0,0 L.325,1 L.65,0',
'W': 'M0,0 L.15,1 L.34,.45 L.53,1 L.68,0',
'X': 'M0,0 L.65,1 M.65,0 L0,1',
'Y': 'M0,0 L.325,.5 L.65,0 M.325,.5 V1',
'Z': 'M0,0 H.65 L0,1 H.65',
'-': 'M.10,.5 H.55',
'0': 'M.325,0 Q0,0 0,.5 Q0,1 .325,1 Q.65,1 .65,.5 Q.65,0 .325,0 Z',
'1': 'M.12,.2 L.35,0 V1 M.10,1 H.60',
'2': 'M0,.22 Q0,0 .32,0 Q.65,0 .65,.22 Q.65,.38 .35,.62 L0,1 H.65',
'3': 'M0,.08 Q.65,-.15 .65,.25 Q.65,.5 .25,.5 Q.65,.5 .65,.76 Q.65,1.15 0,.92',
'4': 'M.52,1 V0 L0,.67 H.65',
'5': 'M.65,0 H0 V.48 H.28 Q.65,.48 .65,.75 Q.65,1 .28,1 Q.1,1 0,.92',
'6': 'M.6,.05 Q0,-.12 0,.65 Q0,1 .32,1 Q.65,1 .65,.7 Q.65,.4 .32,.4 Q0,.4 0,.7',
}


def vector_type(words, x, y, size, color=INK, weight=.065):
    out = []
    cursor = x
    for letter in words.upper():
        if letter == ' ':
            cursor += size * .48
            continue
        out.append(f'<path d="{GLYPHS[letter]}" transform="translate({cursor:.4f} {y:.4f}) scale({size:.4f})" fill="none" stroke="{color}" stroke-width="{weight}" stroke-linecap="round" stroke-linejoin="round"/>')
        cursor += size * .92
    return ''.join(out)


class Card:
    def __init__(self, record, variant):
        self.record, self.variant = record, variant
        self.id = record['record_id'] + '-' + variant
        self.spacing = SPACING[variant]
        self.seed = SEEDS[record['record_id']]
        self.rng = random.Random(self.seed)
        self.elements, self.bounds = [], []

    def strip(self, x, y, width, height=.65, color=INK, direction=1):
        # This one axis expands/compacts relationships around the same held center.
        # Thickness stays constant so a candidate's spacing is judged independently.
        x = 80 + (x - 80) * self.spacing
        y = 70 + (y - 70) * (1 + (self.spacing - 1) * .55)
        width *= self.spacing
        skew = self.rng.uniform(-.10, .10)
        cut = min(.8, width * .12) * direction
        points = [(x, y), (x + width, y + skew),
                  (x + width - cut, y + height + skew), (x + cut, y + height)]
        self.bounds.append([min(p[0] for p in points), min(p[1] for p in points),
                            max(p[0] for p in points), max(p[1] for p in points)])
        pts = ' '.join(f'{px:.4f},{py:.4f}' for px, py in points)
        self.elements.append(f'<polygon points="{pts}" fill="{color}"/>')

    def underpass(self):
        for i in range(67):
            y = 27 + i * 1.32
            edge = 23 + 2.3 * math.sin(i * .21)
            right = 137 + 2 * math.sin(i * .13)
            seam = 83 + 9 * math.sin(i * .075)
            gap = 3.2 + 2.3 * math.sin(i * .11) ** 2
            # A continuous field is cut by a wandering gap and two passing absences.
            cuts = [(seam - gap, seam + gap)]
            if 12 <= i <= 19:
                cuts.append((48 + (i - 12) * .7, 58 + (i - 12) * .7))
            if 44 <= i <= 49:
                cuts.append((111 - (i - 44) * .5, 121 - (i - 44) * .5))
            cursor = edge
            for left, end in sorted(cuts):
                if left > cursor:
                    self.strip(cursor, y, left - cursor, .48 + (i % 4 == 0) * .18)
                cursor = max(cursor, end)
            if cursor < right:
                self.strip(cursor, y, right - cursor, .48)
            if 27 <= i <= 36:
                self.strip(seam - gap - 16, y, 15.0, .65, RUST)

    def potting_shed(self):
        # Uneven taps gather, then a narrow spill breaks their common baseline.
        for k, (x, top, rows, w) in enumerate([(29, 25, 15, 10), (43, 30, 19, 13),
                (61, 23, 12, 8), (74, 37, 17, 10), (91, 31, 10, 7)]):
            for j in range(rows):
                self.strip(x + self.rng.uniform(-1.7, 1.7), top + j * 1.47,
                           w * self.rng.uniform(.68, 1.1), .72, INK)
        for j in range(39):
            y = 56 + j * 1.33
            x = 77 + math.sin(j * .15) * 3 + j * .14
            w = 22 - j * .26 + self.rng.uniform(-1.4, 1.4)
            self.strip(x, y, w, .85 if j < 13 else .60,
                       RUST if j < 20 else INK, -1)
        for j in range(4):
            self.strip(88 + j * 1.2, 111 + j * 1.6, 8 - j * 1.1, .5)

    def back_stair(self):
        for i in range(35):
            y = 25 + i * 2.45
            left = 24 + i * .37
            end = 96 - i * .23 + 5 * math.sin(i * .19)
            if 21 <= i <= 23:
                continue
            self.strip(left, y, end - left, .92 if i % 3 else 1.15, INK)
        for i in range(32):
            y = 39 + i * 2.43
            left = 75 + i * .32 + 5 * math.sin(i * .2)
            right = 136 - i * .28
            if 15 <= i <= 17:
                continue
            self.strip(left, y + 1.15, right - left, .68 if i % 3 else .96, RUST, -1)
        self.strip(41, 80.5, 89, 1.45, INK)

    def window_ledge(self):
        for row in range(44):
            y = 25 + row * 2.1
            for col in range(13):
                x = 24 + col * 8.4 + self.rng.uniform(-1.2, 1.2)
                if self.rng.random() < .12:
                    continue
                self.strip(x, y + self.rng.uniform(-.4, .4), self.rng.uniform(2.2, 5.9), .5)
        for j in range(8):
            self.strip(57 + j * .6, 64 + j * 1.2, 46 - j * 1.4, .7, RUST)

    def empty_basin(self):
        echoes = [(108, 28, 40, 14, 13), (80, 58, 29, 12, 11),
                  (57, 82, 22, 9, 10), (42, 100, 15, 7, 9), (34, 112, 9, 5, 8)]
        for k, (cx, top, width, height, rows) in enumerate(echoes):
            for j in range(rows):
                w = width * (1 - .09 * abs(j - (rows - 1) / 2) / rows)
                x = cx - w / 2 + .7 * math.sin(j * .8)
                self.strip(x, top + j * height / rows, w, .78 if k == 0 else .48,
                           RUST if k == 1 or (k == 0 and j == 7) else INK, -1)

    def service_yard(self):
        for j in range(14):
            self.strip(24 + self.rng.uniform(-1, 1), 25 + j * 1.30, 111, .38)
        for k, (x, y, w, count) in enumerate([(31, 47, 24, 14), (72, 52, 31, 12),
               (103, 66, 20, 11), (52, 80, 26, 9), (94, 101, 18, 7)]):
            for j in range(count):
                self.strip(x + math.sin(j * .35) * 1.5, y + j * 1.4,
                           w * self.rng.uniform(.80, 1.05), .65, RUST if k in (1, 4) else INK)

    def make(self):
        recipe = {'HB-01': self.underpass, 'HB-02': self.potting_shed,
                  'HB-03': self.back_stair, 'HB-04': self.window_ledge,
                  'HB-05': self.empty_basin, 'HB-06': self.service_yard}[self.record['record_id']]
        recipe()
        content = ''.join(self.elements)
        content += vector_type('HELD BETWEEN', 12, 137, 4.05)
        content += vector_type(self.record['label'], 12, 148, 2.22, weight=.075)
        title = html.escape('Held Between — ' + self.record['label'])
        desc = html.escape('Fictional listening card. ' + self.record['observer_note'])
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="160mm" viewBox="0 0 160 160" role="img" aria-labelledby="title desc">'
                f'<title id="title">{title}</title><desc id="desc">{desc}</desc>'
                f'<rect width="160" height="160" fill="{GROUND}"/>{content}</svg>')


def record_manifest(card, svg, source_hash, input_hash):
    bounds = [min(b[0] for b in card.bounds), min(b[1] for b in card.bounds),
              max(b[2] for b in card.bounds), max(b[3] for b in card.bounds)]
    return {'candidate_id': card.id, 'record': card.record,
            'source_sha256': source_hash, 'input_sha256': input_hash,
            'svg_sha256': hashlib.sha256(svg.encode()).hexdigest(),
            'parameters': {'spacing': card.spacing, 'mark_thickness_scaling': 'fixed',
                           'vertical_spacing_factor': 1 + (card.spacing - 1) * .55},
            'seed': card.seed, 'random_implementation': 'Python random.Random / Mersenne Twister',
            'runtime': platform.python_implementation() + ' ' + platform.python_version(),
            'dimensions_mm': [160, 160], 'viewBox': [0, 0, 160, 160],
            'palette': [GROUND, INK, RUST], 'art_bounds_mm': bounds,
            'static': True, 'selected': card.id in SELECTED,
            'candidate_file': f'exploration/{card.id}.svg',
            'edition_file': f'selected/{card.id}.svg' if card.id in SELECTED else None}


def overview(ids, cards, title, columns, cell=178):
    rows = math.ceil(len(ids) / columns)
    height = 26 + rows * (cell + 13)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{columns * cell}mm" height="{height}mm" viewBox="0 0 {columns * cell} {height}">',
           f'<rect width="100%" height="100%" fill="{GROUND}"/>', vector_type(title, 9, 9, 3.4)]
    for n, cid in enumerate(ids):
        x, y = (n % columns) * cell + 9, 25 + (n // columns) * (cell + 13)
        root = ET.fromstring(cards[cid])
        # Nest the source SVG at its intended physical size. All views use one scale.
        root.set('x', str(x)); root.set('y', str(y))
        root.set('width', '160'); root.set('height', '160')
        # IDs are isolated to avoid ambiguous accessibility references in the sheet.
        for node in root.iter():
            if 'id' in node.attrib:
                node.set('id', cid + '-' + node.get('id'))
        root.set('aria-labelledby', cid + '-title ' + cid + '-desc')
        out.append(ET.tostring(root, encoding='unicode'))
        out.append(vector_type(cid, x, y + 165, 2.4))
    out.append('</svg>')
    return ''.join(out)


def verify():
    manifests = json.loads((ROOT / 'manifest.json').read_text())
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    input_hash = hashlib.sha256((ROOT / 'field-records.csv').read_bytes()).hexdigest()
    count = 0
    for item in manifests['candidates']:
        assert item['source_sha256'] == source_hash, item['candidate_id'] + ': source changed'
        assert item['input_sha256'] == input_hash
        raw = (ROOT / item['candidate_file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['svg_sha256']
        root = ET.fromstring(raw)
        assert root.get('width') == root.get('height') == '160mm'
        assert root.get('viewBox') == '0 0 160 160'
        for node in root.iter():
            assert node.tag.rsplit('}', 1)[-1] in {'svg', 'title', 'desc', 'rect', 'path', 'polygon'}
            for key in ('fill', 'stroke'):
                if node.get(key):
                    assert node.get(key) in {GROUND, INK, RUST, 'none'}
            assert not any(k in node.attrib for k in ('opacity', 'filter', 'href', 'font-family'))
        l, t, r, b = item['art_bounds_mm']
        assert 8 <= l < r <= 152 and 8 <= t < b <= 128, (item['candidate_id'], item['art_bounds_mm'])
        if item['selected']:
            assert (ROOT / item['edition_file']).read_bytes() == raw
            count += 1
    assert count == 4
    print(f'PASS: {len(manifests["candidates"])} source/input/output hashes; 160 mm dimensions; flat palette; bounded artwork; 4 identical selected copies.')
    print('Type uses custom vector paths. Footer geometry is fixed within x=11.8..59 and y=136.8..150.4 mm; all marks clear the 8 mm border.')
    print('Structural validation does not certify printing or aesthetic quality.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='validate existing outputs without rewriting')
    args = parser.parse_args()
    if args.check:
        verify(); return
    records = list(csv.DictReader((ROOT / 'field-records.csv').open(newline='')))
    (ROOT / 'exploration').mkdir(exist_ok=True)
    (ROOT / 'selected').mkdir(exist_ok=True)
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    input_hash = hashlib.sha256((ROOT / 'field-records.csv').read_bytes()).hexdigest()
    cards, manifests = {}, []
    for record in records:
        for variant in SPACING:
            card = Card(record, variant)
            svg = card.make()
            cards[card.id] = svg
            (ROOT / 'exploration' / (card.id + '.svg')).write_text(svg + '\n')
            # Hash exactly the delivered bytes, including the final newline.
            manifests.append(record_manifest(card, svg + '\n', source_hash, input_hash))
            if card.id in SELECTED:
                (ROOT / 'selected' / (card.id + '.svg')).write_text(svg + '\n')
    for variant in SPACING:
        ids = [r['record_id'] + '-' + variant for r in records]
        (ROOT / f'exploration-{variant}.svg').write_text(overview(ids, cards, 'HELD BETWEEN', 3) + '\n')
    (ROOT / 'overview.svg').write_text(overview(SELECTED, cards, 'HELD BETWEEN', 2) + '\n')
    manifest = {'edition': 'Held Between / local fictional trial', 'generator': 'generate.py',
                'source_sha256': source_hash, 'input_file': 'field-records.csv',
                'selected_ids': SELECTED, 'candidates': manifests}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    verify()
    print('Generated 18 candidates, 4 selected SVGs, 3 exploration sheets, overview.svg and manifest.json.')

if __name__ == '__main__':
    main()
