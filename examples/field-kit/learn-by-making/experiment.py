#!/usr/bin/env python3
"""A complete standard-library quadratic Bezier experiment. Python 3.10+."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

P0 = (0.0, 0.0)
P2 = (300.0, 0.0)
SAMPLES = (0.0, 0.25, 0.5, 0.75, 1.0)


def curve(t, control):
    """A quadratic Bezier: weights add to 1 for every t from 0 to 1."""
    return tuple((1-t)**2 * a + 2*(1-t)*t * c + t**2 * b
                 for a, c, b in zip(P0, control, P2))


def summarize(control):
    # For these endpoint heights, y(t) = 2*C_y*t*(1-t).
    # Its exact maximum is C_y/2 at t=0.5 (C_y is nonnegative).
    points = [curve(t, control) for t in SAMPLES]
    assert curve(0, control) == P0 and curve(1, control) == P2
    return {
        "control": control,
        "midpoint_at_t_0_5": curve(0.5, control),
        "exact_maximum_height": control[1] / 2,
        "sample_parameters": SAMPLES,
        "sample_points": points,
    }


def panel(left, control, heading):
    # Mathematical y increases upward. SVG y increases downward.
    def screen(point):
        return left + 52 + point[0], 394 - point[1]

    def pair(point):
        x, y = screen(point)
        return f"{x:g},{y:g}"

    cx, cy = screen(control)
    mx, my = screen(curve(0.5, control))
    dots = "".join(f'<circle cx="{screen(p)[0]:g}" '
                   f'cy="{screen(p)[1]:g}" r="4"/>'
                   for p in (curve(t, control) for t in SAMPLES))
    return f'''
    <g>
      <rect x="{left}" y="101" width="404" height="390" rx="10" fill="#ffffff"/>
      <text x="{left+22}" y="133" class="panel-title">{heading}</text>
      <text x="{left+22}" y="156" class="small">Control C = ({control[0]:g}, {control[1]:g})</text>
      <path d="M{pair(P0)} L{pair(P2)}" class="baseline"/>
      <path d="M{pair(P0)} L{pair(control)} L{pair(P2)}" class="polygon"/>
      <path d="M{pair(P0)} Q{pair(control)} {pair(P2)}" class="curve"/>
      <g class="samples">{dots}</g>
      <rect x="{cx-5:g}" y="{cy-5:g}" width="10" height="10" class="control"/>
      <text x="{cx:g}" y="{cy-15:g}" text-anchor="middle" class="label">C</text>
      <circle cx="{mx:g}" cy="{my:g}" r="6" class="midpoint"/>
      <text x="{mx:g}" y="{my+26:g}" text-anchor="middle" class="label">t = 0.5: ({curve(.5, control)[0]:g}, {curve(.5, control)[1]:g})</text>
      <text x="{left+52}" y="426" text-anchor="middle" class="label">P0</text>
      <text x="{left+52}" y="447" text-anchor="middle" class="small">(0, 0)</text>
      <text x="{left+352}" y="426" text-anchor="middle" class="label">P2</text>
      <text x="{left+352}" y="447" text-anchor="middle" class="small">(300, 0)</text>
      <text x="{left+22}" y="477" class="small">Maximum height: {control[1]/2:g}</text>
    </g>'''


def svg_document(first, changed, transfer):
    mx, my = curve(.5, transfer)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="680" viewBox="0 0 900 680" role="img" aria-labelledby="title description">
  <title id="title">A control point pulls a curve; it is not a stop</title>
  <desc id="description">Two quadratic Bezier curves share endpoints (0,0) and (300,0). Only the control point height changes. Control heights {first[1]:g} and {changed[1]:g} give midpoint heights {first[1]/2:g} and {changed[1]/2:g}. Squares are controls; circles lie on the curves.</desc>
  <style>
    text {{font-family: sans-serif; fill: #172d39;}}
    .panel-title {{font-size: 18px; font-weight: bold;}}
    .label {{font-size: 15px;}} .small {{font-size: 14px;}}
    .baseline {{fill: none; stroke: #b5c0c7; stroke-width: 1;}}
    .polygon {{fill: none; stroke: #986321; stroke-width: 1.5; stroke-dasharray: 5 5;}}
    .curve {{fill: none; stroke: #156b86; stroke-width: 4;}}
    .samples {{fill: white; stroke: #156b86; stroke-width: 2;}}
    .control {{fill: #f7dcab; stroke: #986321; stroke-width: 2;}}
    .midpoint {{fill: #d96135; stroke: white; stroke-width: 2;}}
  </style>
  <rect width="900" height="680" fill="#edf2f4"/>
  <text x="30" y="42" font-size="25" font-weight="bold">A control point pulls. It is not a stop.</text>
  <text x="30" y="72" font-size="15">Same endpoints. Same scale. Change only the control height.</text>
{panel(30, first, '1. First curve')}
{panel(466, changed, '2. Change the control height')}
  <rect x="30" y="512" width="840" height="134" rx="10" fill="#172d39"/>
  <g style="fill: #ffffff">
    <text x="52" y="544" style="fill: #ffffff; font-size: 17px">At t = 0.5: 25% P0 + 50% C + 25% P2</text>
    <text x="52" y="574" style="fill: #ffffff; font-size: 15px">Sideways case: C = ({transfer[0]:g}, {transfer[1]:g}) gives midpoint ({mx:g}, {my:g}).</text>
    <text x="52" y="601" style="fill: #ffffff; font-size: 15px">Square = control. Circles = curve samples. Orange = t = 0.5.</text>
    <text x="52" y="628" style="fill: #ffffff; font-size: 14px">Coordinates shown use y upward; drawing converts to SVG's y downward.</text>
  </g>
</svg>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-height", type=int, default=200)
    parser.add_argument("--compare-height", type=int, default=100)
    parser.add_argument("--transfer-x", type=int, default=240)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    if not (40 <= args.control_height <= 200 and 40 <= args.compare_height <= 200):
        parser.error("heights must be 40..200 to keep this fixed-scale drawing readable")
    if not 0 <= args.transfer_x <= 300:
        parser.error("transfer-x must be 0..300")
    first = (150.0, float(args.control_height))
    changed = (150.0, float(args.compare_height))
    transfer = (float(args.transfer_x), first[1])
    results = {"endpoints": [P0, P2], "first": summarize(first),
               "changed_height": summarize(changed), "sideways_transfer": summarize(transfer),
               "boundary_control_on_line": summarize((150.0, 0.0))}
    svg = svg_document(first, changed, transfer)
    ET.fromstring(svg)  # A malformed SVG is a setup failure, not a lesson.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "bezier-experiment.svg").write_text(svg, encoding="utf-8")
    (args.output_dir / "results.json").write_text(json.dumps(results, indent=2)+"\n", encoding="utf-8")
    for name in ("first", "changed_height", "sideways_transfer", "boundary_control_on_line"):
        case = results[name]
        print(f"{name}: C={case['control']}; midpoint={case['midpoint_at_t_0_5']}; maximum height={case['exact_maximum_height']:g}")
    print("Endpoints fixed in all four cases: (0, 0), (300, 0).")
    print("Saved bezier-experiment.svg and results.json; SVG XML parses successfully.")


if __name__ == "__main__":
    main()
