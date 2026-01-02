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

info = flask.blueprints.Blueprint("info", __name__)


@info.route("/info/status", methods=["GET"])
def status():
    return flask.json.jsonify(
        status=True,
    )

@info.route("/info/version", methods=["GET"])
def version():
    try:
        _DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.db"
        connection = sqlite3.connect(_DB_PATH)
        with connection:
            cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices';")
            table_exists = cursor.fetchone() is not None
            if table_exists:
                mode_server = True
            else:
                mode_server = False

        return flask.json.jsonify(
            mode_server=mode_server,
            version="1.1.0",
        )
    
    except sqlite3.Error as e:
        #show error in logs
        print(f"Database error: {e}")
        return flask.json.jsonify(
            mode_server=False,
            version="1.1.0",
        )
        