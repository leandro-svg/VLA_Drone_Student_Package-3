"""SITL position-command exercise for mavsdk==2.8.4. NOT flight tested.

Run only against a local software simulator, with no physical vehicle connected.
This is an integration exercise, not the real aircraft's safety supervisor.
"""
import argparse
import asyncio
import json
import math
import time
from pathlib import Path


async def until(stream, predicate):
    async for item in stream:
        if predicate(item): return item


async def run(out):
    from mavsdk import System
    from mavsdk.offboard import PositionNedYaw
    drone = System()
    await drone.connect(system_address="udp://127.0.0.1:14540")
    await asyncio.wait_for(until(drone.core.connection_state(), lambda x: x.is_connected), 30)
    await asyncio.wait_for(until(drone.telemetry.health(), lambda x: x.is_global_position_ok and x.is_home_position_ok), 60)
    folder = Path(out); folder.mkdir(parents=True, exist_ok=False)
    await drone.telemetry.set_rate_position_velocity_ned(10.)
    armed = False
    try:
        await drone.action.arm(); armed = True
        await drone.offboard.set_position_ned(PositionNedYaw(0., 0., -5., 0.))
        await drone.offboard.start()
        with (folder / "position.jsonl").open("w") as log:
            for north, east in [(0., 0.), (2., 0.), (2., 2.), (0., 2.), (0., 0.)]:
                await drone.offboard.set_position_ned(PositionNedYaw(north, east, -5., 0.))
                # MAVSDK re-sends the setpoint. Never add the delta on each resend.
                reached_since = None
                async def reach():
                    nonlocal reached_since
                    async for pv in drone.telemetry.position_velocity_ned():
                        pos = pv.position; vel = pv.velocity; now = time.monotonic()
                        error = math.sqrt((pos.north_m-north)**2 + (pos.east_m-east)**2 + (pos.down_m+5.)**2)
                        speed = math.sqrt(vel.north_m_s**2 + vel.east_m_s**2 + vel.down_m_s**2)
                        log.write(json.dumps({"host_monotonic_s": now, "north_m": pos.north_m,
                            "east_m": pos.east_m, "down_m": pos.down_m, "target_ne": [north, east], "error_m": error}) + "\n")
                        if error < .25 and speed < .2:
                            reached_since = now if reached_since is None else reached_since
                            if now - reached_since > 1.: return
                        else: reached_since = None
                await asyncio.wait_for(reach(), 30)
    finally:
        if armed:
            # Command LAND directly, then wait for touchdown; no in-air disarm.
            await drone.action.land()
            await asyncio.wait_for(until(drone.telemetry.in_air(), lambda airborne: not airborne), 45)
    print("Square complete; inspect position.jsonl and the PX4 flight log.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sitl", action="store_true")
    ap.add_argument("--out", required=True); args = ap.parse_args()
    if not args.sitl: ap.error("This exercise requires --sitl and an isolated software simulator")
    asyncio.run(run(args.out))
