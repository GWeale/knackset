# Demonstrator predictions — recorded before execution

These are the assistant's predictions, not learner responses. Both endpoints remain P0 = (0, 0), P2 = (300, 0). Coordinates use y upward; the script converts them to SVG's downward y direction only when drawing.

1. With control C = (150, 200), the halfway parameter t = 0.5 should give (150, 100). The control influences the curve; the curve need not pass through it. Because this case is symmetric, the curve's greatest height should be 100, not 200.
2. Change only the control height to 100. The midpoint should become (150, 50), and the greatest height should halve to 50. Endpoints should stay fixed.
3. Nearby transfer: reset the height to 200, then change only control x from 150 to 240. The midpoint should shift to (195, 100). Moving sideways should not change its height or the greatest height.

A “control is a required point on the curve” model predicts a different silhouette for the symmetric first case: it would have to rise to height 200. That is the confusion this experiment distinguishes.

4. Added before running the boundary case: with C = (150, 0), the curve should be a straight segment and its t = 0.5 point should equal C. This guards against replacing “must pass through” with the equally incorrect “never passes through.”
