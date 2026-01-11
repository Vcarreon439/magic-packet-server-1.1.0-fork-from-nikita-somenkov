"""control.py: Control controller API"""

__author__ = "Nikita Somenkov, Victor Carreon"
__email__ = "somenkov.nikita@icloud.com, victor.carreon@pm.me"
__copyright__ = "Copyright 2020–2026, Nikita Somenkov & Victor Carreon"
__license__ = "GPL"

import flask
import flask.json
import flask.blueprints
import json
import typing
from wakeonlan import send_magic_packet
import sqlite3
import pathlib
import requests
import lib.connectivity

_DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db"
control = flask.blueprints.Blueprint("control", __name__)
_API_KEY_SETTING = "api_key"

def _is_server_mode() -> bool:
    return _DB_PATH.exists()

def _generic_handler(connectivity_function):
    timeout = 0

    if flask.request.is_json:
        timeout = flask.request.json.get("timeout", 0)

    response = flask.json.jsonify(
        status=True,
    )

    @response.call_on_close
    def on_close_handler():
        connectivity_function(timeout)

    return response

def _get_connectivity() -> lib.connectivity.Connectivity:
    return flask.current_app.connectivity

def _get_setting(key: str) -> typing.Optional[str]:
    if not _DB_PATH.exists():
        return None

    connection = _init_database()
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def _set_setting(key: str, value: str) -> None:
    connection = _init_database()
    with connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )

def _init_database():
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(_DB_PATH)
    with connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                mac TEXT NOT NULL,
                config TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
    return connection

def _validate_api_key():
    api_key = flask.request.headers.get("Authorization")
    if not api_key:
        return False

    stored_api_key = _get_setting(_API_KEY_SETTING)
    if not stored_api_key or api_key != stored_api_key:
        return False

    return True

@control.route("/control/shutdown", methods=["POST"])
def shutdown():



    if _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Server shutdown is not allowed."
        )
    
    connectivity_object = _get_connectivity()
    return _generic_handler(connectivity_object.shutdown)

@control.route("/control/reboot", methods=["POST"])
def reboot():

    if _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Server reboot is not allowed."
        )
    
    connectivity_object = _get_connectivity()
    return _generic_handler(connectivity_object.reboot)

@control.route("/control/sleep", methods=["POST"])
def sleep():

    if _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Server sleep is not allowed."
        )

    connectivity_object = _get_connectivity()
    return _generic_handler(connectivity_object.sleep)

@control.route("/control/server/setup", methods=["POST"])
def setup():

    #If server is already setup, return error
    if _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Server is already set up. If you want to reconfigure due to api key loss, reinstall the app."
        ), 400
    
    # Initialize database for storing server settings
    _init_database()

    if flask.request.is_json:
        api_key = flask.request.json.get("api_key")

        #If not provided or empty, generate a random one
        if not api_key or api_key == "":
            import secrets
            api_key = secrets.token_hex(16)

        if api_key:
            _set_setting(_API_KEY_SETTING, api_key)

    response = flask.json.jsonify(
        status=True,
        api_key=_get_setting(_API_KEY_SETTING),
        message="Server setup completed successfully. Please store the API key securely and restart service or device."
    )
    return response

@control.route("/control/device/configure", methods=["POST"])
def configure_device():

    if not _validate_api_key():
        return flask.json.jsonify(
            status=False,
            message="Invalid API key."
        ), 403

    if not _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Method allowed only in server mode."
        ), 400

    if not flask.request.is_json:
        return flask.json.jsonify(
            status=False,
            message="Invalid request format. JSON expected."
        ), 400

    data = flask.request.json
    ip = data.get("ip")
    mac = data.get("mac")
    config = data.get("config", {})

    if not ip or not mac:
        return flask.json.jsonify(
            status=False,
            message="Missing required fields: ip and mac."
        ), 400

    connection = _init_database()
    with connection:
        connection.execute(
            """
            INSERT INTO devices (ip, mac, config)
            VALUES (?, ?, ?)
            """,
            (ip, mac, json.dumps(config))
        )

    return flask.json.jsonify(
        status=True,
        message="Device configuration stored successfully."
    )

@control.route("/control/device/list", methods=["GET"])
def list_devices():

    if not _validate_api_key():
        return flask.json.jsonify(
            status=False,
            message="Invalid API key."
        ), 403

    if not _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Method allowed only in server mode."
        ), 400

    api_key = flask.request.headers.get("Authorization")
    
    if not api_key:
        return flask.json.jsonify(
            status=False,
            message="Missing API key in Authorization header."
        ), 401
    
    stored_api_key = _get_setting(_API_KEY_SETTING)
    if not stored_api_key or api_key != stored_api_key:
        return flask.json.jsonify(
            status=False,
            message="Invalid API key."
        ), 403
    
    connection = _init_database()
    cursor = connection.cursor()
    cursor.execute("SELECT ip, mac, config FROM devices")
    devices = [
        {
            "ip": row[0],
            "mac": row[1],
            "config": json.loads(row[2]) if row[2] else {}
        }
        for row in cursor.fetchall()
    ]

    return flask.json.jsonify(  
        status=True,
        devices=devices
    )

