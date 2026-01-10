#!/bin/bash

set -e
set -x

platform=$1
binpath=$2
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)"
topdir="$(cd "${script_dir}/../../"; pwd -P)"
pyinstaller_bin=pyinstaller

cd "$topdir"

# Used for override entry point for pyinstaller-many-linux, useful for CI build
test -n "$CONFIG_TOPDIR" && topdir="$CONFIG_TOPDIR"
test -n "$CONFIG_PYINSTALLER_BIN" && pyinstaller_bin="$CONFIG_PYINSTALLER_BIN"

distpath="$topdir/dist/$platform/$binpath"
workpath="$topdir/build/$platform"
specpath="$topdir/build/$platform"
iconpath="$topdir/installer/resources/magic-packet-icon.ico"

common_options=(
    --onefile
    --nowindowed
    --noconfirm
    --distpath=$distpath
    --workpath=$workpath
    --specpath=$specpath
    --icon=$iconpath
    --paths=$topdir
)

$pyinstaller_bin ${common_options[@]} worker/mpworker.py
$pyinstaller_bin ${common_options[@]} server/mpserver.py
