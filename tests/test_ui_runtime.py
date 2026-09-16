import pytest

from smartjump.ui import SmartJumpRuntime
from smartjump.web_ui import DIGITAL_TWIN_HTML


def test_voice_height_command_moves_both_standards():
    runtime = SmartJumpRuntime()
    result = runtime.voice("Smart Jump, set forty-eight inches", confidence=0.96)
    assert result["intent"] == "set_height"
    assert runtime.left.target_in == 48
    assert runtime.right.target_in == 48


def test_low_confidence_motion_is_rejected():
    runtime = SmartJumpRuntime()
    with pytest.raises(ValueError, match="confidence"):
        runtime.voice("set 48 inches", confidence=0.40)
    assert runtime.left.target_in == 24


def test_low_confidence_stop_is_still_honored():
    runtime = SmartJumpRuntime()
    runtime.set_preset(48)
    result = runtime.voice("stop", confidence=0.10)
    assert result["intent"] == "stop"
    assert runtime.left.target_in == runtime.left.position_in
    assert runtime.right.target_in == runtime.right.position_in


def test_state_includes_visual_telemetry_fields():
    state = SmartJumpRuntime().state()
    assert state["difference_in"] == 0
    assert state["controllers_online"] is True
    assert state["events"]


def test_demo_has_three_rails_and_standalone_interactions():
    assert DIGITAL_TWIN_HTML.count('class="rail ') == 3
    assert "standaloneDemo" in DIGITAL_TWIN_HTML
    assert 'id="heightSlider"' in DIGITAL_TWIN_HTML
    assert "Interactive GitHub demo" in DIGITAL_TWIN_HTML