@control.route("/control/device/wake", methods=["POST"])
def wake_device():

    if not _validate_api_key():
        return flask.json.jsonify(
            status=False,
            message="Invalid API key."
        ), 403

    if not _is_server_mode():
        return flask.json.jsonify(
            status=False,
            message="Method allowed only in server mode."
        ), 400

    try:
        #Get device mac from request
        if not flask.request.is_json:
            return flask.json.jsonify(
                status=False,
                message="Invalid request format. JSON expected."
            ), 400
        
        data = flask.request.json
        mac = data.get("mac")   
        if not mac:
            return flask.json.jsonify(
                status=False,
                message="Missing required field: mac."
            ), 400
        
        send_magic_packet(mac)  

        return flask.json.jsonify(
            status=True,
            message=f"Wake-on-LAN packet sent to {mac}."
        )
    
    except Exception as e:
        return flask.json.jsonify(
            status=False,
            message=f"Error sending Wake-on-LAN packet: {str(e)}"
        ), 500

@control.route("/control/device/shutdown", methods=["POST"])
def shutdown_device():
    try:

        if not _validate_api_key():
            return flask.json.jsonify(
                status=False,
                message="Invalid API key."
            ), 403

        if not _is_server_mode():
            return flask.json.jsonify(
                status=False,
                message="Method allowed only in server mode."
            ), 400

        if not _is_server_mode():
            return flask.json.jsonify(
                status=False,
                message="Method allowed only in server mode."
            ), 400

        #Get device ip from request
        if not flask.request.is_json:
            return flask.json.jsonify(
                status=False,
                message="Invalid request format. JSON expected."
            ), 400
        
        data = flask.request.json
        ip = data.get("ip")   
        if not ip:
            return flask.json.jsonify(
                status=False,
                message="Missing required field: ip."
            ), 400
        
        #POST request to device shutdown endpoint
        result = requests.post(f"http://{ip}:{5154}/control/shutdown", timeout=5)

        if result.status_code != 200:
            return flask.json.jsonify(
                status=False,
                message=f"Failed to send shutdown command to {ip}. Status code: {result.status_code}"
            ), 500
        
        return flask.json.jsonify(
            status=True,
            message=f"Shutdown command sent to {ip}."
        )
    
    except Exception as e:
        return flask.json.jsonify(
            status=False,
            message=f"Error sending shutdown command: {str(e)}"
        ), 500
    
@control.route("/control/device/reboot", methods=["POST"])
def reboot_device():
    try:

        if not _validate_api_key():
            return flask.json.jsonify(
                status=False,
                message="Invalid API key."
            ), 403

        if not _is_server_mode():
            return flask.json.jsonify(
                status=False,
                message="Method allowed only in server mode."
            ), 400

        if not _is_server_mode():
            return flask.json.jsonify(
                status=False,
                message="Method allowed only in server mode."
            ), 400

        #Get device ip from request
        if not flask.request.is_json:
            return flask.json.jsonify(
                status=False,
                message="Invalid request format. JSON expected."
            ), 400
        
        data = flask.request.json
        ip = data.get("ip")   
        if not ip:
            return flask.json.jsonify(
                status=False,
                message="Missing required field: ip."
            ), 400
        
        #POST request to device reboot endpoint
        result = requests.post(f"http://{ip}:{5154}/control/reboot", timeout=5)

        if result.status_code != 200:
            return flask.json.jsonify(
                status=False,
                message=f"Failed to send reboot command to {ip}. Status code: {result.status_code}"
            ), 500
        
        return flask.json.jsonify(
            status=True,
            message=f"Reboot command sent to {ip}."
        )
    
    except Exception as e:
        return flask.json.jsonify(
            status=False,
            message=f"Error sending reboot command: {str(e)}"
        ), 500
    
@control.route("/control/device/sleep", methods=["POST"])
def sleep_device():
    try:

        if not _validate_api_key():
            return flask.json.jsonify(
                status=False,
                message="Invalid API key."
            ), 403

        if not _is_server_mode():
            return flask.json.jsonify(
                status=False,
                message="Method allowed only in server mode."
            ), 400

        #Get device ip from request
        if not flask.request.is_json:
            return flask.json.jsonify(
                status=False,
                message="Invalid request format. JSON expected."
            ), 400
        
        data = flask.request.json
        ip = data.get("ip")   
        if not ip:
            return flask.json.jsonify(
                status=False,
                message="Missing required field: ip."
            ), 400
        
        #POST request to device sleep endpoint
        result = requests.post(f"http://{ip}:{5154}/control/sleep", timeout=5)

        if result.status_code != 200:
            return flask.json.jsonify(
                status=False,
                message=f"Failed to send sleep command to {ip}. Status code: {result.status_code}"
            ), 500
        
        return flask.json.jsonify(
            status=True,
            message=f"Sleep command sent to {ip}."
        )
    
    except Exception as e:
        return flask.json.jsonify(
            status=False,
            message=f"Error sending sleep command: {str(e)}"
        ), 500