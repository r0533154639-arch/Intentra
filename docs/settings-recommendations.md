# Recommended gaze and gesture settings

These recommendations are applied when an account has no saved settings yet.
They do not overwrite existing account settings. Existing users can enter and
save the recommended values on the Settings page if they want to adopt them.
Gesture and gaze calibration remain specific to the user's camera and setup.
“Previous” values below refer to the configuration snapshot originally reviewed,
not any later manual edits to an account. The recommended preset applies only
when no settings have been saved.

## Changed values

| Setting | Previous | Recommended | Reason |
| --- | ---: | ---: | --- |
| Cursor smoothing | 0.85 | 0.90 | A larger value lowers the adaptive filter's low-speed cutoff, stabilizing fixation; a speed-responsive cutoff keeps larger gaze movements responsive. A short median filter also rejects isolated prediction spikes. |
| Pinch threshold | 0.10 | 0.20 | Pinch distance is normalized by palm size and recognized when it is at or below this threshold. The observed intentional pinches around 0.138–0.182 were rejected at 0.10; 0.20 admits those measured values while remaining below the approximately 0.25+ readings in the supplied log. |
| Short-pinch maximum | 200 ms | 300 ms | A pinch up to this duration is treated as a click candidate. The wider window tolerates slower natural pinching; the existing 400 ms double-click interval still delays a single click to distinguish it from a double-click. |
| Right-click hold | 600 ms | 650 ms | Keeps right-click distinct from the longer 300 ms click window and requires an intentional hold. |
| Jitter threshold | 0.001 | 0.002 | Hand-position changes smaller than this amount are discarded. A small increase filters more landmark noise before it can affect movement classification. |

## Reviewed but unchanged

| Setting | Value | Reason |
| --- | ---: | --- |
| Cursor sensitivity | 0.6 | Sensitivity scales gaze displacement around the screen center; lowering it further would shrink the usable cursor range. Calibration quality and robust filtering are better ways to address inaccuracy and jitter. |
| Double-click interval | 400 ms | Retaining the existing interval preserves a comfortable window for the second pinch and avoids making double-clicks harder to perform. |
| Movement threshold | 0.1 | This is the calibrated hand-travel distance used to classify precise scrolling and to reject movement during a right-click. Changing it could shift the boundary between those gestures. |
| Precise-scroll sensitivity | 100 | Unchanged as requested. |
| Movement smoothing | 0.4 | Unchanged as requested. |
| Maximum scroll speed | 10 | Unchanged as requested. |
| Fast-scroll threshold | 1.5 | Unchanged as requested. |
| Fast-scroll acceleration threshold | 10 | Unchanged as requested. |
| Fast-scroll duration | 300 ms | Unchanged as requested. |
| Fast-scroll intensity | 2 | Unchanged as requested. |

The pinch and movement thresholds are starting points, not substitutes for
testing with the target camera. If pinches trigger when the fingers are apart,
lower the pinch threshold slightly; if they are missed, raise it in small steps.

The desktop gaze estimator uses a robust, feature-normalized calibration fit and
a time-aware adaptive filter. Existing calibration coefficients remain
compatible, but users should redo the nine-point calibration after updating for
the best accuracy, capturing each point only while gaze is steady.

## Nine-point calibration procedure

1. Sit about 50-70 cm from the camera. This is the practical balance for
   current webcams: the face and both irises remain visible, while the eyes
   occupy enough pixels for stable localization.
2. Position the camera near the top of the screen and level with the eyes.
   Keep the face roughly centered, with even lighting and no strong backlight.
3. Keep the head comfortably straight but allow small natural movements after
   calibration. Do not turn the face or move dramatically during a capture.
4. Look at each red target for 1-2 seconds before pressing Space. This is long
   enough to collect 15 stable frames and long enough to resist one-frame noise.
5. Capture is rejected if the 15-frame iris features vary beyond the stability
   threshold. The application instructs the user to repeat that target.
6. The calibration uses median feature extraction and robust fitting to limit
   the effect of an outlier frame or point.

The 50-70 cm range should be repeated for normal use. A shorter distance can
partially crop the face and reduce head-movement tolerance. A longer distance
reduces eye and iris pixel resolution and can make small gaze changes
indistinguishable from noise. The current webcam implementation does not
provide calibration accuracy measurements from real human subjects, so
objective eye-gaze accuracy should be validated per user and display.

## Implementation and validation summary

- Gaze features are now compensation-adjusted for head roll before normalized
  mapping. Closed or partially visible eyes are not used as gaze samples.
- Calibration uses feature normalization and robust, residual-weighted fitting.
- Live gaze uses a three-frame median plus a time-aware adaptive filter.
- Hand tracking does not issue a gesture when hand observations disappear.
- Camera capture requests 640x480 at 30 FPS and uses DirectShow on Windows.
- The desktop and server suites pass, and the web application builds.
- Remaining hardware-dependent limitations include eye-occlusion handling,
  extreme pose/head movement, low-light accuracy, and sub-display accuracy.
