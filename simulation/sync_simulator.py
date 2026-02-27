#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple, Optional, Any


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


class TraceLogger:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = Path(path) if path else None
        self._fh = None

        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._fh = self.path.open("w", encoding="utf-8")

    def log(self, event: Dict[str, Any]) -> None:
        if not self._fh:
            return
        self._fh.write(json.dumps(event, separators=(",", ":")) + "\n")

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None


class StandardSim:
    def __init__(self, name: str, speed_mm_s: int = 40, trace: Optional[TraceLogger] = None) -> None:
        self.name = name
        self.trace = trace

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

    def _trace(self, kind: str, extra: Dict[str, Any]) -> None:
        if not self.trace:
            return
        base = {
            "ts_ms": self.now_ms,
            "device": self.name,
            "kind": kind,
            "state": self.state.value,
            "fault_code": self.fault_code,
            "pos_mm": self.pos,
            "tgt_mm": self.tgt,
        }
        base.update(extra)
        self.trace.log(base)

    def receive_cmd(self, cmd: str, payload: Dict) -> None:
        self.last_cmd_ms = self.now_ms
        self._trace("cmd_rx", {"cmd": cmd, "payload": payload})

        if cmd == "keepalive":
            return

        if cmd == "stop":
            self.state = StdState.idle_ready if self.state != StdState.fault else StdState.fault
            self._trace("stop_applied", {})
            return

        if self.state in (StdState.fault, StdState.estop):
            return

        if cmd == "set_targets":
            self.tgt = list(payload["tgt_mm"])
            self.state = StdState.moving
            self._trace("motion_start", {})

    def tick(self, dt_ms: int) -> None:
        self.now_ms += dt_ms

        if self.state != StdState.moving:
            return

        if self.now_ms - self.last_cmd_ms > self.comm_timeout_ms:
            self.state = StdState.fault
            self.fault_code = 5
            self._trace("fault", {"reason": "comm_timeout"})
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
            self._trace("motion_complete", {})

    def telemetry(self) -> Optional[Telemetry]:
        if self.drop_telemetry:
            self._trace("telemetry_drop", {})
            return None

        t = Telemetry(
            ts_ms=self.now_ms,
            state=self.state,
            fault_code=self.fault_code,
            pos_mm=(self.pos[0], self.pos[1], self.pos[2]),
            tgt_mm=(self.tgt[0], self.tgt[1], self.tgt[2]),
        )
        self._trace("telemetry", {"telemetry": {
            "state": t.state.value,
            "fault_code": t.fault_code,
            "pos_mm": list(t.pos_mm),
            "tgt_mm": list(t.tgt_mm),
        }})
        return t


class AppOrchestratorSim:
    def __init__(self, left: StandardSim, right: StandardSim, trace: Optional[TraceLogger] = None) -> None:
        self.left = left
        self.right = right
        self.trace = trace
        self.desync_tol_mm = 8

    def _trace(self, kind: str, extra: Dict[str, Any]) -> None:
        if not self.trace:
            return
        base = {"ts_ms": self.left.now_ms, "kind": kind}
        base.update(extra)
        self.trace.log(base)

    def set_preset_targets(self, tgt_left: Tuple[int, int, int], tgt_right: Tuple[int, int, int]) -> None:
        self._trace("app_set_targets", {"left": list(tgt_left), "right": list(tgt_right)})
        self.left.receive_cmd("set_targets", {"tgt_mm": tgt_left})
        self.right.receive_cmd("set_targets", {"tgt_mm": tgt_right})

    def stop_all(self, reason: str = "app_stop") -> None:
        self._trace("app_stop_all", {"reason": reason})
        self.left.receive_cmd("stop", {})
        self.right.receive_cmd("stop", {})

    def keepalive(self) -> None:
        self.left.receive_cmd("keepalive", {})
        self.right.receive_cmd("keepalive", {})

    def check_sync(self, tL: Telemetry, tR: Telemetry) -> bool:
        delta = abs(tL.pos_mm[2] - tR.pos_mm[2])
        ok = delta <= self.desync_tol_mm
        if not ok:
            self._trace("desync", {"delta_mm": delta, "tol_mm": self.desync_tol_mm})
        return ok
