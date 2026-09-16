from __future__ import annotations

import json
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from ble.gatt_emulator import GattEmulator
from app.orchestrator import Orchestrator
from smartjump.config import MAX_HEIGHT_IN, MIN_HEIGHT_IN, VOICE_CONFIDENCE_THRESHOLD
from smartjump.voice import interpret_voice_command
from smartjump.web_ui import DIGITAL_TWIN_HTML


HTML = r"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Smart Jump UI</title>
    <style>
      :root { color-scheme: dark; }
      body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin: 24px; }
      .wrap { max-width: 980px; margin: 0 auto; }
      .top { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
      .brand { display: flex; align-items: baseline; gap: 12px; }
      .brand h1 { margin: 0; font-size: 22px; letter-spacing: 0.2px; }
      .brand .tag { opacity: 0.8; font-size: 13px; }
      .pill { padding: 8px 12px; border-radius: 999px; display: inline-flex; align-items: center; gap: 8px; font-weight: 650; border: 1px solid rgba(255,255,255,0.14); background: rgba(255,255,255,0.05); }
      .dot { width: 10px; height: 10px; border-radius: 999px; display: inline-block; background: rgba(255,255,255,0.5); }
      .grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-top: 18px; }
      .card { border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 16px; background: rgba(255,255,255,0.04); }
      .row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
      .k { opacity: 0.8; }
      .v { font-weight: 700; }
      .controls { display: grid; gap: 12px; }
      .btns { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
      button { cursor: pointer; border: 1px solid rgba(255,255,255,0.14); background: rgba(255,255,255,0.06); color: white; padding: 10px 12px; border-radius: 12px; font-weight: 700; }
      button:hover { background: rgba(255,255,255,0.10); }
      button.primary { background: rgba(80,140,255,0.25); border-color: rgba(80,140,255,0.45); }
      button.danger { background: rgba(255,80,80,0.22); border-color: rgba(255,80,80,0.45); }
      .slider { display: grid; gap: 8px; }
      input[type="range"] { width: 100%; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New"; font-size: 12px; opacity: 0.95; }
      .banner { margin-top: 12px; padding: 10px 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.14); background: rgba(255,255,255,0.05); }
      .banner.bad { border-color: rgba(255,80,80,0.55); background: rgba(255,80,80,0.10); }
      .small { font-size: 12px; opacity: 0.8; }
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="top">
        <div class="brand">
          <h1>Smart Jump</h1>
          <div class="tag">mounted control ui (simulation)</div>
        </div>
        <div class="pill" id="statusPill">
          <span class="dot" id="statusDot"></span>
          <span id="statusText">loading</span>
        </div>
      </div>

      <div class="grid">
        <div class="card">
          <div class="row">
            <div class="k">Left standard</div>
            <div class="v mono" id="leftLine">...</div>
          </div>
          <div style="height:10px"></div>
          <div class="row">
            <div class="k">Right standard</div>
            <div class="v mono" id="rightLine">...</div>
          </div>

          <div class="banner bad" id="faultBanner" style="display:none;">
            <div class="v">Fault detected: <span class="mono" id="faultReason"></span></div>
            <div class="small">System halted safely.</div>
          </div>

          <div class="banner">
            <div class="k">Last event</div>
            <div class="mono" id="lastEvent">none</div>
          </div>
        </div>

        <div class="card">
          <div class="controls">
            <div class="btns">
              <button class="primary" onclick="preset(24)">24 in</button>
              <button class="primary" onclick="preset(36)">36 in</button>
              <button class="primary" onclick="preset(48)">48 in</button>
              <button class="primary" onclick="preset(60)">60 in</button>
            </div>

            <div class="slider">
              <div class="row">
                <div class="k">Custom preset</div>
                <div class="v mono"><span id="sliderVal">36</span> in</div>
              </div>
              <input id="slider" type="range" min="12" max="72" value="36" step="1" />
              <button onclick="presetFromSlider()">Set custom preset</button>
            </div>

            <div class="row">
              <button class="danger" onclick="stopAll()">Stop</button>
              <button onclick="forceDesync()">Force desync</button>
              <button onclick="resetFault()">Reset</button>
            </div>

            <div class="small">
              Tip: set a preset, then hit force desync while moving to see the safety fault.
            </div>
          </div>
        </div>
      </div>
    </div>

    <script>
      const slider = document.getElementById("slider");
      const sliderVal = document.getElementById("sliderVal");
      slider.addEventListener("input", () => sliderVal.textContent = slider.value);

      async function api(path, body=null) {
        const opts = body ? {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)} : {};
        const res = await fetch(path, opts);
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
      }

      function preset(h) { api("/api/preset", {height_in: h}); }
      function presetFromSlider() { preset(parseInt(slider.value, 10)); }
      function stopAll() { api("/api/stop", {}); }
      function forceDesync() { api("/api/force_desync", {}); }
      function resetFault() { api("/api/reset", {}); }

      function setPill(state) {
        const pill = document.getElementById("statusPill");
        const dot = document.getElementById("statusDot");
        const txt = document.getElementById("statusText");

        txt.textContent = state;

        if (state === "app_fault") {
          pill.style.borderColor = "rgba(255,80,80,0.55)";
          pill.style.background = "rgba(255,80,80,0.10)";
          dot.style.background = "rgba(255,80,80,0.95)";
          return;
        }

        if (state === "app_moving") {
          pill.style.borderColor = "rgba(80,140,255,0.55)";
          pill.style.background = "rgba(80,140,255,0.12)";
          dot.style.background = "rgba(80,140,255,0.95)";
          return;
        }

        pill.style.borderColor = "rgba(120,255,160,0.40)";
        pill.style.background = "rgba(120,255,160,0.10)";
        dot.style.background = "rgba(120,255,160,0.95)";
      }

      async function refresh() {
        const s = await api("/api/state");
        setPill(s.app_state);

        document.getElementById("leftLine").textContent =
          `state=${s.left_state} height=${s.left_pos_in} in`;

        document.getElementById("rightLine").textContent =
          `state=${s.right_state} height=${s.right_pos_in} in`;

        const fb = document.getElementById("faultBanner");
        const fr = document.getElementById("faultReason");
        if (s.app_state === "app_fault" && s.last_fault_reason) {
          fb.style.display = "block";
          fr.textContent = s.last_fault_reason;
        } else {
          fb.style.display = "none";
          fr.textContent = "";
        }

        document.getElementById("lastEvent").textContent =
          s.last_event ? JSON.stringify(s.last_event) : "none";
      }

      setInterval(refresh, 250);
      refresh();
    </script>
  </body>
