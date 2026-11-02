# Complete experiment: a control point is not a required stop

The question is whether a curve must pass through its control point. This small experiment fixes two endpoints and changes only the height of one quadratic Bézier control. The generating script and SVG are complete; no learner response is needed to receive or run them.

## Run, inspect, change, reset

From the repository root, run:

```sh
python3 examples/field-kit/learn-by-making/experiment.py
```

Open `bezier-experiment.svg` in an SVG viewer when available. Both panels share endpoints and scale. Blue is the curve, the gold square is its control, and circles are calculated curve samples. Orange marks t = 0.5. The SVG uses a native quadratic `Q` path; the Python formula independently supplies the sample positions. The file uses no external assets.

Read the small `curve()` function first. `panel()` is just drawing and labeling. The inputs and five sample parameters are visible near the top; there is no randomness, external state or account.

For one small change, lower only the comparison height from 100 to 60:

```sh
python3 examples/field-kit/learn-by-making/experiment.py --compare-height 60
```

Predict before running: should the orange comparison point move to height 60 or 30? This is an optional prompt for your own later use, not an answer attributed to you. Compare `changed_height` in the new output to the saved baseline transcript below. The drawing keeps the same endpoints and scale. Re-running the first command resets all outputs to their original inputs. Outputs are overwritten in the script's directory; `--output-dir PATH` preserves a separate variation if desired. Plot height controls are deliberately limited to 40–200 so labels stay within this small fixed layout.

## What was actually run

The command above was executed locally with Python and exited successfully. Its final observed output was:

```text
first: C=(150.0, 200.0); midpoint=(150.0, 100.0); maximum height=100
changed_height: C=(150.0, 100.0); midpoint=(150.0, 50.0); maximum height=50
sideways_transfer: C=(240.0, 200.0); midpoint=(195.0, 100.0); maximum height=100
boundary_control_on_line: C=(150.0, 0.0); midpoint=(150.0, 0.0); maximum height=0
Endpoints fixed in all four cases: (0, 0), (300, 0).
Saved bezier-experiment.svg and results.json; SVG XML parses successfully.
```

`results.json` preserves each control, both endpoints, the five sample parameters and their calculated coordinates. `predictions.md` records the assistant's predictions before the corresponding execution; they matched these results. These are demonstrations, not observations of a learner's understanding. No SVG rendering or visual inspection was performed; only the generated XML was parsed.

## Why the result looks different from “pass through C”

For each coordinate, the exact quadratic rule is:

```text
B(t) = (1-t)^2 P0 + 2(1-t)t C + t^2 P2, for 0 ≤ t ≤ 1
```

At t = 0 and t = 1, the weights force the curve onto P0 and P2. At t = 0.5 the weights are 1/4, 1/2, 1/4. Therefore the first example gives:

```text
x = 1/4*0 + 1/2*150 + 1/4*300 = 150
y = 1/4*0 + 1/2*200 + 1/4*0   = 100
```

The control is weighted halfway; it is not an endpoint the curve must visit. Lowering C's height to 100 lowers that y to 50. A useful mental model is that C pulls the bend toward itself. “Pulls” is a metaphor; the weighted-coordinate equation is the actual rule.

For these endpoint heights, every point satisfies `y(t) = 2*C_y*t*(1-t)`. The factor `t*(1-t)` has a maximum of 1/4 at t = 0.5, so the exact maximum height is `C_y/2`. This is an algebraic bound, not a conclusion drawn from five sample dots. With C at height 200 the entire curve stays at or below height 100: it cannot reach C anywhere. The naïve model would require it to reach 200 and is contradicted by this example.

Moving C sideways to (240, 200) changes the t = 0.5 x to 195 but leaves the same height rule. Here “midpoint” means the halfway parameter t = 0.5; it does not promise half the length along an asymmetric curve.

The boundary result matters: if C = (150, 0), it lies on the straight curve and equals its t = 0.5 point. A control **need not** lie on a curve; it is not forbidden from doing so. The half-height rule in this experiment relies on both endpoint heights being zero; for arbitrary endpoints use the full equation.

## One nearby transfer challenge

After the complete example, optionally predict the t = 0.5 point when C moves left to (60, 200), then run:

```sh
python3 examples/field-kit/learn-by-making/experiment.py --transfer-x 60
```

Check `sideways_transfer` in the command output or JSON. Use the 1/4, 1/2, 1/4 weights to explain both coordinates. This challenge has not been run or answered for you here. One successful run would demonstrate the artifact, not establish your mastery.

## Parent follow-up

The parent independently reran the unchanged Python script, matched the saved
SVG and results, then rendered and inspected the SVG at 900 × 680 using installed
librsvg/cairo. That visual check found no clipped labels or overlap. The author’s
execution account above is retained; this later inspection is separate.
