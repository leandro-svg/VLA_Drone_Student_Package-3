# Lab 11 Build reliable detours and resumption

**Where:** Mac for milestone A; validated SITL bridge for B. **Before starting:** Lab 5 for A; Lab 8B for B. **Theory:** guide pages 35–42. **Status:** research implementation assignment.

## Goal

Build ordinary software that preserves unfinished coverage, validates proposed events and resumes correctly after inspection. Begin with scripted proposals so model errors cannot hide manager errors.

## Predict before implementing

A MARK request commits a map entry, then the process crashes before RESUME. What must be stored so restarting and replaying the same request cannot create a second entry or skip survey ground? Why is category alone an insufficient object identity?

## Milestone A Implement a replayable manager

Create a new module such as `mission_manager.py`. These are proposed interfaces, not supplied functions:

```python
result = manager.accept_or_reject(proposal, observation, now)
# result: accepted event, next state, execution request, reason
snapshot = manager.snapshot()
manager = MissionManager.restore(snapshot)
```

Use a fake clock in tests. Store route version, segment index, progress within the segment, measured coverage, active candidate, map records, context version and task epoch. Include the accepted-event results needed for duplicate handling. Keep actual flight execution outside this module.

## Define the transition contract

| State | Request | Accepted effect |
| --- | --- | --- |
| SURVEY | CONTINUE | Continue the ordinary route |
| SURVEY | DETOUR | Snapshot progress; select an image-grounded candidate; enter INSPECT |
| INSPECT | CONTINUE | Validate a bounded inspection movement |
| INSPECT | ANALYSE | Request a validated hold; enter ANALYSE |
| ANALYSE | MORE_VIEW | Return to INSPECT with the active candidate |
| ANALYSE | MARK | Commit evidence and geometry once; remain in ANALYSE |
| INSPECT or ANALYSE | RESUME | Close inspection; rejoin unfinished coverage; enter SURVEY |
| Any active state | HOLD | Preserve mission progress and request the reviewed hold |

Define recovery out of HOLD explicitly through a validated recovery path. A generic CONTINUE must not accidentally release a fault hold. Define task-epoch increments for mode/task changes and require new proposals to use the current context.

For an already accepted event ID with identical contents, return its stored result without replaying side effects. Reuse of an ID with different contents is an error. For new IDs, validate observation identity, epoch, context, expiry, allowed transition, budget and bounds. Persist the state change, event result and execution intent atomically, then publish a deduplicated execution request.

## Test faults before flight integration

- Replay DETOUR and MARK: unchanged snapshot and one map entry.
- Deliver an old movement after RESUME: rejection, no inspection target restored.
- Interrupt after map commit: restart preserves the entry and unfinished route.
- Use two objects of the same category: separate spatial/evidence identities.
- Detour halfway through a segment: coverage, not merely waypoint index, determines resumption.
- Lose the target, camera or valid pose: defined hold/recovery with reasons.
- Exhaust budget or propose an invalid transition: explicit rejection/override record.

## Milestone B Close the simulator loop

Connect execution requests to the Lab 8B supervisor. Run a scripted survey, detour, inspection, analysis, MARK and explicit RESUME. Verify the actual path and coverage against the saved snapshot. Include timing, rejected events and physical response in the log.

## Completion check

A passes with deterministic replay, restart/fault tests and before/after state records on your Mac. B requires a simulated mission with an evidence-linked map and no skipped unobserved ground. Save a coverage plot. Neither milestone requires a learned event selector yet; report scripted decisions explicitly.

