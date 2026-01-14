#!/bin/bash

set -e

default_prefix="/usr/bin"
default_systemd_prefix="/usr/lib/systemd/system"
default_data_dir="/var/lib/mpserver"

function usage() {
    echo ""
    echo "Magic Packet Server Installer"
    echo ""
    echo "./installer.sh <install|uninstall>"
    echo ""
    echo "             --prefix=<path> - binary prefix (default=$default_prefix)"
    echo "     --systemd-prefix=<path> - custom systemd prefix (default=$default_systemd_prefix)"
    echo ""
    exit 1
}

topdir="$(cd "$(dirname "$(which "$0")")"; pwd -P)"
mode=
prefix=$default_prefix
systemd_prefix=$default_systemd_prefix

for opt ; do
    case "${opt}" in
        install) mode=install;;
        uninstall) mode=uninstall;;
        --prefix=*) prefix="${opt#--prefix=}";;
        --systemd-prefix=*) systemd_prefix="${opt#--systemd-prefix=}";;
        -h|--help|--usage|help) usage;;
        *)
            echo ""
            echo "Unknown option: '$opt'"
            usage;;
    esac
done

if ! type systemctl &> /dev/null; then
    echo ""
    echo "You don't seem to be using systemd"
    echo ""
    echo "So, just add mpserver and mpworker binaries to autostart"
    echo "Or write to developer here:"
    echo "https://apps.somenkov.ru/magic-packet/support/"
    echo ""
    exit 3
fi

if (( $EUID != 0 )); then
    echo ""
    echo "Please run as root:"
    echo "  $ sudo ./installer.sh <options>"
    echo ""
    exit 2
fi

function generate_systemd() {
    local description="$1"
    local binary="$2"
    local path="$3"
    local user="$4"
    local depend="$4"
    local depend="$5"
    local data_dir="$6"

    cat >"$path" <<ENDL
[Unit]
Description=$description
ENDL

    if test -n "$user"; then
        cat >>"$path" <<ENDL
User=$user
Group=$user
ENDL
    fi

    if test -n "$depend"; then
        cat >>"$path" <<ENDL
Requires=$depend
ENDL
    fi

    cat >>"$path" <<ENDL

[Service]
ExecStart=$binary
Environment=MP_DATA_DIR=$data_dir

[Install]
WantedBy=multi-user.target
ENDL
}

function do_install() {
    if ! test -d $prefix; then
        echo ""
        echo "Failed to install: \"$prefix\" do not exist"
        echo ""
        exit 4
    fi

    if ! test -d $systemd_prefix; then
        echo ""
        echo "Failed to install: \"$systemd_prefix\" do not exist"
        echo ""
        exit 4
    fi

    cp "$topdir/mpserver" "$prefix"
    cp "$topdir/mpworker" "$prefix"

    if ! id mpserver &>/dev/null; then
        useradd --comment "Magic Packet Server User" --no-create-home --system mpserver
    fi

    install -d -m 750 -o mpserver -g mpserver "$default_data_dir"

    generate_systemd "Magic Packet Worker" "$prefix/mpworker" "$systemd_prefix/mpworker.service" "" "" "$default_data_dir"
    generate_systemd "Magic Packet Server" "$prefix/mpserver" "$systemd_prefix/mpserver.service" mpserver mpworker.service "$default_data_dir"

    systemctl enable --quiet mpworker
    systemctl enable --quiet mpserver

    systemctl start mpworker
    systemctl start mpserver

    echo ""
    echo "Magic Packet Server was installed"
    echo ""
}

function warn() {
    echo "warning: $1"
}

function do_uninstall() {
    systemctl stop mpserver || warn "cannot stop mpserver"
    systemctl stop mpworker || warn "cannot stop mpworker"

    systemctl disable --quiet mpworker || warn "cannot disable mpworker.service"
    systemctl disable --quiet mpserver || warn "cannot disable mpserver.service"

    rm "$systemd_prefix/mpworker.service" || warn "cannot remove $systemd_prefix/mpworker.service"
    rm "$systemd_prefix/mpserver.service" || warn "cannot remove $systemd_prefix/mpserver.service"

    if id mpserver &>/dev/null; then
        userdel mpserver || warn "cannot delete user mpserver"
    fi

    rm "$prefix/mpserver" || warn "cannot remove mpserver from $prefix/mpserver"
    rm "$prefix/mpworker" || warn "cannot remove mpworker from $prefix/mpworker"

    echo ""
    echo "Magic Packet Server was uninstalled"
    echo ""
}

case $mode in
    install) do_install;;
    uninstall) do_uninstall;;
    *)
        echo ""
        echo "Specify what you want to do uninstall or install"
        usage;;
esac
