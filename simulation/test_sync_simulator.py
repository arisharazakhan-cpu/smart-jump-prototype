#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Tuple

from simulation.sync_simulator import StandardSim, AppOrchestratorSim, StdState


Preset = Tuple[int, int, int]


def run_scenario(
    tgt: Preset,
    inject_desync: bool = False,
    inject_drop_telemetry: bool = False,
    inject_comm_timeout: bool = False,
) -> bool:
    left = StandardSim("L", speed_mm_s=200)
    right = StandardSim("R", speed_mm_s=200)
    app = AppOrchestratorSim(left, right)

    app.set_preset_targets(tgt, tgt)

    if inject_desync:
        right.freeze_axis = 2

    if inject_drop_telemetry:
        right.drop_telemetry = True

    tick_ms = 50
    start = time.time()

    while time.time() - start < 8:
        if not inject_comm_timeout:
            app.keepalive()

        left.tick(tick_ms)
        right.tick(tick_ms)

        tL = left.telemetry()
        tR = right.telemetry()

        if tL is None or tR is None:
            return inject_drop_telemetry

        if tL.state == StdState.fault or tR.state == StdState.fault:
            return inject_comm_timeout

        if not app.check_sync(tL, tR):
            return inject_desync

        if tL.state == StdState.idle_ready and tR.state == StdState.idle_ready:
            return not (inject_desync or inject_drop_telemetry or inject_comm_timeout)

        time.sleep(tick_ms / 1000.0)

    return False


def main() -> int:
    preset = (380, 690, 910)

    results = {
        "happy_path": run_scenario(preset),
        "desync_stop": run_scenario(preset, inject_desync=True),
        "telemetry_drop_stop": run_scenario(preset, inject_drop_telemetry=True),
        "comm_timeout_stop": run_scenario(preset, inject_comm_timeout=True),
    }

    for k, v in results.items():
        print(f"{k}: {'pass' if v else 'fail'}")

    if all(results.values()):
        print("all cases passed")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
