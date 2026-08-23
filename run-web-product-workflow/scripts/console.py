#!/usr/bin/env python3
"""Governance console: a read-only local server over the two governed asset roots.

Lifecycle is explicit so the console is easy to operate:

    console.py start   --project-root <project-root>   # background, opens the browser
    console.py status                                  # is it running, and where
    console.py open                                    # reopen the browser
    console.py stop                                    # shut it down

Read-only by construction: only GET and HEAD are served, every requested path must
resolve inside .project-governance or LG_project_docs, and nothing is ever written to
a governance record. The console is a view; per C10 8.0 a DerivedView must never be
the only source of a tracking fact.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

import console_assets
import console_model
import console_render
from governance_artifacts import GovernanceError

HOST = "127.0.0.1"
DEFAULT_PORT = 7788
STATE_RELATIVE = Path(".project-governance") / "runtime-cache" / "console.json"
# Only these roots are ever readable, and only below the project root.
SERVABLE_ROOTS = (".project-governance", "LG_project_docs")
TEXT_PREVIEW_LIMIT = 400_000


# --- state ------------------------------------------------------------------


def state_path(project_root: Path) -> Path:
    return project_root.resolve() / STATE_RELATIVE


def read_state(project_root: Path) -> dict[str, Any] | None:
    path = state_path(project_root)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_state(project_root: Path, payload: dict[str, Any]) -> None:
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def clear_state(project_root: Path) -> None:
    try:
        state_path(project_root).unlink()
    except FileNotFoundError:
        pass


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, errors="replace",
        )
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    except OSError:
        return False
    return True


def port_responds(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.4)
        return probe.connect_ex((HOST, port)) == 0


def running_instance(project_root: Path) -> dict[str, Any] | None:
    state = read_state(project_root)
    if not state:
        return None
    if process_alive(int(state.get("pid", 0))) and port_responds(int(state.get("port", 0))):
        return state
    clear_state(project_root)
    return None


def free_port(preferred: int) -> int:
    for candidate in [preferred] + list(range(preferred + 1, preferred + 40)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            if probe.connect_ex((HOST, candidate)) != 0:
                return candidate
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((HOST, 0))
        return probe.getsockname()[1]


# --- safe path resolution ---------------------------------------------------


def resolve_servable(project_root: Path, raw: str) -> Path | None:
    """Resolve a request path, or None if it escapes the servable roots.

    resolve() collapses .. and follows symlinks before the containment test, so a
    link pointing outside the project cannot be used to read arbitrary files.
    """

    candidate = urllib.parse.unquote(raw or "").strip().replace("\\", "/")
    if not candidate or candidate.startswith("/") or (len(candidate) > 1 and candidate[1] == ":"):
        return None
    root = project_root.resolve()
    try:
        target = (root / candidate).resolve()
    except (OSError, RuntimeError, ValueError):
        return None
    if not target.is_file():
        return None
    for servable in SERVABLE_ROOTS:
        base = (root / servable).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            continue
        return target
    return None


# --- request handling -------------------------------------------------------


class ConsoleHandler(BaseHTTPRequestHandler):
    server_version = "GovernanceConsole/1.0"
    project_root: Path = Path(".")

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter console
        return

    # Read-only: BaseHTTPRequestHandler only dispatches the verbs we define.
    def do_GET(self) -> None:  # noqa: N802
        self._handle(send_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self._handle(send_body=False)

    def _send(self, status: int, body: bytes, content_type: str, *, send_body: bool = True,
              extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def _html(self, status: int, markup: str, send_body: bool) -> None:
        self._send(status, markup.encode("utf-8"), "text/html; charset=utf-8", send_body=send_body)

    def _handle(self, *, send_body: bool) -> None:
        parsed = urllib.parse.urlparse(self.path)
        route = urllib.parse.unquote(parsed.path)
        params = urllib.parse.parse_qs(parsed.query)
        try:
            if route == "/static/console.css":
                self._send(200, console_assets.CSS.encode("utf-8"), "text/css; charset=utf-8", send_body=send_body)
                return
            if route == "/static/console.js":
                self._send(200, console_assets.JS.encode("utf-8"), "text/javascript; charset=utf-8", send_body=send_body)
                return
            if route == "/favicon.ico":
                self._send(204, b"", "image/x-icon", send_body=send_body)
                return
            if route == "/raw":
                self._serve_raw(params.get("path", [""])[0], send_body)
                return
            model = console_model.scan(self.project_root)
            self._route_page(model, route, params, send_body)
        except (GovernanceError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            fallback = {"project_id": "", "tasks": [], "docs": {}, "artifacts": [], "unresolved": [],
                        "doc_findings": [], "integrity": {}, "derivation": {}, "state_present": True}
            markup = console_render.shell(
                fallback, path=route, title="错误",
                crumbs=[("/", "总览"), ("", "错误")],
                body=console_render.page_error(fallback, 500, "读取治理资产时出错。", str(exc)),
            )
            self._html(500, markup, send_body)

    def _route_page(self, model: dict[str, Any], route: str, params: dict[str, list[str]], send_body: bool) -> None:
        home = ("/", "总览")
        if route == "/":
            self._html(200, console_render.shell(model, path=route, title="总览", crumbs=[("", "总览")],
                                                 body=console_render.page_overview(model)), send_body)
            return
        if route == "/tasks":
            self._html(200, console_render.shell(model, path=route, title="任务", crumbs=[home, ("", "任务")],
                                                 body=console_render.page_tasks(model)), send_body)
            return
        if route.startswith("/tasks/"):
            task_id = route[len("/tasks/"):]
            body = console_render.page_task(model, task_id)
            if body is None:
                self._not_found(model, route, f"没有找到任务 {task_id}", send_body)
                return
            self._html(200, console_render.shell(model, path="/tasks", title=task_id,
                                                 crumbs=[home, ("/tasks", "任务"), ("", task_id)], body=body), send_body)
            return
        if route == "/lineage":
            self._html(200, console_render.shell(model, path=route, title="血缘与衍生",
                                                 crumbs=[home, ("", "血缘与衍生")],
                                                 body=console_render.page_lineage(model)), send_body)
            return
        if route == "/unresolved":
            self._html(200, console_render.shell(model, path=route, title="未决项", crumbs=[home, ("", "未决项")],
                                                 body=console_render.page_unresolved(model)), send_body)
            return
        if route == "/docs":
            self._html(200, console_render.shell(model, path=route, title="项目文档", crumbs=[home, ("", "项目文档")],
                                                 body=console_render.page_docs(model)), send_body)
            return
        if route.startswith("/docs/"):
            requirement_id = route[len("/docs/"):]
            body = console_render.page_requirement(model, requirement_id)
            if body is None:
                self._not_found(model, route, f"没有找到需求目录 {requirement_id}", send_body)
                return
            self._html(200, console_render.shell(model, path="/docs", title=requirement_id,
                                                 crumbs=[home, ("/docs", "项目文档"), ("", requirement_id)],
                                                 body=body), send_body)
            return
        if route == "/intake":
            self._html(200, console_render.shell(model, path=route, title="待分类", crumbs=[home, ("", "待分类")],
                                                 body=console_render.page_intake(model)), send_body)
            return
        if route == "/archive":
            self._html(200, console_render.shell(model, path=route, title="迁移归档", crumbs=[home, ("", "迁移归档")],
                                                 body=console_render.page_archive(model)), send_body)
            return
        if route == "/artifacts":
            self._html(200, console_render.shell(model, path=route, title="生成物", crumbs=[home, ("", "生成物")],
                                                 body=console_render.page_artifacts(model)), send_body)
            return
        if route == "/integrity":
            self._html(200, console_render.shell(model, path=route, title="完整性与审计",
                                                 crumbs=[home, ("", "完整性与审计")],
                                                 body=console_render.page_integrity(model)), send_body)
            return
        if route == "/search":
            query = params.get("q", [""])[0]
            hits = console_model.search(model, query)
            self._html(200, console_render.shell(model, path=route, title="检索", crumbs=[home, ("", "检索")],
                                                 body=console_render.page_search(model, query, hits)), send_body)
            return
        if route == "/preview":
            self._preview(model, params.get("path", [""])[0], send_body)
            return
        self._not_found(model, route, "没有这个页面。", send_body)

    def _not_found(self, model: dict[str, Any], route: str, message: str, send_body: bool) -> None:
        markup = console_render.shell(
            model, path=route, title="未找到", crumbs=[("/", "总览"), ("", "未找到")],
            body=console_render.page_error(model, 404, message, "检查链接是否仍然有效。"),
        )
        self._html(404, markup, send_body)

    def _preview(self, model: dict[str, Any], raw: str, send_body: bool) -> None:
        target = resolve_servable(self.project_root, raw)
        if target is None:
            markup = console_render.shell(
                model, path="/preview", title="拒绝访问", crumbs=[("/", "总览"), ("", "拒绝访问")],
                body=console_render.page_error(
                    model, 403, "该路径不在可读资产范围内。",
                    "控制台只读取 .project-governance 与 LG_project_docs 之下的文件。"),
            )
            self._html(403, markup, send_body)
            return
        relative = target.relative_to(self.project_root.resolve()).as_posix()
        kind = console_model.preview_kind(target)
        payload: str | None = None
        note = ""
        if kind in {"text", "json"}:
            data = target.read_bytes()
            if len(data) > TEXT_PREVIEW_LIMIT:
                data = data[:TEXT_PREVIEW_LIMIT]
                note = f"文件较大，只显示前 {TEXT_PREVIEW_LIMIT // 1000} KB。"
            payload = data.decode("utf-8", errors="replace")
            if kind == "json":
                payload = console_render.format_json(payload)
            elif target.suffix.lower() in {".md", ".mdx"}:
                kind = "markdown"
        body = console_render.page_preview(model, relative, kind, payload, note)
        markup = console_render.shell(
            model, path="/preview", title=target.name,
            crumbs=[("/", "总览"), ("", target.name)], body=body,
        )
        self._html(200, markup, send_body)

    def _serve_raw(self, raw: str, send_body: bool) -> None:
        target = resolve_servable(self.project_root, raw)
        if target is None:
            self._send(403, b"forbidden", "text/plain; charset=utf-8", send_body=send_body)
            return
        guessed, _ = mimetypes.guess_type(target.name)
        content_type = guessed or "application/octet-stream"
        if target.suffix.lower() in {".html", ".htm"}:
            # Served only into a sandboxed iframe; keep it inert on its own too.
            content_type = "text/html; charset=utf-8"
        self._send(
            200, target.read_bytes(), content_type, send_body=send_body,
            extra={"Content-Security-Policy": "sandbox", "Content-Disposition": f'inline; filename="{target.name}"'},
        )


# --- commands ---------------------------------------------------------------


def serve(project_root: Path, port: int) -> None:
    ConsoleHandler.project_root = project_root.resolve()
    with ThreadingHTTPServer((HOST, port), ConsoleHandler) as httpd:
        httpd.serve_forever()


def cmd_start(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    if not (project_root / ".project-governance").is_dir():
        print(f"ERROR: 不是受治理的项目根（缺少 .project-governance）: {project_root}", file=sys.stderr)
        return 2
    existing = running_instance(project_root)
    if existing:
        print(f"已在运行：{existing['url']}  (pid {existing['pid']})")
        if not args.no_open:
            webbrowser.open(existing["url"])
        return 0
    port = args.port or free_port(DEFAULT_PORT)
    url = f"http://{HOST}:{port}/"
    if args.foreground:
        write_state(project_root, {"pid": os.getpid(), "port": port, "url": url,
                                   "project_root": str(project_root), "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
        print(f"治理控制台运行中：{url}\n按 Ctrl+C 结束。")
        if not args.no_open:
            threading.Timer(0.6, webbrowser.open, args=(url,)).start()
        try:
            serve(project_root, port)
        except KeyboardInterrupt:
            print("\n已停止。")
        finally:
            clear_state(project_root)
        return 0

    command = [sys.executable, "-B", str(Path(__file__).resolve()), "serve",
               "--project-root", str(project_root), "--port", str(port)]
    creation = 0
    kwargs: dict[str, Any] = {}
    if os.name == "nt":
        creation = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        kwargs["creationflags"] = creation
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
    for _ in range(60):
        if port_responds(port):
            break
        time.sleep(0.1)
    else:
        process.terminate()
        print("ERROR: 服务未能在 6 秒内就绪", file=sys.stderr)
        return 2
    write_state(project_root, {"pid": process.pid, "port": port, "url": url,
                               "project_root": str(project_root), "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    print(f"治理控制台已启动：{url}  (pid {process.pid})")
    print(f"停止： console.py stop --project-root {project_root}")
    if not args.no_open:
        webbrowser.open(url)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    state = running_instance(project_root)
    if not state:
        print("未运行。")
        print(f"启动： console.py start --project-root {project_root}")
        return 0
    print(f"运行中：{state['url']}  (pid {state['pid']}，启动于 {state.get('started_at', '?')})")
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    state = running_instance(project_root)
    if not state:
        print("未运行；先执行 console.py start。", file=sys.stderr)
        return 1
    webbrowser.open(state["url"])
    print(f"已打开 {state['url']}")
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    state = read_state(project_root)
    if not state:
        print("未运行。")
        return 0
    pid = int(state.get("pid", 0))
    if process_alive(pid):
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"], capture_output=True)
        else:
            try:
                os.kill(pid, 15)
            except OSError:
                pass
        for _ in range(30):
            if not process_alive(pid):
                break
            time.sleep(0.1)
    clear_state(project_root)
    print(f"已停止 (pid {pid})。")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    serve(Path(args.project_root), args.port)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    commands = parser.add_subparsers(dest="command", required=True)

    start = commands.add_parser("start", help="后台启动控制台并打开浏览器")
    start.add_argument("--project-root", default=".")
    start.add_argument("--port", type=int, default=0, help=f"默认自动选择，从 {DEFAULT_PORT} 起找空闲端口")
    start.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    start.add_argument("--foreground", action="store_true", help="前台运行，Ctrl+C 结束")
    start.set_defaults(func=cmd_start)

    status = commands.add_parser("status", help="查看是否在运行以及访问地址")
    status.add_argument("--project-root", default=".")
    status.set_defaults(func=cmd_status)

    reopen = commands.add_parser("open", help="重新打开浏览器")
    reopen.add_argument("--project-root", default=".")
    reopen.set_defaults(func=cmd_open)

    stop = commands.add_parser("stop", help="停止控制台")
    stop.add_argument("--project-root", default=".")
    stop.set_defaults(func=cmd_stop)

    inner = commands.add_parser("serve", help="内部使用：在当前进程提供服务")
    inner.add_argument("--project-root", default=".")
    inner.add_argument("--port", type=int, required=True)
    inner.set_defaults(func=cmd_serve)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return int(args.func(args))
    except (GovernanceError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
