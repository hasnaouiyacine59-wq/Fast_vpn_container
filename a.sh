#!/bin/bash
echo "sleep"
sleep 30
check_account() {
    nordvpn account 2>&1 | grep -q "Account created:"
}

# while ! check_account; do
    # python3 /Fast_vpn_container/camoufox_browser.py
    # [ -f ok ] && rm ok && break
# done
while true; do
    timeout 500 python3 /Fast_vpn_container/cum.py
done
