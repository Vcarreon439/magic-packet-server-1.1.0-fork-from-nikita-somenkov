"""control.py: Control controller API"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import flask
import flask.json
import flask.blueprints

import lib.connectivity

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
