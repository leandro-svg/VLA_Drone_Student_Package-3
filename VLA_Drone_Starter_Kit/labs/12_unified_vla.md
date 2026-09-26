# Lab 12 Build and evaluate the unified mission model

**Where:** Mac for schema/tests; training workstation and SITL for completion. **Before starting:** Labs 10 and 11B. **Theory:** guide pages 46–56 and 66–68. **Status:** research implementation assignment; shared mission heads are not supplied.

## Goal

Extend one shared model with mission events, candidate grounding and semantic labels alongside inspection actions. Demonstrate that its accepted decisions improve complete missions while preserving coverage and execution constraints.

## Predict before implementing

Can the same visible candidate require different decisions when time is short or it is already mapped? Can an object receive its later close-up label at an earlier ambiguous frame without leaking future evidence? Write paired examples and justify their labels.

## Milestone A Build the mission data contract

Create `mission_dataset.py` with an explicit allowlist of deployable inputs and per-head validity masks. Review `templates/single_vla/` as illustrative records; its image path does not resolve and these examples are not training data. Collect separate complete missions with survey, inspection, analysis, resumption, negative candidates and interruptions.

Split whole missions by layout and collection session before sampling frames. Keep evaluator truth and future outcomes separate. Record the observation, task epoch, context version, calibration, proposed event, accepted event and override reason. Include ambiguous labels as unknown where visible evidence is insufficient.

## Milestone B Add heads and prove the losses work

Create `unified_policy.py` around one shared backbone. Return event logits, one grounded region, semantic outputs and an inspection action when enabled. Define the units, vocabularies, shapes and validity of every output before training.

Create `train_unified.py` with event classification, region and semantic losses plus the native flow-matching action objective. Normalise each head's loss by its valid labels. A head with no valid examples contributes zero; select valid rows before computing its loss so missing/NaN labels cannot contaminate the batch. Ordinary survey-route commands do not train the inspection-action head.

Test masked labels, all-empty masks, padded dimensions and gradients through shared features. Overfit 10–20 reviewed snippets first, retaining a movement regression check. This milestone diagnoses implementation; it does not measure unseen mission success.

## Milestone C Integrate proposals with the manager

Create `evaluate_mission.py` around the Lab 11 manager and Lab 8 bridge. Keep model proposals, accepted events, execution and observed coverage in separate log fields. Allow MARK only with valid evidence and a geometric location from calibration and capture pose. Keep one consistent event per accepted proposal and log every fallback.

Test paired inputs: change the requested category, remaining budget or mapped-object history while holding the image fixed. Use examples whose expert decision should change, and examples whose decision should remain stable. Record both expected and actual outputs.

## Milestone D Compare complete systems

| Condition | Purpose |
| --- | --- |
| B0 | Tuned classical detector, fixed decisions and classical movement |
| B1 | Unified learned perception/semantic/action outputs with fixed event rules |
| U | Complete unified model with learned events |
| U without context | Measure the contribution of mission history and coverage inputs |

Hold routes, layouts, mission clock, action limits, geometry, map matching and budgets fixed. Use matched missions containing absent litter, duplicate sightings, two same-class objects, unsuccessful inspections and partial-segment detours.

Declare map matching tolerance and success criteria before final testing. Report map precision/recall, location error, coverage, detour/hold time, resumption failures, invalid proposals, overrides and camera-to-command age. Count failed and timed-out missions. Select on validation missions; evaluate frozen configurations on grouped test missions. Report actual training seeds and uncertainty across missions.

## Completion check and scope

Save the dataset/version contract, shared checkpoint, per-head diagnostics, manager tests, complete mission traces and B0/B1/U comparisons. Passing requires correct simulated execution and resumption on unseen missions. Orin timing and real transfer remain later experiments. If resources stop at an earlier milestone, report that milestone explicitly rather than claiming the unified mission system is complete.

