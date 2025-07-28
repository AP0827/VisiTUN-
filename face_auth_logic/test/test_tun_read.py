from network.tun_interface import create_tun_interface
import os

tun_fd, name = create_tun_interface()
print(f"TUN device '{name}' created and ready.")

while True:
    packet = os.read(tun_fd, 2048)
    print(f"\n📦 Packet received ({len(packet)} bytes)")
    print(packet[:40].hex())  # Print first 40 bytes of raw IP packet
