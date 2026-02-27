"""
Bluetooth le gatt emulator (logical, deterministic)

Purpose
- Emulates a single controller that exposes the SmartJump gatt contract
- Lets app logic and tests interact with it like bluetooth le
- Uses a simulated clock advanced by tick(dt_ms) so tests are deterministic

Payload format: python dicts for prototype simplicity
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Any

@dataclass
class GattEmulator:
    controller_id: str
    state: str = "idle_ready"
    position_in: int = 24
    target_in: int = 24

    heartbeat_timeout_ms: int = 700
    notify_hz_moving: int = 20
    notify_hz_idle: int = 2

    sim_time_ms: int = 0
    last_hb_ms: int = 0
    seq_tx: int = 0
    notify_accum_ms: int = 0

    on_notify: Optional[Callable[[Dict[str, Any]], None]] = None

    def write_command(self, msg: Dict[str, Any]) -> None:
        t = msg.get("type")

        if t == "stop":
            self.state = "idle_ready"
            self.target_in = self.position_in
            self._emit({"type": "ack", "ack": "stop"})
            self._emit_state()
            return

        if t == "set_preset":
            preset = int(msg["preset_in"])
            self.target_in = preset
            self.state = "moving"
            self._emit({"type": "ack", "ack": "set_preset", "target_in": preset})
            return

        if t == "home":
            self.state = "homing"
            self._emit({"type": "ack", "ack": "home"})
            return

        if t == "reset_fault":
            if self.state == "fault":
                self.state = "idle_ready"
                self._emit({"type": "ack", "ack": "reset_fault"})
                self._emit_state()
            return

        self._emit({"type": "fault", "fault": "unknown_command"})

    def write_heartbeat(self, _msg: Optional[Dict[str, Any]] = None) -> None:
        self.last_hb_ms = self.sim_time_ms

    def tick(self, dt_ms: int = 50) -> None:
        self.sim_time_ms += int(dt_ms)

        if self.state == "moving" and (self.sim_time_ms - self.last_hb_ms) > self.heartbeat_timeout_ms:
            self.state = "fault"
            self._emit({"type": "fault", "fault": "heartbeat_timeout"})
            self._emit_state()
            return

        if self.state == "moving":
            step = 1
            if self.position_in < self.target_in:
                self.position_in += step
            elif self.position_in > self.target_in:
                self.position_in -= step
            if self.position_in == self.target_in:
                self.state = "idle_ready"

        if self.state == "homing":
            self.position_in = 0
            self.target_in = 0
            self.state = "idle_ready"

        self.notify_accum_ms += int(dt_ms)
        hz = self.notify_hz_moving if self.state == "moving" else self.notify_hz_idle
        period_ms = max(1, int(1000 / hz))
        if self.notify_accum_ms >= period_ms:
            self.notify_accum_ms = 0
            self._emit_state()

    def _emit_state(self) -> None:
        self._emit(
            {
                "type": "state_update",
                "state": self.state,
                "position_in": self.position_in,
                "target_in": self.target_in,
                "fault": None if self.state != "fault" else "latched",
            }
        )

    def _emit(self, msg: Dict[str, Any]) -> None:
        self.seq_tx += 1
        msg.setdefault("seq", self.seq_tx)
        msg.setdefault("ts_ms", self.sim_time_ms)
        msg.setdefault("controller_id", self.controller_id)
        if self.on_notify:
            self.on_notify(msg)
