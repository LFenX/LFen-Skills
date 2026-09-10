import gzip
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

try:
    from .outbox import AckValidationError, Outbox, validate_ack
except ImportError:  # direct ``python test_outbox.py`` invocation
    from outbox import AckValidationError, Outbox, validate_ack


class _Handler(BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):  # noqa: N802
        raw = self.rfile.read(int(self.headers["Content-Length"]))
        events = json.loads(gzip.decompress(raw))["data"]["events"]
        self.__class__.seen.append((self.headers["Idempotency-Key"], events))
        body = json.dumps({
            "data": {"accepted": len(events), "duplicate": 0, "rejected": 0},
            "meta": {"request_id": "test-request"},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


class OutboxTests(unittest.TestCase):
    def test_gzip_idempotent_enqueue_and_flush(self):
        server = HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory, Outbox(Path(directory) / "outbox.db") as outbox:
                event = {"event_id": "e1", "payload": "原文"}
                batch_id = outbox.enqueue([event])
                self.assertEqual(outbox.enqueue([event]), None)
                result = outbox.flush(f"http://127.0.0.1:{server.server_port}/")
                self.assertEqual(result[0].status, "sent")
                self.assertEqual(_Handler.seen[-1], (batch_id, [event]))
        finally:
            server.shutdown()
            server.server_close()

    def test_reject_conflicting_event_and_ack(self):
        with tempfile.TemporaryDirectory() as directory, Outbox(Path(directory) / "outbox.db") as outbox:
            outbox.enqueue([{"event_id": "e1", "value": 1}])
            with self.assertRaises(ValueError):
                outbox.enqueue([{"event_id": "e1", "value": 2}])
        with self.assertRaises(AckValidationError) as caught:
            validate_ack({"data": {"accepted": 1, "duplicate": 0, "rejected": 1,
                                     "results": [{"event_id": "e1", "status": "accepted"},
                                                 {"event_id": "e2", "status": "rejected"}]},
                          "meta": {"request_id": "r"}}, 2)
        self.assertTrue(caught.exception.partial)


if __name__ == "__main__":
    unittest.main()
