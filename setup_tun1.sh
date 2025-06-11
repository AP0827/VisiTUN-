#!/bin/bash
sudo ip tuntap add dev tun1 mode tun
sudo ip addr add 10.8.0.2/24 dev tun1
sudo ip link set dev tun1 up
sudo ip route add 10.8.0.1 dev tun1
