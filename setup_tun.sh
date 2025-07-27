sudo ip link set tun0 down
sudo ip link set tun1 down
sudo ip addr del 10.8.0.1/24 dev tun0
sudo ip addr del 10.8.0.2/24 dev tun1

sudo ip route del 10.8.0.0/24 dev tun0
sudo ip route del 10.8.0.0/24 dev tun1

# Create tun0 and tun1 if your script doesn't already
sudo ip tuntap add dev tun0 mode tun
sudo ip tuntap add dev tun1 mode tun

# Assign IP addresses
sudo ip addr add 10.8.0.1/24 dev tun0
sudo ip addr add 10.8.0.2/24 dev tun1

# Bring interfaces up
sudo ip link set tun0 up
sudo ip link set tun1 up

# Add routes if needed (might not be mandatory if all is local)
sudo ip route add 10.8.0.0/24 dev tun0
sudo ip route add 10.8.0.0/24 dev tun1
