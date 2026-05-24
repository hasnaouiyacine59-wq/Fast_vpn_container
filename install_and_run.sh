#!/bin/bash
# Combined install + runtime script (replaces Dockerfile.unified + entrypoint-unified.sh)
# Run as root on Ubuntu 22.04

export DEBIAN_FRONTEND=noninteractive

# ── System packages ──────────────────────────────────────────────────────────
apt-get update && apt-get install -y \
    curl ca-certificates gnupg wget \
    python3 python3-pip \
    iproute2 iptables \
    xvfb x11vnc novnc websockify fluxbox xterm \
    git jq dbus \
    libgtk-3-0 libdbus-glib-1-2 libasound2 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# ── NordVPN ───────────────────────────────────────────────────────────────────
curl -sSf https://repo.nordvpn.com/gpg/nordvpn_public.asc \
    | gpg --dearmor -o /usr/share/keyrings/nordvpn.gpg
echo "deb [signed-by=/usr/share/keyrings/nordvpn.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" \
    > /etc/apt/sources.list.d/nordvpn.list
apt-get update && apt-get install -y nordvpn && rm -rf /var/lib/apt/lists/*

# ── Python packages + camoufox ───────────────────────────────────────────────
pip3 install --timeout 300 --retries 5 -r requirements.txt
python3 -m camoufox fetch

# ── Timezone ──────────────────────────────────────────────────────────────────
echo "Detecting timezone from IP..."
TIMEZONE=$(curl -s http://ip-api.com/json | jq -r '.timezone' 2>/dev/null || echo "UTC")
ln -sf /usr/share/zoneinfo/$TIMEZONE /etc/localtime 2>/dev/null || true
echo "$TIMEZONE" > /etc/timezone
echo "Timezone set to: $TIMEZONE"

# ── Repo ──────────────────────────────────────────────────────────────────────
if [ -d "dock_hop/.git" ]; then
    (cd dock_hop && git pull) || true
else
    rm -rf dock_hop
    git clone https://github.com/hasnaouiyacine59-wq/dock_hop.git || true
fi

# ── Display ───────────────────────────────────────────────────────────────────
export DISPLAY=:1
Xvfb :1 -screen 0 1920x1080x24 & sleep 2
fluxbox & sleep 1
x11vnc -display :1 -nopw -forever -quiet -rfbport 5900 & sleep 1
websockify --web /usr/share/novnc 6080 localhost:5900 & sleep 1

# ── D-Bus ─────────────────────────────────────────────────────────────────────
mkdir -p /var/run/dbus /run/nordvpn
rm -f /var/run/dbus/pid /var/run/dbus/system_bus_socket
dbus-daemon --system --fork || true
sleep 1

# ── NordVPN daemon + config ───────────────────────────────────────────────────
rm -f /run/nordvpn/nordvpnd.sock /run/nordvpnd.pid /run/nordvpnd.sock
/etc/init.d/nordvpn start || true
sleep 3
nordvpn set killswitch off || true
nordvpn whitelist add subnet 172.0.0.0/8 || true
nordvpn set technology openvpn
nordvpn set protocol tcp
nordvpn set ipv6 off
nordvpn whitelist add port 22

# ── Launch ────────────────────────────────────────────────────────────────────
echo "noVNC ready at http://localhost:6080/vnc.html"
bash dock_hop/camoufox_browser.py >> /proc/1/fd/1 2>> /proc/1/fd/2 &
bash dock_hop/a.sh >> /proc/1/fd/1 2>> /proc/1/fd/2 &

tail -f /dev/null
