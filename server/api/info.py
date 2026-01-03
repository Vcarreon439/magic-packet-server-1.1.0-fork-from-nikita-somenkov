"""info.py: Info controller API"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"


import flask.blueprints
import flask.json
import flask
import sqlite3
import pathlib
import requests

info = flask.blueprints.Blueprint("info", __name__)

#Method to get server status
def check_server_status():
    _DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db"
    connection = sqlite3.connect(_DB_PATH)
    with connection:
        cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices';")
        table_exists = cursor.fetchone() is not None
        if table_exists:
            return True
        else:
            return False


# Global cache for children IPs
_children_ips_cache = []
_children_count = 0

def _update_children_cache():
    global _children_ips_cache, _children_count
    try:
        connection = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db")
        with connection:
            cursor = connection.execute("SELECT ip FROM devices;")
            _children_ips_cache = [row[0] for row in cursor.fetchall()]
            _children_count = len(_children_ips_cache)
    except sqlite3.Error:
        pass

@info.route("/info/status", methods=["GET"])
def status():
    global _children_ips_cache, _children_count
    
    try:
        is_server = check_server_status()

        if not is_server:
            return flask.json.jsonify(status=True)
        
        # Check if device count changed
        connection = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db")
        with connection:
            cursor = connection.execute("SELECT COUNT(*) FROM devices;")
            current_count = cursor.fetchone()[0]
        
        # Update cache if count changed or cache is empty
        if current_count != _children_count or not _children_ips_cache:
            _update_children_cache()
        
        children_status = []
        for ip in _children_ips_cache:
            try:
                response = requests.get(f"http://{ip}:{5154}/info/status", timeout=2)
                status_result = response.status_code == 200
            except requests.RequestException:
                status_result = False
            
            children_status.append({"ip": ip, "status": status_result})
        
        return flask.json.jsonify(status=all(child["status"] for child in children_status), children=children_status)
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return flask.json.jsonify(status=False, error=str(e))
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return flask.json.jsonify(status=False, error=str(e))


@info.route("/info/version", methods=["GET"])
def version():
    try:
        mode_server = check_server_status()
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
        