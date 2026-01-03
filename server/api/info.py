"""info.py: Info controller API"""

__author__ = "Nikita Somenkov, Victor Carreon"
__email__ = "somenkov.nikita@icloud.com, victor.carreon@pm.me"
__copyright__ = "Copyright 2020–2026, Nikita Somenkov & Victor Carreon"
__license__ = "GPL"

import pathlib, sqlite3, threading
import flask, flask.json, flask.blueprints
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

info = flask.blueprints.Blueprint("info", __name__)

_DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db"

# ---- Cache & lock (thread-safe) ----
_cache_lock = threading.Lock()
_children_ips_cache = []
_children_count = 0
_is_server_cached = None  # opcional: cachear resultado

def check_server_status_cached():
    """Evita consultar sqlite_master en cada request."""
    global _is_server_cached
    if _is_server_cached is not None:
        return _is_server_cached
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            cur = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='devices' LIMIT 1;"
            )
            _is_server_cached = (cur.fetchone() is not None)
    except sqlite3.Error:
        _is_server_cached = False
    return _is_server_cached

def _update_children_cache():
    global _children_ips_cache, _children_count
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            cur = conn.execute("SELECT ip FROM devices;")
            ips = [row[0] for row in cur.fetchall()]
        with _cache_lock:
            _children_ips_cache = ips
            _children_count = len(ips)
    except sqlite3.Error:
        # no rompas la ruta por fallas de cache
        pass

def _get_children_ips():
    """Lee COUNT y refresca cache solo si cambió."""
    global _children_count
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM devices;")
            current_count = cur.fetchone()[0]
    except sqlite3.Error:
        return []

    with _cache_lock:
        needs_refresh = (current_count != _children_count) or (not _children_ips_cache)

    if needs_refresh:
        _update_children_cache()

    with _cache_lock:
        return list(_children_ips_cache)  # copia segura

def _check_child(session: requests.Session, ip: str):
    url = f"http://{ip}:5154/info/status"
    try:
        # timeout=(connect, read)
        r = session.get(url, timeout=(0.5, 0.8))
        ok = (r.status_code == 200)
    except requests.RequestException:
        ok = False
    return {"ip": ip, "status": ok}

@info.route("/info/status", methods=["GET"])
def status():
    try:
        is_server = check_server_status_cached()
        if not is_server:
            return flask.json.jsonify(status=True)

        ips = _get_children_ips()

        # Concurrencia: ajusta según tu #children y hardware
        max_workers = min(32, max(4, len(ips)))  # ejemplo
        children_status = []

        with requests.Session() as session:
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=64, pool_maxsize=64, max_retries=0
            )
            session.mount("http://", adapter)

            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                futures = [ex.submit(_check_child, session, ip) for ip in ips]
                for f in as_completed(futures):
                    children_status.append(f.result())

        overall = all(c["status"] for c in children_status)
        # opcional: ordenar para respuesta estable
        return flask.json.jsonify(status=True, children=children_status)

    except sqlite3.Error as e:
        return flask.json.jsonify(status=False, error=str(e))
    except Exception as e:
        return flask.json.jsonify(status=False, error=str(e))

@info.route("/info/version", methods=["GET"])
def version():
    try:
        mode_server = check_server_status_cached()
        return flask.json.jsonify(
            mode_server=mode_server,
            version="1.1.1",
        )
    
    except sqlite3.Error as e:
        #show error in logs
        print(f"Database error: {e}")
        return flask.json.jsonify(
            mode_server=False,
            version="1.1.1",
        )
        