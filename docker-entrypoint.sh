#!/bin/bash
set -e

pulseaudio --start
exec ./TTMediaBot.sh "$@"