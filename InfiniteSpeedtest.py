# 通信容量無制限の携帯回線が本当に無制限か確認するためのコード
import argparse
import subprocess
import time
from datetime import datetime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run repeated download-only speed tests.",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=None,
        help="Number of times to run. Omit for indefinite execution until interrupted.",
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=float,
        default=0.0,
        help="Seconds to sleep between runs.",
    )
    parser.add_argument(
        "--log-file",
        default="speedtest.log",
        help="Path to the log file to append results to.",
    )
    return parser.parse_args()


def log_result(log_file: str, run_number: int, status: str, detail: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    message = f"{timestamp}\tRun {run_number}\t{status}\t{detail}\n"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(message)


def run_speedtests() -> None:
    args = parse_args()
    successes = 0
    failures = 0
    run_number = 0

    try:
        while args.count is None or run_number < args.count:
            run_number += 1
            try:
                subprocess.check_call(["speedtest", "--download"])
            except subprocess.CalledProcessError as exc:
                failures += 1
                log_result(
                    args.log_file,
                    run_number,
                    "FAILURE",
                    f"Return code {exc.returncode}",
                )
            except FileNotFoundError as exc:
                failures += 1
                log_result(
                    args.log_file,
                    run_number,
                    "FAILURE",
                    f"Command not found: {exc}",
                )
            else:
                successes += 1
                log_result(args.log_file, run_number, "SUCCESS", "Download test passed")

            if args.sleep > 0 and (args.count is None or run_number < args.count):
                time.sleep(args.sleep)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Printing summary...")
    finally:
        total = successes + failures
        print("=== Speedtest summary ===")
        print(f"Total attempts: {total}")
        print(f"Successes     : {successes}")
        print(f"Failures      : {failures}")


if __name__ == "__main__":
    run_speedtests()
