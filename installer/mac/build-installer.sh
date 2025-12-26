#!/bin/bash

set -e

mydir=$(cd $(dirname "$0"); pwd -P)
topdir=$(cd ${mydir}/../..; pwd -P)

cd ${topdir}

distpath="${topdir}/dist/mac"
buildpath="${topdir}/build/mac"

version=1.0

mkdir -p ${buildpath}
mkdir -p ${distpath}

rm ${distpath}/mpserver.dmg || true

function make_pkg() {
    local type=$1
    local pkgversion=${version}

    pkgbuild --root ${distpath}                           \
             --scripts ${mydir}/${type}-scripts           \
             --identifier ru.somenkov.mpserver.${type}    \
             --version ${pkgversion}                      \
             --ownership recommended                      \
             ${buildpath}/${type}.pkg
}

make_pkg Installer
make_pkg Uninstaller

cat <<ENDL >${buildpath}/settings.py
files = [
    "${buildpath}/Installer.pkg",
    "${buildpath}/Uninstaller.pkg",
]
ENDL

dmgbuild -s ${buildpath}/settings.py "Magic Packet Server" "${distpath}/mpserver-installer.dmg"
