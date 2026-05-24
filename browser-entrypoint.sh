#!/bin/bash
set -e

Xvfb :1 -screen 0 1280x800x24 &
sleep 1

fluxbox &

x11vnc -display :1 -nopw -forever -quiet &

websockify --web /usr/share/novnc 6081 localhost:5900 &

sleep 2

firefox --new-instance &

echo "Browser noVNC running at http://localhost:6081/vnc.html"

tail -f /dev/null
