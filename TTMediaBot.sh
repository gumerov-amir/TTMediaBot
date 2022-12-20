#!/bin/sh

PROGNAME=TTMediaBot.py
PROGDIR=$(dirname "$(readlink -f $0)")
LD_LIBRARY_PATH=$PROGDIR:$PROGDIR/TeamTalk_DLL:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH
python3 "$PROGDIR/$PROGNAME" "$@"