</html>
"""


class SmartJumpRuntime:
    def __init__(self) -> None:
        self.left = GattEmulator(controller_id="L")
        self.right = GattEmulator(controller_id="R")
        self.app = Orchestrator(self.left, self.right)

        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._events: list[dict] = []
        self._record("System initialized", "system")

    def _record(self, message: str, kind: str = "info") -> None:
        self._events.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "message": message,
                "kind": kind,
            }
        )
        self._events = self._events[-20:]

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while self._running:
            with self._lock:
                if self.app.state != "app_fault":
                    self.app.heartbeat()
                self.app.tick(50)
            time.sleep(0.05)

    def state(self) -> dict:
        with self._lock:
            last_event = self.app.events[-1] if self.app.events else None
            last_fault_reason = None
            if last_event and last_event.get("type") == "app_fault":
                last_fault_reason = last_event.get("reason")

            return {
                "app_state": self.app.state,
                "left_state": self.left.state,
                "right_state": self.right.state,
                "left_pos_in": self.left.position_in,
                "right_pos_in": self.right.position_in,
                "left_target_in": self.left.target_in,
                "right_target_in": self.right.target_in,
                "difference_in": abs(self.left.position_in - self.right.position_in),
                "desync_tolerance_in": self.app.desync_tolerance_in,
                "min_height_in": MIN_HEIGHT_IN,
                "max_height_in": MAX_HEIGHT_IN,
                "controllers_online": True,
                "heartbeat_active": self.app.state != "app_fault",
                "last_event": last_event,
                "last_fault_reason": last_fault_reason,
                "events": list(reversed(self._events[-8:])),
            }

    def set_preset(self, height_in: int) -> None:
        with self._lock:
            self.app.set_preset(int(height_in))
            self._record(f"Movement requested: {int(height_in)} inches", "command")

    def stop(self) -> None:
        with self._lock:
            # Orchestrator stop
            self.app.user_stop()

            # Hard cancel motion at device layer so movement stops immediately
            for dev in (self.left, self.right):
                dev.target_in = dev.position_in
                if dev.state != "fault":
                    dev.state = "idle_ready"
            self._record("Emergency stop accepted", "stop")

    def reset(self) -> None:
        with self._lock:
            # Clear app fault memory
            self.app.events.clear()
            self.app.state = "app_idle"

            # Re-sync positions for a clean demo start state
            avg = int((self.left.position_in + self.right.position_in) / 2)
            for dev in (self.left, self.right):
                dev.position_in = avg
                dev.target_in = avg
                dev.state = "idle_ready"
            self._record("Fault reset; standards re-synchronized", "reset")

    def force_desync(self) -> None:
        with self._lock:
            # Guarantee we're in motion so the demo is repeatable
            if self.app.state != "app_moving":
                # kick off a move far enough away that we have time to inject desync
                target = max(self.left.position_in, self.right.position_in) + 24
                self.app.set_preset(int(target))

            # Inject a desync bigger than any reasonable tolerance
            bump = max(6, int(getattr(self.app, "desync_tolerance_in", 1)) + 5)
            self.left.position_in += bump

            # Force an immediate orchestrator evaluation so the UI updates right away
            # dt_ms=0 means "do not advance motion", but still runs desync checks
            self.app.tick(0)
            self._record("Desynchronization injected for demonstration", "fault")

    def voice(self, transcript: str, confidence: float) -> dict:
        command = interpret_voice_command(transcript)
        with self._lock:
            self._record(f'Voice heard: "{transcript}"', "voice")

        # A stop command is always honored, even with low recognition confidence.
        if command.intent == "stop":
            self.stop()
            return {"ok": True, "intent": "stop", "spoken_reply": "Stopped."}

        if confidence < VOICE_CONFIDENCE_THRESHOLD:
            with self._lock:
                self._record("Voice command rejected: confidence too low", "warning")
            raise ValueError("Voice confidence is too low. Please repeat the command.")

        if command.intent == "status":
            snapshot = self.state()
            return {
                "ok": True,
                "intent": "status",
                "spoken_reply": (
                    f"The jump is at {snapshot['left_pos_in']} inches and the system is "
                    f"{snapshot['app_state'].replace('_', ' ')}."
                ),
            }

        if command.intent == "set_height" and command.height_in is not None:
            self.set_preset(command.height_in)
            return {
                "ok": True,
                "intent": "set_height",
                "height_in": command.height_in,
                "spoken_reply": f"Setting both standards to {command.height_in} inches.",
            }

        raise ValueError("Voice command could not be completed.")

def run_ui(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> int:
    runtime = SmartJumpRuntime()
    runtime.start()

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, code: int, payload: dict) -> None:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))

        def do_GET(self) -> None:
            path = urlparse(self.path).path

            if path == "/" or path == "/index.html":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(DIGITAL_TWIN_HTML.encode("utf-8"))
                return

            if path == "/api/state":
                self._send_json(200, runtime.state())
                return

            self._send_json(404, {"error": "not_found"})

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            length = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(length).decode("utf-8") if length else ""
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json(400, {"ok": False, "error": "invalid_json"})
                return

            if path == "/api/preset":
                try:
                    runtime.set_preset(int(data.get("height_in", 36)))
                except (TypeError, ValueError) as exc:
                    self._send_json(400, {"ok": False, "error": str(exc)})
                    return
                except RuntimeError as exc:
                    self._send_json(409, {"ok": False, "error": str(exc)})
                    return
                self._send_json(200, {"ok": True, "state": runtime.state()})
                return

            if path == "/api/voice":
                try:
                    result = runtime.voice(
                        str(data.get("transcript", "")),
                        float(data.get("confidence", 1.0)),
                    )
                except (TypeError, ValueError) as exc:
                    self._send_json(400, {"ok": False, "error": str(exc)})
                    return
                except RuntimeError as exc:
                    self._send_json(409, {"ok": False, "error": str(exc)})
                    return
                self._send_json(200, result)
                return

            if path == "/api/stop":
                runtime.stop()
                self._send_json(200, {"ok": True})
                return

            if path == "/api/force_desync":
                runtime.force_desync()
                self._send_json(200, {"ok": True})
                return

            if path == "/api/reset":
                runtime.reset()
                self._send_json(200, {"ok": True})
                return

            self._send_json(404, {"error": "not_found"})

        def log_message(self, format: str, *args) -> None:
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"

    print(f"Smart Jump UI running at {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    return 0

def main():
    run_ui()

if __name__ == "__main__":
    main()
