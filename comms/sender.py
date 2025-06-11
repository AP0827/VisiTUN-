import os
import socket
from network.tun_interface import create_tun_interface
from network.udp_handler import UDPSender
from crypto.encry_decry import encrypt
from facial.face_encrypt import load_key, encoding_to_key

DEST_IP = "127.0.0.1"       
DEST_PORT = 9090            
TUN_BUFFER_SIZE = 2048

def main():
    aes_key = load_key()

    tun_fd, tun_name = create_tun_interface()
    print(f"[+] TUN interface '{tun_name}' created and ready.")

    sock = UDPSender()

    print("[*] Sender started. Reading from TUN and sending encrypted packets...")
    while True:
        try:
            packet = os.read(tun_fd, TUN_BUFFER_SIZE)

            ciphertext, nonce = encrypt(packet, aes_key)

            packet_out = nonce + ciphertext

            sock.send(packet_out)

            print(f"[📤] Packet sent: {len(packet_out)} bytes")

        except KeyboardInterrupt:
            print("\n[!] Sender stopped by user.")
            break

if __name__ == "__main__":
    main()
