"""control.py: Control controller API"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import flask
import flask.json
import flask.blueprints
import json
from wakeonlan import send_magic_packet
import sqlite3
import pathlib

import lib.connectivity

_DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db"
control = flask.blueprints.Blueprint("control", __name__)


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
    return connection


@control.route("/control/shutdown", methods=["POST"])
def shutdown():
    connectivity_object = _get_connectivity()
    return _generic_handler(connectivity_object.shutdown)


@control.route("/control/reboot", methods=["POST"])
def reboot():
    connectivity_object = _get_connectivity()
    return _generic_handler(connectivity_object.reboot)


@control.route("/control/sleep", methods=["POST"])
def sleep():
    connectivity_object = _get_connectivity()
    return _generic_handler(connectivity_object.sleep)


#Route for server setup
@control.route("/control/server/setup", methods=["POST"])
def setup():
    # Initialize database for storing server settings
    _init_database()
    response = flask.json.jsonify(
        status=True,
        message="Server setup completed successfully."
    )
    return response

#Router for store device configuration
@control.route("/control/device/configure", methods=["POST"])
def configure_device():
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

#Route for controling remote devices
@control.route("/control/device/wake", methods=["POST"])
def wake_device():

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

   