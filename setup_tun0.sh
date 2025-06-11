#!/bin/bash
sudo ip tuntap add dev tun0 mode tun
sudo ip addr add 10.8.0.1/24 dev tun0
sudo ip link set dev tun0 up
sudo ip route add 10.8.0.2 dev tun0
