from decimal import Decimal
from types import SimpleNamespace

import pytest

from calc import (
    HELP_MESSAGE,
    CalculatorState,
    initialize_state,
    parse_cli_args,
    process_command,
)


def test_initialize_state_rejects_invalid_start():
    args = SimpleNamespace(start="not-a-number", memory=[], show_help=False)
    state, message = initialize_state(args)
    assert state is None
    assert message == '"not-a-number" is not a number.'


def test_initialize_state_with_memory_values():
    args = parse_cli_args(["--start", "2.5", "--memory", "1", "3.5"])
    state, message = initialize_state(args)
    assert message is None
    assert state.value == Decimal("2.5")
    assert state.memory == [Decimal("1"), Decimal("3.5")]


@pytest.mark.parametrize(
    "command,expected_value",
    [
        ("add 3", Decimal("3")),
        ("subtract 2", Decimal("-2")),
        ("multiply 4", Decimal("0")),
        ("divide 2", Decimal("0")),
        ("power 2", Decimal("0")),
    ],
)
def test_process_command_math_operations(command, expected_value):
    state = CalculatorState()
    should_continue, message = process_command(state, command)
    assert should_continue
    assert message is None
    assert state.value == expected_value


def test_process_command_reports_decimal_error():
    state = CalculatorState()
    should_continue, message = process_command(state, "add nope")
    assert should_continue
    assert message == '"nope" is not a number.'
    assert state.value == Decimal("0")


def test_process_command_reports_division_by_zero():
    state = CalculatorState(value=Decimal("10"))
    should_continue, message = process_command(state, "divide 0")
    assert should_continue
    assert message == "Cannot divide by zero."
    assert state.value == Decimal("10")


def test_process_command_help_on_unknown_input():
    state = CalculatorState()
    should_continue, message = process_command(state, "unknown command")
    assert should_continue
    assert "Commands:" in message


def test_process_command_sets_value_from_plain_number():
    state = CalculatorState()
    should_continue, message = process_command(state, "42.5")
    assert should_continue
    assert message is None
    assert state.value == Decimal("42.5")


def test_sqrt_reports_negative_value_error():
    state = CalculatorState(value=Decimal("-1"))
    should_continue, message = process_command(state, "sqrt")
    assert should_continue
    assert message == "Cannot take square root of a negative number."
    assert state.value == Decimal("-1")


def test_help_flag_shows_commands():
    # Simulate running main initializer with --help.
    args = parse_cli_args(["--help"])
    state, message = initialize_state(args)
    assert state is not None
    assert HELP_MESSAGE in message


def test_save_and_load_round_trip():
    state = CalculatorState(value=Decimal("7"))
    should_continue, message = process_command(state, "save")
    assert should_continue
    assert "Saved" in message

    state.value = Decimal("1")
    should_continue, message = process_command(state, "load 0")
    assert should_continue
    assert state.value == Decimal("7")
    assert "Loaded" in message


def test_load_reports_invalid_index():
    state = CalculatorState()
    should_continue, message = process_command(state, "load 3")
    assert should_continue
    assert message == "Invalid memory index."
