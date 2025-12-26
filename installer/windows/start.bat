@echo off
SET mydir=%~dp0
SET mpserver="%mydir:~0,-1%\mpserver.exe"
SET mpworker="%mydir:~0,-1%\mpworker.exe"

%mpserver% stop
%mpworker% stop

%mpworker% --startup=auto install || goto :error
%mpworker% start || goto :error

%mpserver% --startup=auto install || goto :error
sc config mpserver depend= "mpworker" || goto :error
%mpserver% start || goto :error
exit 0

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%
