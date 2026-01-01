"""Command-line calculator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Tuple


class pycolor:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RETURN = "\033[07m"  # 反転
    ACCENT = "\033[01m"  # 強調
    FLASH = "\033[05m"  # 点滅
    RED_FLASH = "\033[05;41m"  # 赤背景+点滅
    END = "\033[0m"


COMMAND_ALIASES = {
    "p": "add",
    "+": "add",
    "s": "subtract",
    "-": "subtract",
    "m": "multiply",
    "*": "multiply",
    "d": "divide",
    "/": "divide",
    "^": "power",
    "power": "power",
    "%": "percent",
    "c": "clear",
}

COMMAND_LIST = {
    "add": "後ろに入力した数値を足します。 (+, p)",
    "subtract": "後ろに入力した数値を引きます。 (-, s)",
    "multiply": "後ろに入力した数値をかけます。 (*, m)",
    "divide": "後ろに入力した数値で割ります。 (/ , d)",
    "power": "現在値の後ろに入力した数値乗を出します。 (^, power)",
    "percent": "現在値の後ろに入力した数値パーセントを出します。 (%)",
    "sqrt": "現在値の平方根を出します。",
    "save": "現在値をメモリに保存します。",
    "load": "メモリから値を読み込みます。",
    "clear": "現在値を0にします。 (c)",
    "exit": "終了します。",
    "help": "このヘルプを表示します。 (--help)",
}


HELP_MESSAGE = "Commands:\n" + "\n".join(
    f"  {name}: {description}" for name, description in COMMAND_LIST.items()
)


@dataclass
class CalculatorState:
    value: Decimal = Decimal("0")
    memory: List[Decimal] = field(default_factory=list)


def safe_decimal(value: str) -> Tuple[Decimal | None, str | None]:
    """Return Decimal or error message without raising."""

    try:
        return Decimal(value), None
    except (InvalidOperation, ValueError):
        return None, f'"{value}" is not a number.'


def parse_cli_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Command-line calculator", add_help=False)
    parser.add_argument("--help", action="store_true", dest="show_help", help="Show command list")
    parser.add_argument(
        "--start",
        default="0",
        help="Initial value for the calculator (Decimal compatible)",
    )
    parser.add_argument(
        "--memory",
        nargs="*",
        default=[],
        help="Initial memory values (space separated Decimal compatible)",
    )
    return parser.parse_args(argv)


def initialize_state(args: argparse.Namespace) -> Tuple[CalculatorState | None, str | None]:
    value, error = safe_decimal(args.start)
    if error:
        return None, error

    state = CalculatorState(value=value)
    for item in args.memory:
        converted, memory_error = safe_decimal(item)
        if memory_error:
            return None, memory_error
        state.memory.append(converted)

    if args.show_help:
        return state, HELP_MESSAGE

    return state, None


def _missing_value_message(command_name: str) -> str:
    return f"Missing value for {command_name}." + f"\n{HELP_MESSAGE}"


def process_command(state: CalculatorState, input_line: str) -> Tuple[bool, str | None]:
    parts = input_line.strip().split()
    if not parts:
        return True, HELP_MESSAGE

    command = parts[0]
    command = COMMAND_ALIASES.get(command, command)

    if command in {"--help", "help"}:
        return True, HELP_MESSAGE

    if command in {"commands", "list"}:
        return True, HELP_MESSAGE

    if command == "exit":
        return False, f"{pycolor.GREEN}Bye.{pycolor.END}"

    if command == "add":
        if len(parts) < 2:
            return True, _missing_value_message("add")
        operand, error = safe_decimal(parts[1])
        if error:
            return True, error
        state.value += operand
        return True, None

    if command == "subtract":
        if len(parts) < 2:
            return True, _missing_value_message("subtract")
        operand, error = safe_decimal(parts[1])
        if error:
            return True, error
        state.value -= operand
        return True, None

    if command == "multiply":
        if len(parts) < 2:
            return True, _missing_value_message("multiply")
        operand, error = safe_decimal(parts[1])
        if error:
            return True, error
        state.value *= operand
        return True, None

    if command == "divide":
        if len(parts) < 2:
            return True, _missing_value_message("divide")
        operand, error = safe_decimal(parts[1])
        if error:
            return True, error
        if operand == 0:
            return True, "Cannot divide by zero."
        state.value /= operand
        return True, None

    if command == "power":
        if len(parts) < 2:
            return True, _missing_value_message("power")
        operand, error = safe_decimal(parts[1])
        if error:
            return True, error
        state.value = state.value ** operand
        return True, None

    if command == "percent":
        if len(parts) < 2:
            return True, _missing_value_message("percent")
        operand, error = safe_decimal(parts[1])
        if error:
            return True, error
        state.value *= operand / Decimal("100")
        return True, None

    if command == "sqrt":
        if state.value < 0:
            return True, "Cannot take square root of a negative number."
        state.value = state.value.sqrt()
        return True, None

    if command == "save":
        state.memory.append(state.value)
        return True, f"{pycolor.BLUE}Saved {state.value}.{pycolor.END}"

    if command == "load":
        if len(parts) < 2:
            return True, _missing_value_message("load")
        try:
            index = int(parts[1])
        except ValueError:
            return True, f'"{parts[1]}" is not a number.'
        if index < 0 or index >= len(state.memory):
            return True, "Invalid memory index."
        state.value = state.memory[index]
        return True, f"{pycolor.BLUE}Loaded {state.value}.{pycolor.END}"

    if command == "clear":
        state.value = Decimal("0")
        return True, None

    if state.value == 0:
        parsed, error = safe_decimal(command)
        if error is None and parsed is not None:
            state.value = parsed
            return True, None

    return True, f"Error: command not found\n{HELP_MESSAGE}"


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_cli_args(argv)
    state, init_message = initialize_state(args)
    if state is None:
        print(init_message)
        return

    if init_message:
        print(init_message)

    while True:
        print(f"{pycolor.CYAN}{state.value}{pycolor.END}\n{pycolor.ACCENT}❯{pycolor.END} ", end="")
        try:
            raw = input()
        except EOFError:
            print(pycolor.RED + "\nEOF has been entered." + pycolor.END)
            break
        except KeyboardInterrupt:
            print(pycolor.RED + "\nA KeyBoardInterrupt occurred." + pycolor.END)
            break

        should_continue, message = process_command(state, raw)
        if message:
            print(message)
        if not should_continue:
            break


if __name__ == "__main__":
    main()
