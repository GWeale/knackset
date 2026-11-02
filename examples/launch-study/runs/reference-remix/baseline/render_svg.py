#!/usr/bin/env python3
"""Render SVG locally using the installed librsvg and Cairo libraries."""
import ctypes as C
import ctypes.util
import sys
from pathlib import Path

rsvg = C.CDLL(ctypes.util.find_library('rsvg-2'))
cairo = C.CDLL(ctypes.util.find_library('cairo'))
gobject = C.CDLL(ctypes.util.find_library('gobject-2.0'))
class Rectangle(C.Structure):
    _fields_ = [('x', C.c_double), ('y', C.c_double), ('width', C.c_double), ('height', C.c_double)]
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
source, destination, width, height = sys.argv[1:]
width, height = int(width), int(height)
error = C.c_void_p()
handle = rsvg.rsvg_handle_new_from_file(str(Path(source).resolve()).encode(), C.byref(error))
if not handle:
    raise RuntimeError('SVG load failed')
surface = cairo.cairo_image_surface_create(0, width, height)
context = cairo.cairo_create(surface)
if not rsvg.rsvg_handle_render_document(handle, context, C.byref(Rectangle(0, 0, width, height)), C.byref(error)):
    raise RuntimeError('SVG render failed')
status = cairo.cairo_surface_write_to_png(surface, str(Path(destination).resolve()).encode())
cairo.cairo_destroy(context)
cairo.cairo_surface_destroy(surface)
gobject.g_object_unref(handle)
if status:
    raise RuntimeError(f'PNG write failed: {status}')
print(f'{destination}: {width}×{height}, rendered with librsvg/Cairo')
