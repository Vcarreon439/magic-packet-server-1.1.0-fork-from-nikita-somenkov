"""info.py: Info controller API"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"


import flask.blueprints
import flask.json
import flask

info = flask.blueprints.Blueprint("info", __name__)


@info.route("/info/status", methods=["GET"])
def status():
    return flask.json.jsonify(
        status=True,
    )


@info.route("/info/version", methods=["GET"])
def version():
    return flask.json.jsonify(
        version="1.1.0",
    )
