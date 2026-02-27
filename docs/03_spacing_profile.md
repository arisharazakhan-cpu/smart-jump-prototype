# Rail Spacing Profile Specification
## Mounted-Capable Vertical Geometry Model

---

# 1. Objective

Define deterministic rail positions for each preset height to maintain realistic vertical spacing as height increases.

Each preset defines:
- Top rail height (absolute)
- Middle rail height (absolute)
- Bottom rail height (absolute)

These values represent target heights above ground.

---

# 2. Design Principles

1. The bottom rail should remain relatively low across presets.
2. The middle rail should increase proportionally but not linearly with the top rail.
3. The spacing between rails should increase gradually as height increases.
4. All values must remain within actuator stroke limits.

---

# 3. Preset Height Table (Initial Engineering Model)

All values in inches above ground.

| Preset | Top Rail | Middle Rail | Bottom Rail |
|---------|----------|-------------|-------------|
| 2'0     | 24       | 17          | 10          |
| 2'3     | 27       | 19          | 11          |
| 2'6     | 30       | 22          | 12          |
| 2'9     | 33       | 25          | 14          |
| 3'0     | 36       | 27          | 15          |
| 3'3     | 39       | 30          | 17          |
| 3'6     | 42       | 33          | 19          |

These values are initial engineering targets and will be validated during calibration.

---

# 4. Derived Spacing (For Verification)

Spacing between rails:

Example for 3'6:
Top to Middle: 42 - 33 = 9 inches
Middle to Bottom: 33 - 19 = 14 inches

Spacing increases gradually as overall height increases.

---

# 5. Mechanical Constraints

Each actuator must support:
- Minimum height: approximately 10 inches
- Maximum height: at least 42 inches
- Stroke requirement: minimum 32 inches

Design margin recommended:
Stroke >= 36 inches

---

# 6. Calibration Strategy

During installation:

1. System homes each stage.
2. Manual measurement confirms actual rail height.
3. Calibration offsets are stored in persistent memory.
4. Preset table is adjusted to match physical build tolerances.

---

# 7. Future Optimization

Future versions may:
- Allow trainer-defined spacing profiles.
- Provide adjustable spacing curves.
- Support discipline-specific spacing templates.

