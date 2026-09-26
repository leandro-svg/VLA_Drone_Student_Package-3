# Illustrative mission records

These files are schema examples with invented values, not flight recordings or
training data. They show the intended boundaries for Labs 11 and 12.

- `observation.json`: image reference and deployable mission context.
- `proposal.json`: one DETOUR request referring to that observation.
- `supervision.json`: labels and validity masks for that survey sample.

The image reference is deliberately illustrative and does not resolve to a
bundled image. Replace these values with actual recorded inputs and annotations.
Store physical item truth and future outcomes in a separate evaluator file.

Use integer task epochs to invalidate old work after mode changes. Compute
expiry against the recorded monotonic capture clock, including preprocessing
and inference delay. Do not infer time synchronisation from field names alone.

On DETOUR acceptance, snapshot route version, segment index, along-segment
progress and the measured coverage bitmap. The small coverage summary supplied
to the model does not replace the manager's complete coverage record. On MARK,
associate the predicted region with the capture pose and camera calibration;
do not interpret predicted semantic text as metric coordinates.
