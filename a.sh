#!/bin/bash
echo "sleep"
sleep 30
check_account() {
    nordvpn account 2>&1 | grep -q "Account created:"
}

while ! check_account; do
    python3 /dock_hop/camoufox_browser.py
    [ -f ok ] && rm ok && break
done
while true; do
    timeout 400 python3 /dock_hop/cum.py
done
