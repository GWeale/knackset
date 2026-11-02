#!/usr/bin/env python3
"""Build an 80-second captioned deck from the saved creative-pilot outputs.

Optional local build tools: Pillow, librsvg, Cairo and DejaVu Sans.
No downloads, browser, model calls or account access. Run from any directory.
"""

import base64
import ctypes as C
import ctypes.util
from html import escape
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / "launch-study"
WIDTH, HEIGHT = 960, 540
DURATIONS = [8000, 14000, 18000, 16000, 14000, 10000]


def image(path, x, y, width, height):
    data = base64.b64encode(path.read_bytes()).decode()
    return (f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'href="data:image/png;base64,{data}" preserveAspectRatio="xMidYMid meet"/>')


def text(value, x, y, size=25, color="#f4efe5"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans" '
            f'font-size="{size}">{escape(value)}</text>')


def render(source, destination):
    class Rectangle(C.Structure):
        _fields_ = [(name, C.c_double) for name in ("x", "y", "width", "height")]

    rsvg = C.CDLL(ctypes.util.find_library("rsvg-2"))
    cairo = C.CDLL(ctypes.util.find_library("cairo"))
    gobject = C.CDLL(ctypes.util.find_library("gobject-2.0"))
    rsvg.rsvg_handle_new_from_file.argtypes = [C.c_char_p, C.POINTER(C.c_void_p)]
    rsvg.rsvg_handle_new_from_file.restype = C.c_void_p
    rsvg.rsvg_handle_render_document.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(Rectangle), C.POINTER(C.c_void_p)]
    rsvg.rsvg_handle_render_document.restype = C.c_int
    cairo.cairo_image_surface_create.argtypes = [C.c_int, C.c_int, C.c_int]
    cairo.cairo_image_surface_create.restype = C.c_void_p
    cairo.cairo_create.argtypes = [C.c_void_p]
    cairo.cairo_create.restype = C.c_void_p
    cairo.cairo_surface_write_to_png.argtypes = [C.c_void_p, C.c_char_p]
    cairo.cairo_surface_write_to_png.restype = C.c_int
    cairo.cairo_destroy.argtypes = [C.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [C.c_void_p]
    gobject.g_object_unref.argtypes = [C.c_void_p]
    error = C.c_void_p()
    handle = rsvg.rsvg_handle_new_from_file(str(source).encode(), C.byref(error))
    if not handle:
        raise RuntimeError(f"Cannot load {source.name}")
    surface = cairo.cairo_image_surface_create(0, WIDTH, HEIGHT)
    context = cairo.cairo_create(surface)
    ok = rsvg.rsvg_handle_render_document(handle, context, C.byref(Rectangle(0, 0, WIDTH, HEIGHT)), C.byref(error))
    status = cairo.cairo_surface_write_to_png(surface, str(destination).encode()) if ok else -1
    cairo.cairo_destroy(context)
    cairo.cairo_surface_destroy(surface)
    gobject.g_object_unref(handle)
    if status:
        raise RuntimeError(f"Cannot render {source.name}: {status}")


def main():
    baseline = STUDY / "runs/reference-remix/baseline/card.png"
    candidate = STUDY / "runs/reference-remix/with-skill/card.png"
    slides = [
        ("Follow a question.", [
            text("Make something worth keeping.", 50, 225, 43, "#d5e953"),
            text("Knackset / creative field kit", 50, 308, 27),
            text("A preview built from work you can inspect.", 50, 370, 25),
        ]),
        ("Start with actual material.", [
            text("A question with conflicting evidence.", 50, 200, 31),
            text("References that need an original direction.", 50, 270, 31),
            text("A stalled project that needs one useful proof.", 50, 340, 31),
            text("Rabbit Hole / Reference Remix / Unstick Project", 50, 425, 23, "#d5e953"),
        ]),
        ("Same brief. Two finished cards.", [
            text("Without the Knackset skill", 40, 165, 23),
            text("With Reference Remix", 505, 165, 23),
            image(baseline, 35, 195, 440, 231),
            image(candidate, 485, 195, 440, 231),
            text("Both outputs and their decisions are retained.", 40, 472, 22),
        ]),
        ("Ask what the evidence measures.", [
            text("Passing helper tests checks the tools.", 50, 200, 31),
            text("An older mail study checks its own tasks.", 50, 270, 31),
            text("Creative usefulness needs creative-task evidence.", 50, 340, 29, "#d5e953"),
            text("Read the investigation and its source trail.", 50, 425, 23),
        ]),
        ("Finish one useful thing.", [
            text("The demo packet exists, with an editable artifact,", 50, 200, 29),
            text("a source trail and a bounded first task.", 50, 250, 29),
            text("The pilot is three pairs on one project's launch work.", 50, 340, 26),
            text("General benefit and outside-user feedback remain open.", 50, 400, 25, "#d5e953"),
        ]),
        ("Bring it a real job.", [
            text("Try one method for twenty minutes.", 50, 205, 35, "#d5e953"),
            text("Tell us what you kept, fixed or discarded.", 50, 280, 29),
            text("github.com/GWeale/knackset", 50, 380, 31),
            text("The field-test guide is linked from the README.", 50, 438, 22),
        ]),
    ]
    frames = []
    for number, (title, body) in enumerate(slides, 1):
        content = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
                   '<rect width="960" height="540" fill="#152a23"/>'
                   '<path d="M40 42H920" stroke="#d5e953" stroke-width="3"/>'
                   + text(title, 40, 112, 39) + ''.join(body)
                   + text(f"KNACKSET / PREVIEW     {number} / 6", 40, 517, 16) + '</svg>')
        source = HERE / f"frame-{number:02}.svg"
        source.write_text(content)
        target = source.with_suffix('.png')
        render(source, target)
        with Image.open(target) as opened:
            frames.append(opened.convert('RGB').quantize(colors=128))
    frames[0].save(HERE / 'creative-preview.gif', save_all=True, append_images=frames[1:],
                   duration=DURATIONS, loop=0, disposal=2, optimize=False)
    with Image.open(HERE / 'creative-preview.gif') as saved:
        actual = []
        for index in range(saved.n_frames):
            saved.seek(index)
            saved.load()
            actual.append(saved.info['duration'])
        if saved.size != (WIDTH, HEIGHT) or actual != DURATIONS:
            raise RuntimeError('Saved deck differs from the six-frame, 80-second plan')
    print('Built six 960×540 frames and a verified 80-second captioned GIF.')


if __name__ == '__main__':
    main()
