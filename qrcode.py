import argparse
import logging
import sys
import time
from pathlib import Path

import cv2
from pyzbar.pyzbar import decode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QR code reader using OpenCV and pyzbar.")
    parser.add_argument(
        "--camera-id", type=int, default=0, help="Camera device ID to open (default: 0)."
    )
    parser.add_argument(
        "--width", type=int, help="Requested capture width. Skipped when not provided."
    )
    parser.add_argument(
        "--height", type=int, help="Requested capture height. Skipped when not provided."
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="Exit automatically after the given number of seconds. Disabled when omitted.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Optional file path to save decode results in addition to stdout logging.",
    )
    return parser.parse_args()


def setup_logging(log_file: Path | None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=handlers)


def main() -> int:
    args = parse_args()
    setup_logging(args.log_file)

    cap = cv2.VideoCapture(args.camera_id)
    if not cap.isOpened():
        logging.error("Failed to open camera with ID %s.", args.camera_id)
        return 1

    if args.width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    if args.height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    font = cv2.FONT_HERSHEY_SIMPLEX
    start_time = time.time()
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                decoded = decode(frame)
                if decoded:
                    for barcode in decoded:
                        x, y, w, h = barcode.rect
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        barcode_data = barcode.data.decode("utf-8")
                        frame = cv2.putText(
                            frame,
                            barcode_data,
                            (x, y - 10),
                            font,
                            0.5,
                            (0, 0, 255),
                            2,
                            cv2.LINE_AA,
                        )
                        logging.info("Decoded data: %s", barcode_data)

                cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            if args.timeout and (time.time() - start_time) >= args.timeout:
                logging.info("Timeout reached after %.2f seconds. Exiting.", args.timeout)
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
