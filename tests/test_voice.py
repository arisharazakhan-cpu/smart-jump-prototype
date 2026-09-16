import pytest

from smartjump.voice import interpret_voice_command


@pytest.mark.parametrize(
    ("transcript", "expected"),
    [
        ("Smart Jump, set 48 inches", 48),
        ("raise the jump to forty eight inches", 48),
        ("lower height to thirty-six", 36),
    ],
)
def test_height_commands(transcript, expected):
    command = interpret_voice_command(transcript)
    assert command.intent == "set_height"
    assert command.height_in == expected


def test_stop_has_priority_over_other_words():
    command = interpret_voice_command("Stop, do not set it to 60")
    assert command.intent == "stop"
    assert command.height_in is None


def test_status_command():
    assert interpret_voice_command("What height is the jump?").intent == "status"


@pytest.mark.parametrize("transcript", ["set it very high", "set 100 inches", "hello jump"])
def test_unsafe_or_ambiguous_commands_are_rejected(transcript):
    with pytest.raises(ValueError):
        interpret_voice_command(transcript)

