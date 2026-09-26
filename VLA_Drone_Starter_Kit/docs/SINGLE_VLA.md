# Single VLA mission research implementation

The expanded [Lab 11](../labs/11_mission_manager.md) separates offline manager replay from SITL integration. [Lab 12](../labs/12_unified_vla.md) defines data, loss, integration and complete-mission evaluation milestones. These remain assignments; the updated workbook does not claim their implementations are supplied.

The final target uses one learned model to monitor an ordinary survey,
choose a detour, generate local inspection movements, analyse visible litter,
propose a map record and request resumption. It has one shared visual/language
backbone with event, grounding, semantic and continuous-action outputs.

The mission manager, geometry, map association and command supervisor are
ordinary software. They retain route progress and validate execution. The
existing autopilot maintains stable flight. The target system has no second
VLM planner or external learned detector. A separate detector can be used in
the classical comparator and clearly labelled offline annotation work.

## What this package implements

- `litterlab/`: the executed teaching simulator and tiny movement learner.
- `integration/`: movement-only SmolVLA integration and PX4/Gazebo exercises,
  subject to the validation limitations in `VALIDATION.md`.
- `templates/single_vla/`: illustrative input, proposal and supervision records.

The package does **not** implement the final shared mission heads, their joint
trainer, the mission manager or a complete learned survey. The existing
`integration.train_smolvla` command trains the movement pilot only. The 210
bundled episodes contain local centring skills, not mission decisions.

## Build in this order

1. Reproduce Labs 1–5, then integrate the simulator and complete the classical
   mission using Labs 6–8 and the related guide chapters.
2. Follow Lab 11 to implement `mission_manager.py`. Replay explicit proposals
   before connecting any learned event head. Test duplicated events, expired
   commands, target loss and interruption during map commit.
3. Run the movement pilot in Labs 9–10. This does not complete the thesis model.
4. Collect complete mission demonstrations and implement the Lab 12 dataset,
   shared heads, masked losses and closed-loop mission evaluation.
5. Validate on Orin with real-time SITL, then progress through the guide's real
   transfer stages under the lab's flight procedure.

## Proposed event interface

- `CONTINUE`: ordinary survey in SURVEY, bounded action in INSPECT.
- `DETOUR`: request an image-grounded candidate, save progress and start inspection.
- `ANALYSE`: enter a validated hold to assess evidence.
- `MORE_VIEW`: return from analysis to bounded inspection.
- `MARK`: commit an evidence-linked semantic record and projected location.
- `RESUME`: close the inspection and rejoin unfinished coverage.
- `HOLD`: request the validated hold response.

Tag proposals with event, observation and context IDs, a task epoch and expiry.
The manager logs both the proposed and accepted event and every rejection or
override. MARK is idempotent. In ANALYSE, MARK commits once and leaves the
inspection active until a subsequent RESUME or MORE_VIEW request.

## Training rules

Train event classification, region grounding and semantic labels from the same
shared representations as the movement policy. Use the model's native flow
matching objective for continuous inspection actions. Normalise each loss by
the valid labels in its batch; a head with no valid labels contributes zero.
Survey route commands do not train the inspection-action head.

Split complete missions, layouts and collection sessions before sampling.
Exclude surveyed coordinates, future evidence and evaluator-only outcomes
from deployed inputs. Keep instructions and mission context meaningful through
paired examples and intervention tests. Never report replay accuracy as flight
success.

## Minimum comparisons

- B0: tuned classical detector, decision rules and inspection.
- B1: the unified model's perception, semantic and movement heads with fixed
  event-selection rules.
- U: the complete unified model with learned mission events.
- U without context: a focused coverage/history ablation.

Keep geometry, map association, flight limits, survey route and mission clock
consistent. Include detour cost, analysis holds, resumption failures and all
interventions. A paper requires a novel, evidenced contribution beyond a
working demonstration; see the guide's publication chapter.
