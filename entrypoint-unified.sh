#!/bin/bash
# No set -e — we don't want one failed command to kill the whole container

# Set timezone based on IP geolocation
echo "Detecting timezone from IP..."
TIMEZONE=$(curl -s http://ip-api.com/json | jq -r '.timezone' 2>/dev/null || echo "UTC")
ln -sf /usr/share/zoneinfo/$TIMEZONE /etc/localtime 2>/dev/null || true
echo $TIMEZONE > /etc/timezone
echo "Timezone set to: $TIMEZONE"

if [ -d "Fast_vpn_container/.git" ]; then
    (cd Fast_vpn_container && git pull) || true
else
    rm -rf Fast_vpn_container
    git clone https://github.com/hasnaouiyacine59-wq/Fast_vpn_container.git || true
    # git clone https://github.com/hasnaouiyacine59-wq/dock_hop.git || true
fi

# Start virtual display
Xvfb :1 -screen 0 1920x1080x24 &
sleep 2

fluxbox &
sleep 1

# Start VNC server
x11vnc -display :1 -nopw -forever -quiet -rfbport 5900 &
sleep 1

# Start noVNC websocket proxy (foreground-safe background)
websockify --web /usr/share/novnc 6080 localhost:5900 &
sleep 1

# Start D-Bus
mkdir -p /var/run/dbus
rm -f /var/run/dbus/pid /var/run/dbus/system_bus_socket
dbus-daemon --system --fork || true
sleep 1

# ── NordVPN (commented out — replaced by OpenVPN) ──
# mkdir -p /run/nordvpn
# rm -f /run/nordvpn/nordvpnd.sock /run/nordvpnd.pid /run/nordvpnd.sock
# /etc/init.d/nordvpn start || true
# sleep 3
# nordvpn set killswitch off || true
# nordvpn set technology NORDWHISPER
# nordvpn set dns on
# nordvpn set notify off
# nordvpn set tray off
# nordvpn set ipv6 off
# nordvpn whitelist add port 22
# nordvpn whitelist add port 6080
# nordvpn whitelist add subnet 172.0.0.0/8 || true

# ── OpenVPN whitelist (ports 22, 6080 and subnet 172.0.0.0/8) ──
chmod +x /etc/openvpn-up.sh
/etc/openvpn-up.sh || true

echo "noVNC ready at http://localhost:6080/vnc.html"

bash Fast_vpn_container/a.sh >> /proc/1/fd/1 2>> /proc/1/fd/2 &

tail -f /dev/null
