from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
import json
import os
import time

APP_VERSION = os.getenv("APP_VERSION", "3.0.0")
APP_MESSAGE = os.getenv("APP_MESSAGE", "Initial GitOps deployment")
START_TIME = time.time()
COUNTERS = {}
INFLIGHT = 0
LOCK = Lock()


def metric_path(path):
    return path if path in ("/", "/healthz", "/metrics") else "/other"


def render_metrics():
    with LOCK:
        counters = dict(COUNTERS)
        inflight = INFLIGHT
    lines = [
        "# HELP cse644_http_requests_total Total HTTP requests handled by path and status.",
        "# TYPE cse644_http_requests_total counter",
    ]
    for (path, status), count in sorted(counters.items()):
        lines.append(f'cse644_http_requests_total{{path="{path}",status="{status}"}} {count}')
    lines.extend([
        "# HELP cse644_inflight_requests Current requests being handled.",
        "# TYPE cse644_inflight_requests gauge",
        f"cse644_inflight_requests {inflight}",
        "# HELP cse644_process_start_time_seconds Application process start time.",
        "# TYPE cse644_process_start_time_seconds gauge",
        f"cse644_process_start_time_seconds {START_TIME:.3f}",
        "# HELP cse644_app_info Static application identity.",
        "# TYPE cse644_app_info gauge",
        f'cse644_app_info{{student="Jingyou Ma",version="{APP_VERSION}"}} 1',
    ])
    return ("\n".join(lines) + "\n").encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global INFLIGHT
        with LOCK:
            INFLIGHT += 1
        status = 200
        try:
            if self.path == "/metrics":
                body = render_metrics()
                content_type = "text/plain; version=0.0.4"
            elif self.path == "/healthz":
                body = b"healthy"
                content_type = "text/plain"
            elif self.path == "/":
                body = json.dumps({
                    "student": "Jingyou Ma",
                    "course": "CSE644",
                    "assignment": "GitOps and Application Observability",
                    "version": APP_VERSION,
                    "message": APP_MESSAGE,
                }).encode()
                content_type = "application/json"
            else:
                status = 404
                body = b"not found"
                content_type = "text/plain"
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        finally:
            with LOCK:
                key = (metric_path(self.path), str(status))
                COUNTERS[key] = COUNTERS.get(key, 0) + 1
                INFLIGHT -= 1

    def log_message(self, fmt, *args):
        print(f"request client={self.client_address[0]} " + fmt % args, flush=True)


if __name__ == "__main__":
    print(f"CSE644 app version {APP_VERSION} listening on 0.0.0.0:8888", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8888), Handler).serve_forever()

