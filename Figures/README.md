# Figures for the thesis guide

These are the figures embedded in the illustrated guide. Use PNG files in
Word or slides. SVG files retain editable text, shapes and lines; open them
in a vector editor. Figure 5 is the original raster teaching replay and has
no SVG counterpart. Keep the explanatory captions when reusing figures.
Figure numbers remain stable between editions; Figure 14 shows the newly
specified shared model and therefore appears beside Figure 3 in the guide.

| Figure | Subject | Guide page |
| --- | --- | --- |
| 1 | The litter search mission | 6 |
| 2 | From camera pixels to ground offsets | 10 |
| 3 | One VLA decides and acts | 11 |
| 14 | Inside the single VLA | 12 |
| 4 | Anchor one prediction to one observation | 20 |
| 5 | A recorded teaching episode | 23 |
| 6 | Measured teaching results | 28 |
| 7 | The simulator and flight software loop | 34 |
| 8 | From repeated sightings to object tracks | 42 |
| 9 | Mission labels and information boundaries | 48 |
| 10 | Training one shared model | 54 |
| 11 | One model across mission modes | 61 |
| 12 | The stages of transfer evidence | 65 |
| 13 | Main system and decision comparisons | 68 |

## Evidence and interpretation

Figures 5 and 6 show saved outputs of the bundled NumPy teaching experiment.
Figure 4 uses recorded seed 7 position values with an illustrative timeline.
Other figures are original explanatory schematics or worked examples of the
proposed system. They are not photographs, real-flight results or measured
Orin benchmarks. In Figure 6 the changed-task and no-task interventions are
scored against the original goal, and do not establish general language
understanding. Each bar uses the same 30 teaching starts.

Figure 6 reads `../VLA_Drone_Starter_Kit/examples/tiny_model/history.json`
and the `summary.json` files in `examples/eval_*`. Figure 5 corresponds to
`examples/first_episode/`. Data counts in Figure 9 describe the bundled
teaching split, not a required real-world dataset size.

## Edit or regenerate

Edit copies of the SVG files directly, or edit `regenerate_figures.py`.
With the starter kit Python environment activated, run from this folder:

```sh
python regenerate_figures.py
```

The script uses Pillow and rewrites the thirteen PNG/SVG pairs in this
folder. It leaves Figure 5 unchanged and reads the saved teaching results
from the neighbouring starter kit. It looks for Arial on macOS/Windows or
DejaVu Sans on Linux. Set LITTER_FIGURE_FONT and LITTER_FIGURE_BOLD to paths
to alternative TrueType fonts when necessary. Font substitutions can change
line wrapping, so inspect the outputs before inserting them into a thesis.
The script does not update the Word document automatically.
