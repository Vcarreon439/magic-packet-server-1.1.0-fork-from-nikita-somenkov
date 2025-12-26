#!/bin/bash

set -e
set -x

topdir="$(cd "$(dirname "$(which "$0")")/../../"; pwd -P)"

mydir=$(cd $(dirname "$0"); pwd -P)
topdir=$(cd ${mydir}/../..; pwd -P)

cd ${topdir}

buildpath="${topdir}/build/linux"
distpath="${topdir}/dist/linux"

archivepath="$buildpath/archive/mpserver"

mkdir -p $archivepath

cp $distpath/mpserver $archivepath
cp $distpath/mpworker $archivepath
cp $mydir/resources/installer.sh $archivepath
chmod +x $archivepath/installer.sh

pushd $buildpath/archive
tar -pcvzf $distpath/mpserver.tar.gz mpserver
popd
