"""windows.py: Windows worker specific implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import os
import sys
import ctypes
import typing
import time

import win32event
import win32service
import win32serviceutil
import servicemanager

import lib.messages
import worker.specific.shared


class MagicPacketWorkerService (win32serviceutil.ServiceFramework):
    _svc_name_ = "mpworker"
    _svc_display_name_ = "Magic Packet Worker"
    _svc_description_ = "Is waiting for commands from the pipe and executes them"

    run: typing.Callable
    stop: typing.Callable

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        MagicPacketWorkerService.stop()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        MagicPacketWorkerService.run()


class WindowsWorkerRunner(worker.specific.shared.WorkerRunner):
    def __init__(self):
        super().__init__()
        self.no_service = False

    def get_specific_logger_options(self) -> dict:
        directory = os.path.join(os.getenv('APPDATA'), "Magic Packet Service", "logs")
        if not os.path.exists(directory):
            os.makedirs(directory)
        return dict(filename=os.path.join(directory, "mpworker.log"))

    def handle_args(self):
        super().handle_args()

        if "noservice" in sys.argv:
            self.no_service = True
            return

        if len(sys.argv) <= 1:
            return

        # In Windows platform we should exit after handling args
        rc = win32serviceutil.HandleCommandLine(MagicPacketWorkerService)
        sys.exit(rc)

    def setup(self):
        super().setup()

        if self.no_service:
            return

        if len(sys.argv) > 1:
            sys.exit(-1)

        # We should call shared version of run in MagicPacketWorkerService.SvcDoRun()
        MagicPacketWorkerService.run = super().run
        MagicPacketWorkerService.stop = super().stop

        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MagicPacketWorkerService)

    def run(self):
        if self.no_service:
            super().run()
            return

        servicemanager.StartServiceCtrlDispatcher()

    def system_shutdown(self, message: lib.messages.ShutdownMessage):
        os.system(f"shutdown /s /t {message.timeout}")

    def system_reboot(self, message: lib.messages.RebootMessage):
        os.system(f"shutdown /r /t {message.timeout}")

    def system_sleep(self, message: lib.messages.SleepMessage):
        time.sleep(message.timeout)
        ctypes.windll.powrprof.SetSuspendState(False, True, False)
