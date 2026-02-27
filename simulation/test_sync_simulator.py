#!/usr/bin/env python3
from __future__ import annotations

from typing import Tuple

from simulation.sync_simulator import StandardSim, AppOrchestratorSim, StdState, TraceLogger


Preset = Tuple[int, int, int]


def run_scenario(
    name: str,
    tgt: Preset,
    inject_desync: bool = False,
    inject_drop_telemetry: bool = False,
    inject_comm_timeout: bool = False,
) -> bool:
    trace_path = f"test-artifacts/logs/{name}.jsonl"
    trace = TraceLogger(trace_path)

    left = StandardSim("L", speed_mm_s=200, trace=trace)
    right = StandardSim("R", speed_mm_s=200, trace=trace)
    app = AppOrchestratorSim(left, right, trace=trace)

    app.set_preset_targets(tgt, tgt)

    if inject_desync:
        right.freeze_axis = 2

    if inject_drop_telemetry:
        right.drop_telemetry = True

    tick_ms = 50
    max_ticks = 400

    ok = False
    for _ in range(max_ticks):
        if not inject_comm_timeout:
            app.keepalive()

        left.tick(tick_ms)
        right.tick(tick_ms)

        tL = left.telemetry()
        tR = right.telemetry()

        if tL is None or tR is None:
            ok = inject_drop_telemetry
            app.stop_all("telemetry_timeout")
            break

        if tL.state == StdState.fault or tR.state == StdState.fault:
            ok = inject_comm_timeout
            app.stop_all("device_fault")
            break

        if not app.check_sync(tL, tR):
            ok = inject_desync
            app.stop_all("desync")
            break

        if tL.state == StdState.idle_ready and tR.state == StdState.idle_ready:
            ok = not (inject_desync or inject_drop_telemetry or inject_comm_timeout)
            break

    trace.log({"kind": "scenario_result", "name": name, "pass": ok})
    trace.close()
    return ok


def main() -> int:
    preset = (380, 690, 910)

    results = {
        "happy_path": run_scenario("happy_path", preset),
        "desync_stop": run_scenario("desync_stop", preset, inject_desync=True),
        "telemetry_drop_stop": run_scenario("telemetry_drop_stop", preset, inject_drop_telemetry=True),
        "comm_timeout_stop": run_scenario("comm_timeout_stop", preset, inject_comm_timeout=True),
    }

    for k, v in results.items():
        print(f"{k}: {'pass' if v else 'fail'}")

    if all(results.values()):
        print("all cases passed")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
