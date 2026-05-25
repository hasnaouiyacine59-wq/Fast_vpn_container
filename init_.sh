#!/bin/bash
docker rm -f $(docker ps -aq)
docker pull quay.io/mylastres0rt05_redhat/fast_vpn_container:latest

docker run -d \
  --name n-1 \
  --hostname fast_b_gate_1 \
  --privileged \
  --device /dev/net/tun \
  quay.io/mylastres0rt05_redhat/fast_vpn_container:latest



docker run -d \
  --name n-2 \
  --hostname fast_b_gate_2 \
  --privileged \
  --device /dev/net/tun \
  quay.io/mylastres0rt05_redhat/fast_vpn_container:latest



docker run -d \
  --name n-3 \
  --hostname fast_b_gate_3 \
  --privileged \
  --device /dev/net/tun \
  quay.io/mylastres0rt05_redhat/fast_vpn_container:latest



docker run -d \
  --name n-4 \
  --hostname fast_b_gate_4 \
  --privileged \
  --device /dev/net/tun \
  quay.io/mylastres0rt05_redhat/fast_vpn_container:latest
sleep 60
docker logs -f n-1 &
docker logs -f n-2 &
docker logs -f n-3 &
docker logs -f n-4 &

#docker exec n-1 python3 dock_hop/camoufox_browser.py &
#docker exec n-2 python3 dock_hop/camoufox_browser.py &


#docker exec n-1 python3 dock_hop/camoufox_browser.py &
#docker exec n-2 python3 dock_hop/camoufox_browser.py &
