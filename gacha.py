import argparse
import collections
import csv
import json
import random
import statistics
from typing import Dict, Iterable, List, Sequence


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


MAX_CHARACTERS = 1_000_000
MAX_TRIALS = 1_000_000


def probability_percentage(value: str) -> float:
    percentage = float(value)
    if not 0 <= percentage <= 100:
        raise argparse.ArgumentTypeError("確率は 0 以上 100 以下で指定してください。")
    return percentage


def bounded_positive_int(name: str, limit: int):
    def parser(value: str) -> int:
        number = int(value)
        if number < 1 or number > limit:
            raise argparse.ArgumentTypeError(
                f"{name} は 1 以上 {limit} 以下で指定してください。"
            )
        return number

    return parser


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="指定確率で成功するまでの試行回数を集計します。"
    )
    parser.add_argument(
        "-p",
        "--probability",
        type=probability_percentage,
        required=True,
        help="成功確率 (0-100%%)",
    )
    parser.add_argument(
        "-c",
        "--characters",
        type=bounded_positive_int("キャラ数", MAX_CHARACTERS),
        required=True,
        help=f"シミュレーションするキャラ数 (1-{MAX_CHARACTERS})",
    )
    parser.add_argument(
        "-t",
        "--trials",
        type=bounded_positive_int("試行回数", MAX_TRIALS),
        required=True,
        help=f"試行の繰り返し回数 (1-{MAX_TRIALS})",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="乱数シード (未指定時はランダム)",
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="詳細ログを抑制します。",
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="詳細ログを有効にします。",
    )

    parser.add_argument(
        "--csv-output",
        type=str,
        help="結果を CSV 形式で保存するパス。",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        help="結果を JSON 形式で保存するパス。",
    )
    return parser.parse_args()


def simulate_once(probability: float, rng: random.Random, verbose: bool) -> int:
    count = 0
    while True:
        value = rng.random()
        success = value < probability
        count += 1
        if verbose:
            color = pycolor.RED if success else pycolor.BLUE
            print(f"rand={value:.6f}, {color}{success}{pycolor.END}")
        if success:
            break
    return count


def simulate_characters(
    probability: float,
    characters: int,
    rng: random.Random,
    verbose: bool,
) -> int:
    attempts: List[int] = []
    for index in range(characters):
        attempt_count = simulate_once(probability, rng, verbose)
        attempts.append(attempt_count)
        if verbose:
            print(f"character {index + 1}: attempts={attempt_count}")
    return sum(attempts)


def simulate_trials(
    probability: float,
    characters: int,
    trials: int,
    rng: random.Random,
    quiet: bool,
    verbose: bool,
) -> List[int]:
    record: List[int] = []
    for trial_index in range(trials):
        total_attempts = simulate_characters(probability, characters, rng, verbose)
        record.append(total_attempts)
        if not quiet:
            print(f"trial {trial_index + 1}/{trials}: total_attempts={total_attempts}")
    return record


def summarize(record: Sequence[int]) -> Dict[str, object]:
    histogram = dict(sorted(collections.Counter(record).items()))
    average = statistics.fmean(record) if record else 0
    variance = statistics.pvariance(record) if len(record) > 1 else 0.0
    return {
        "trials": len(record),
        "total_attempts": sum(record),
        "average_attempts": average,
        "variance": variance,
        "max_attempts": max(record) if record else 0,
        "min_attempts": min(record) if record else 0,
        "histogram": histogram,
    }


def save_json(
    path: str,
    record: Sequence[int],
    summary: Dict[str, object],
    probability_percentage: float,
    characters: int,
    trials: int,
    seed: int | None,
) -> None:
    payload = {
        "parameters": {
            "probability_percent": probability_percentage,
            "characters": characters,
            "trials": trials,
            "seed": seed,
        },
        "record": list(record),
        "summary": summary,
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    print(f"JSON を保存しました: {path}")


def save_csv(
    path: str,
    record: Iterable[int],
    probability_percentage: float,
    characters: int,
    seed: int | None,
) -> None:
    fieldnames = ["trial_index", "attempts", "characters", "probability_percent", "seed"]
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for index, attempts in enumerate(record, start=1):
            writer.writerow(
                {
                    "trial_index": index,
                    "attempts": attempts,
                    "characters": characters,
                    "probability_percent": probability_percentage,
                    "seed": seed,
                }
            )
    print(f"CSV を保存しました: {path}")


def main() -> None:
    args = parse_args()
    probability = args.probability / 100

    rng = random.Random(args.seed)
    if args.seed is not None and not args.quiet:
        print(f"乱数シードを設定しました: {args.seed}")

    record = simulate_trials(
        probability=probability,
        characters=args.characters,
        trials=args.trials,
        rng=rng,
        quiet=args.quiet,
        verbose=args.verbose,
    )
    summary = summarize(record)

    print("---- summary ----")
    print(f"trials: {summary['trials']}")
    print(f"total_attempts: {summary['total_attempts']}")
    print(f"average_attempts: {summary['average_attempts']:.4f}")
    print(f"variance: {summary['variance']:.4f}")
    print(f"max_attempts: {summary['max_attempts']}")
    print(f"min_attempts: {summary['min_attempts']}")
    print(f"histogram: {summary['histogram']}")

    if args.json_output:
        save_json(
            args.json_output,
            record,
            summary,
            probability_percentage=args.probability,
            characters=args.characters,
            trials=args.trials,
            seed=args.seed,
        )

    if args.csv_output:
        save_csv(
            args.csv_output,
            record,
            probability_percentage=args.probability,
            characters=args.characters,
            seed=args.seed,
        )


if __name__ == "__main__":
    main()
