#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional


class StdState(Enum):
    idle_ready = "idle_ready"
    moving = "moving"
    fault = "fault"
    estop = "estop"


@dataclass
class Telemetry:
    ts_ms: int
    state: StdState
    fault_code: int
    pos_mm: Tuple[int, int, int]
    tgt_mm: Tuple[int, int, int]


class StandardSim:
    def __init__(self, name: str, speed_mm_s: int = 40) -> None:
        self.name = name
        self.state = StdState.idle_ready
        self.fault_code = 0

        self.pos = [0, 0, 0]
        self.tgt = [0, 0, 0]

        self.speed_mm_s = speed_mm_s

        self.now_ms = 0
        self.last_cmd_ms = 0
        self.comm_timeout_ms = 800

        self.freeze_axis: Optional[int] = None
        self.drop_telemetry = False

    def receive_cmd(self, cmd: str, payload: Dict) -> None:
        self.last_cmd_ms = self.now_ms

        if cmd == "keepalive":
            return

        if cmd == "stop":
            self.state = StdState.idle_ready if self.state != StdState.fault else StdState.fault
            return

        if self.state in (StdState.fault, StdState.estop):
            return

        if cmd == "set_targets":
            self.tgt = list(payload["tgt_mm"])
            self.state = StdState.moving

    def tick(self, dt_ms: int) -> None:
        self.now_ms += dt_ms

        if self.state != StdState.moving:
            return

        if self.now_ms - self.last_cmd_ms > self.comm_timeout_ms:
            self.state = StdState.fault
            self.fault_code = 5
            return

        step = max(1, int(self.speed_mm_s * (dt_ms / 1000.0)))

        for i in range(3):
            if self.freeze_axis == i:
                continue

            if self.pos[i] < self.tgt[i]:
                self.pos[i] = min(self.tgt[i], self.pos[i] + step)
            elif self.pos[i] > self.tgt[i]:
                self.pos[i] = max(self.tgt[i], self.pos[i] - step)

        if tuple(self.pos) == tuple(self.tgt):
            self.state = StdState.idle_ready

    def telemetry(self) -> Optional[Telemetry]:
        if self.drop_telemetry:
            return None

        return Telemetry(
            ts_ms=self.now_ms,
            state=self.state,
            fault_code=self.fault_code,
            pos_mm=(self.pos[0], self.pos[1], self.pos[2]),
            tgt_mm=(self.tgt[0], self.tgt[1], self.tgt[2]),
        )


class AppOrchestratorSim:
    def __init__(self, left: StandardSim, right: StandardSim) -> None:
        self.left = left
        self.right = right
        self.desync_tol_mm = 8

    def set_preset_targets(self, tgt_left: Tuple[int, int, int], tgt_right: Tuple[int, int, int]) -> None:
        self.left.receive_cmd("set_targets", {"tgt_mm": tgt_left})
        self.right.receive_cmd("set_targets", {"tgt_mm": tgt_right})

    def stop_all(self) -> None:
        self.left.receive_cmd("stop", {})
        self.right.receive_cmd("stop", {})

    def keepalive(self) -> None:
        self.left.receive_cmd("keepalive", {})
        self.right.receive_cmd("keepalive", {})

    def check_sync(self, tL: Telemetry, tR: Telemetry) -> bool:
        delta = abs(tL.pos_mm[2] - tR.pos_mm[2])
        return delta <= self.desync_tol_mm
