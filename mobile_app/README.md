# Mobile Application Layer

Represents the mounted rider control interface.

Responsibilities:
- Connect to two BLE controller devices
- Send synchronized preset commands
- Transmit heartbeat at fixed interval
- Monitor telemetry notifications
- Detect desynchronization beyond tolerance
- Trigger coordinated stop on any anomaly
- Expose emergency stop UI

Core logic currently implemented in:
app/orchestrator.py

Future implementation options:
- Native Swift / Kotlin
- Flutter
- React Native

Security considerations:
- Device pairing and bonding
- Encrypted BLE characteristics
- Command authentication
