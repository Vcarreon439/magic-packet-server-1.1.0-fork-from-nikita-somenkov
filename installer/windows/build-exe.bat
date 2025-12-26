@echo off

SET mydir=%~dp0
SET topdir="%mydir:~0,-1%\..\.."
SET distpath="%topdir%\dist\windows"
SET specpath="%topdir%\build\windows"
SET workpath="%topdir%\build\windows"
SET iconpath="%topdir%\installer\resources\magic-packet-icon.ico"

cd /d %topdir%

pyinstaller                             ^
    --onefile                           ^
    --nowindowed                        ^
    --noconfirm                         ^
    --hidden-import=win32timezone       ^
    --distpath=%distpath%               ^
    --workpath=%workpath%               ^
    --specpath=%specpath%               ^
    --icon=%iconpath%                   ^
    --paths=%topdir%                    ^
    worker\mpworker.py

pyinstaller                             ^
    --onefile                           ^
    --nowindowed                        ^
    --noconfirm                         ^
    --hidden-import=win32timezone       ^
    --distpath=%distpath%               ^
    --workpath=%workpath%               ^
    --specpath=%specpath%               ^
    --icon=%iconpath%                   ^
    --paths=%topdir%                    ^
    server\mpserver.py
