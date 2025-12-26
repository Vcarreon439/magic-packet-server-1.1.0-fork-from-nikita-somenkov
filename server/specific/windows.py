""""shared.py: Shared start point of Magic Packet Server Server"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import os
import sys
import json
import typing
import urllib
import urllib.request

import flask
import flask.json
import flask.blueprints
import win32event
import win32service
import win32serviceutil
import servicemanager

import server.specific.shared

stop_server = flask.blueprints.Blueprint("stop-server", __name__)


@stop_server.route("/specific/stop-server", methods=["POST"])
def force_stop_server():
    really_stop_server = False

    if flask.request.is_json:
        really_stop_server = flask.request.json.get("we-really-want-to-stop-server", False)

    if really_stop_server:
        stop_function = flask.request.environ.get('werkzeug.server.shutdown')
        if stop_function is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        stop_function()
        return 'Server was stopped'
    else:
        return "Stop server command was ignored"


class MagicPacketServerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "mpserver"
    _svc_display_name_ = "Magic Packet Server"
    _svc_description_ = "Flask server listening incoming commands and redirect to Magic Packet Worker (mpworker)"

    run: typing.Callable = None
    stop: typing.Callable = None
    port = 0

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        request = urllib.request.Request(f"http://localhost:{MagicPacketServerService.port}/specific/stop-server")
        request.add_header("Content-Type", "application/json")
        request.data = json.dumps({"we-really-want-to-stop-server": True}).encode()
        request.method = "POST"

        urllib.request.urlopen(request)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        MagicPacketServerService.run()


class WindowsServerRunner(server.specific.shared.ServerRunner):
    def __init__(self):
        super().__init__()
        self.no_service = False

    def get_specific_logger_options(self) -> dict:
        directory = os.path.join(os.getenv('APPDATA'), "Magic Packet Service", "logs")
        if not os.path.exists(directory):
            os.makedirs(directory)
        return dict(filename=os.path.join(directory, "mpserver.log"))

    def handle_args(self):
        super().handle_args()

        if "noservice" in sys.argv:
            self.no_service = True
            return

        if len(sys.argv) <= 1:
            return

        # In Windows platform we should exit after handling args
        rc = win32serviceutil.HandleCommandLine(MagicPacketServerService)
        sys.exit(rc)

    def setup(self):
        super().setup()

        self.app.register_blueprint(stop_server)

        if self.no_service:
            return

        if len(sys.argv) > 1:
            sys.exit(-1)

        # We should call shared version of run in MagicPacketWorkerService.SvcDoRun()
        MagicPacketServerService.run = super().run
        MagicPacketServerService.port = self.port

        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MagicPacketServerService)

    def run(self):
        if self.no_service:
            super().run()
            return
        servicemanager.StartServiceCtrlDispatcher()
