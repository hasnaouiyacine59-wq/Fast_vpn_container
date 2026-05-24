#!/bin/bash
# Called by OpenVPN after tunnel is up (--up /etc/openvpn-up.sh)
# Equivalent of nordvpn whitelist: allow ports 22, 6080 and subnet 172.0.0.0/8
# through the physical interface, bypassing the VPN tunnel.

PHY=$(ip route | awk '/default/ && !/tun/ {print $5; exit}')

# Allow inbound/outbound on port 22 via physical interface
iptables -I INPUT  -i "$PHY" -p tcp --dport 22 -j ACCEPT
iptables -I OUTPUT -o "$PHY" -p tcp --sport 22 -j ACCEPT

# Allow inbound/outbound on port 6080 via physical interface
iptables -I INPUT  -i "$PHY" -p tcp --dport 6080 -j ACCEPT
iptables -I OUTPUT -o "$PHY" -p tcp --sport 6080 -j ACCEPT

# Allow inbound/outbound on port 6081 via physical interface
iptables -I INPUT  -i "$PHY" -p tcp --dport 6081 -j ACCEPT
iptables -I OUTPUT -o "$PHY" -p tcp --sport 6081 -j ACCEPT

# Allow subnet 172.0.0.0/8 to bypass VPN (route via physical interface)
ip route add 172.0.0.0/8 via "$ROUTE_GATEWAY" dev "$PHY" 2>/dev/null || true
iptables -I INPUT  -s 172.0.0.0/8 -j ACCEPT
iptables -I OUTPUT -d 172.0.0.0/8 -j ACCEPT

echo "[ovpn-up] whitelist applied: ports 22,6080,6081 + subnet 172.0.0.0/8 via $PHY"
