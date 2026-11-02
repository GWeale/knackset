#!/usr/bin/env python3
"""Optional local preview: existing librsvg + Cairo via Python stdlib ctypes.
No browser, Python packages, downloads or font files are used. SVGs remain the
edition masters. PNGs are inspection aids, not print-production exports.
"""
import argparse
import ctypes as C
import ctypes.util
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

class Rect(C.Structure):
    _fields_ = [('x', C.c_double), ('y', C.c_double), ('width', C.c_double), ('height', C.c_double)]

class GError(C.Structure):
    _fields_ = [('domain', C.c_uint), ('code', C.c_int), ('message', C.c_char_p)]


def render(source, target, px_per_mm):
    rsvg = C.CDLL(ctypes_name('rsvg-2'))
    cairo = C.CDLL(ctypes_name('cairo'))
    gobject = C.CDLL(ctypes_name('gobject-2.0'))
    rsvg.rsvg_handle_new_from_file.argtypes = [C.c_char_p, C.POINTER(C.POINTER(GError))]
    rsvg.rsvg_handle_new_from_file.restype = C.c_void_p
    rsvg.rsvg_handle_render_document.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(Rect), C.POINTER(C.POINTER(GError))]
    rsvg.rsvg_handle_render_document.restype = C.c_int
    cairo.cairo_image_surface_create.argtypes = [C.c_int, C.c_int, C.c_int]
    cairo.cairo_image_surface_create.restype = C.c_void_p
    cairo.cairo_create.argtypes = [C.c_void_p]
    cairo.cairo_create.restype = C.c_void_p
    cairo.cairo_surface_write_to_png.argtypes = [C.c_void_p, C.c_char_p]
    cairo.cairo_surface_write_to_png.restype = C.c_int
    cairo.cairo_destroy.argtypes = [C.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [C.c_void_p]
    cairo.cairo_version_string.restype = C.c_char_p
    cairo.cairo_surface_flush.argtypes = [C.c_void_p]
    cairo.cairo_image_surface_get_data.argtypes = [C.c_void_p]
    cairo.cairo_image_surface_get_data.restype = C.POINTER(C.c_ubyte)
    cairo.cairo_image_surface_get_stride.argtypes = [C.c_void_p]
    cairo.cairo_image_surface_get_stride.restype = C.c_int
    gobject.g_object_unref.argtypes = [C.c_void_p]
    root = ET.parse(source).getroot()
    view = [float(n) for n in root.get('viewBox').split()]
    width, height = round(view[2] * px_per_mm), round(view[3] * px_per_mm)
    error = C.POINTER(GError)()
    handle = rsvg.rsvg_handle_new_from_file(str(source).encode(), C.byref(error))
    if not handle:
        raise RuntimeError(error.contents.message.decode())
    surface = cairo.cairo_image_surface_create(0, width, height)
    cr = cairo.cairo_create(surface)
    visible_bounds = None
    try:
        if not rsvg.rsvg_handle_render_document(handle, cr, C.byref(Rect(0, 0, width, height)), C.byref(error)):
            raise RuntimeError(error.contents.message.decode())
        if source.parent.name == 'selected':
            cairo.cairo_surface_flush(surface)
            stride = cairo.cairo_image_surface_get_stride(surface)
            pixels = C.string_at(cairo.cairo_image_surface_get_data(surface), stride * height)
            ground = pixels[:4]
            coordinates = [(x, y) for y in range(height) for x in range(width)
                           if pixels[y * stride + x * 4:y * stride + x * 4 + 4] != ground]
            visible_bounds = [min(x for x, y in coordinates), min(y for x, y in coordinates),
                              max(x for x, y in coordinates), max(y for x, y in coordinates)]
            l, t, r, b = visible_bounds
            border = 8 * px_per_mm
            assert l >= border and t >= border and r < width - border and b < height - border, visible_bounds
        result = cairo.cairo_surface_write_to_png(surface, str(target).encode())
        if result:
            raise RuntimeError(f'Cairo PNG error {result}')
    finally:
        cairo.cairo_destroy(cr)
        cairo.cairo_surface_destroy(surface)
        gobject.g_object_unref(handle)
    return {'svg': str(source.relative_to(ROOT)), 'png': str(target.relative_to(ROOT)),
            'svg_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'png_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'pixel_dimensions': [width, height], 'pixels_per_mm': px_per_mm,
            'non_ground_pixel_bounds': visible_bounds,
            'eight_mm_blank_border_checked': visible_bounds is not None,
            'cairo_version': cairo.cairo_version_string().decode(),
            'librsvg_version': '.'.join(str(C.c_uint.in_dll(rsvg, 'rsvg_' + p + '_version').value)
                                       for p in ('major', 'minor', 'micro'))}


def ctypes_name(name):
    value = C.util.find_library(name)
    if not value:
        raise RuntimeError('Optional local renderer unavailable: ' + name)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pixels-per-mm', type=float, default=4.0)
    args = parser.parse_args()
    assert 1 <= args.pixels_per_mm <= 12
    target_dir = ROOT / 'previews'
    target_dir.mkdir(exist_ok=True)
    files = [ROOT / f'exploration-{v}.svg' for v in ('a', 'b', 'c')]
    files += [ROOT / 'overview.svg'] + sorted((ROOT / 'selected').glob('*.svg'))
    records = [render(path, target_dir / (path.stem + '.png'), args.pixels_per_mm) for path in files]
    (ROOT / 'render-settings.json').write_text(json.dumps({'renderer_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'renders': records}, indent=2) + '\n')
    print(f'Rendered {len(files)} SVGs with existing librsvg/Cairo at {args.pixels_per_mm:g} px/mm.')

if __name__ == '__main__':
    main()
