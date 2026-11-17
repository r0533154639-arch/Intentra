# Phase 1 gestures

The approved mapping is implemented by `desktop/src/gestures/gesture_detector.py`:

- Brief pinch and release: single click, delayed until the double-click interval expires.
- Two brief pinches within the configured interval: one double-click.
- Sustained pinch without significant movement: right-click on release.
- Pinch with gradual movement: continuous precise scroll while pinched.
- Pinch with fast wrist movement: one fast scroll on release.

The detector uses explicit idle, pinch, hold, precise-scroll, fast-scroll,
released, and cooldown states. A gesture is classified once; a fast-scroll
candidate cannot also trigger a click or right-click. Timing, movement,
jitter, acceleration, and speed thresholds are user-configurable because
the specification requires these values to be calibrated on target hardware.
Zero placeholder thresholds intentionally keep gesture control disabled.
