"""The map's page: plain HTTP and HTML forms, no JavaScript, the page reloading itself every 2 s
(bata/SOFTWARE.md, *The map*). One page: the questions first, then a table by line; the settings
only in the service mode. Storož's state shown, with no button: resuming stays over SSH.
"""
from __future__ import annotations

import html
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .core import Map
from .lists import PLACES

STYLE = ("body{font-family:sans-serif;margin:1em}table{border-collapse:collapse}"
         "td,th{border:1px solid #888;padding:.2em .5em}.missing{color:#a00}"
         ".ask{background:#ffd}form{display:inline;margin:0}")


def page(m: Map, storoz: str) -> str:
    e = html.escape
    out = [f"<!doctype html><meta charset=utf-8><meta http-equiv=refresh content=2>"
           f"<title>The suit's map</title><style>{STYLE}</style><h1>The suit's map</h1>",
           f"<p>Storož: {e(storoz)}. Mode: {'service' if m.service else 'measuring'}.</p>"]
    for q in m.questions():
        places = "".join(f"<option value={p}>{p} {e(PLACES[p])}</option>"
                         for p in m.free_places(q.line))
        blink = ("its LED blinks" if m.blinking == q.uid else
                 f"<form method=post action=/ask><input type=hidden name=uid value={e(q.uid)}>"
                 f"<button>blink its LED</button></form>")
        choose = (f"<form method=post action=/answer><input type=hidden name=uid "
                  f"value={e(q.uid)}><select name=place>{places}</select>"
                  f"<button>this place</button></form>" if places else
                  "no place of the line is free: forget a missing unit first")
        out.append(f"<p class=ask>Line {q.line}: which place is the unit "
                   f"{e(q.uid[-4:].upper())}? {blink} {choose}</p>")
    out.append("<table><tr><th>line</th><th>place</th><th>UID</th><th>kind</th><th>number</th>"
               "<th>firmware</th><th>state</th><th>bias</th><th>strip's ground</th>"
               "<th>IMU mode</th><th>diagnostics</th></tr>")
    for r in m.table():
        state = "present" if r["present"] else "missing"
        if r["replaces"]:
            state += (f", replaces {e(r['replaces'])} <form method=post action=/confirm>"
                      f"<input type=hidden name=uid value={e(r['uid'])}><button>confirm"
                      f"</button></form>")
        if not r["present"]:
            state += (f" <form method=post action=/forget><input type=hidden name=uid "
                      f"value={e(r['uid'])}><button>forget</button></form>")
        module = r["kind"] == "module"               # the bias a module's; the glove's and the
        settings = ([("yes" if r["bias"] else "no") if module else "",     # sock's the rest
                     ("driven" if r["shield"] else "ground"), str(r["imu_mode"])]
                    if r["sensing"] else ["", "", ""])
        if m.service and r["sensing"]:
            u = e(r["uid"])
            settings = [
                f"<form method=post action=/set><input type=hidden name=uid value={u}>"
                f"<input type=hidden name=bias value={0 if r['bias'] else 1}>"
                f"<button>{'yes' if r['bias'] else 'no'}</button></form>" if module else "",
                f"<form method=post action=/set><input type=hidden name=uid value={u}>"
                f"<input type=hidden name=shield value={0 if r['shield'] else 1}>"
                f"<button>{'driven' if r['shield'] else 'ground'}</button></form>",
                f"<form method=post action=/set><input type=hidden name=uid value={u}>"
                f"<input name=imu_mode value={r['imu_mode']} size=2><button>set</button></form>"]
        d = r["diagnostics"]
        diag = ", ".join(f"{e(str(k))} {e(str(v))}" for k, v in d.items()) if d else ""
        cls = "" if r["present"] else " class=missing"
        out.append(f"<tr{cls}><td>{r['line']}</td><td>{r['place'] or ''} "
                   f"{e(r['place_name'])}</td><td>{e(r['uid4'])}"
                   f"{' (blinking)' if r['blinking'] else ''}</td><td>{e(r['kind'])}</td>"
                   f"<td>{r['number']:#04x}</td><td>{r['firmware'] or ''}</td><td>{state}</td>"
                   + "".join(f"<td>{s}</td>" for s in settings) + f"<td>{diag}</td></tr>")
    out.append("</table>")
    return "".join(out)


def serve(m: Map, host: str = "127.0.0.1", port: int = 8080,
          storoz: Callable[[], str] = lambda: "unknown",
          blink: Callable[[str | None], None] = lambda uid: None) -> ThreadingHTTPServer:
    """The page on host:port, Baťa's local network's address, never a public one. `blink` tells
    the Mamka link which unit's LED to blink (None: none)."""
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):                      # quiet
            pass

        def do_GET(self):
            if self.path != "/":
                self.send_error(404)
                return
            with lock:
                body = page(m, storoz()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            form = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
            uid = form.get("uid", "")
            try:
                with lock:
                    if uid not in m.units:
                        raise ValueError("no such unit")
                    if self.path == "/answer":
                        m.answer(uid, int(form["place"]))
                        blink(None)
                    elif self.path == "/ask":
                        m.ask(uid)
                        blink(uid)
                    elif self.path == "/confirm":
                        m.confirm(uid)
                    elif self.path == "/forget":
                        m.forget(uid)
                    elif self.path == "/set":
                        m.set(uid, bias=bool(int(form["bias"])) if "bias" in form else None,
                              shield=int(form["shield"]) if "shield" in form else None,
                              imu_mode=int(form["imu_mode"]) if "imu_mode" in form else None)
                    else:
                        self.send_error(404)
                        return
            except (ValueError, KeyError, PermissionError) as exc:
                self.send_error(400, str(exc))
                return
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

    return ThreadingHTTPServer((host, port), Handler)
