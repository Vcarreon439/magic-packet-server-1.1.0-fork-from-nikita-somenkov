#!/bin/bash

set -e
set -x

topdir="$(cd "$(dirname "$(which "$0")")/../../"; pwd -P)"

$topdir/installer/shared/build-exe.sh mac usr/local/bin
