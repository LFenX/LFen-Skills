"""One-command collector client: collect, persist, and optionally flush."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from collector_core import collect_task, load_local_secret  # noqa: E402
from client.outbox import Outbox  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser("sync", help="collect task evidence into outbox and optionally flush")
    collect.add_argument("--task-dir", required=True, type=Path)
    collect.add_argument("--outbox", required=True, type=Path)
    collect.add_argument("--endpoint")
    collect.add_argument("--token")
    collect.add_argument("--secret-file", type=Path)
    collect.add_argument("--max-events", type=int, default=100)
    collect.add_argument("--max-compressed-bytes", type=int, default=1_000_000)
    flush = sub.add_parser("flush", help="replay due outbox batches")
    flush.add_argument("--outbox", required=True, type=Path)
    flush.add_argument("--endpoint", required=True)
    flush.add_argument("--token")
    flush.add_argument("--limit", type=int, default=20)
    measure = sub.add_parser("measure", help="run a command and write a measured sidecar")
    measure.add_argument("--task-dir", required=True, type=Path)
    measure.add_argument("--stage", required=True)
    measure.add_argument("--step-id", required=True)
    measure.add_argument("--plan-step-ref")
    measure.add_argument("argv", nargs=argparse.REMAINDER)
    status = sub.add_parser("status", help="show local outbox counts")
    status.add_argument("--outbox", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "sync":
        secret = load_local_secret(args.secret_file)
        batch = collect_task(args.task_dir, secret=secret)
        with Outbox(args.outbox) as box:
            ids = box.enqueue_many(batch["events"], batch_id=batch["batch_id"],
                                    max_events=args.max_events, max_compressed_bytes=args.max_compressed_bytes)
            result = {"queued_batches": ids, "event_count": batch["event_count"]}
            if args.endpoint:
                result["flush"] = [r.__dict__ for r in box.flush(args.endpoint, token=args.token)]
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "flush":
        with Outbox(args.outbox) as box:
            print(json.dumps({"flush": [r.__dict__ for r in box.flush(args.endpoint, token=args.token, limit=args.limit)]}, ensure_ascii=False))
        return 0
    if args.command == "status":
        with Outbox(args.outbox) as box:
            print(json.dumps(box.status(), ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "measure":
        command = args.argv
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            raise SystemExit("measure requires a command after --")
        started = time.monotonic()
        completed = subprocess.run(command, check=False)
        duration_ms = round((time.monotonic() - started) * 1000, 3)
        sidecar = args.task_dir / "collector-measurements.jsonl"
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        record = {"stage": args.stage, "event_type": "measured_step", "execution_step_ref": args.step_id,
                  "plan_step_ref": args.plan_step_ref, "duration_ms": duration_ms,
                  "duration_provenance": "measured", "status": "succeeded" if completed.returncode == 0 else "failed",
                  "exit_code": completed.returncode,
                  "occurred_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")}
        with sidecar.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return completed.returncode
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
