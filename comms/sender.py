import os
import socket
from getpass import getpass
from network.tun_interface import create_tun_interface
from network.udp_handler import UDPSender
from crypto.encry_decry import encrypt
from facial.face_encrypt import load_key, encoding_to_key, cam_video
from facial.landmark_encoding import get_features,get_landmarks, hybrid_key, quantize, bin_key


key_filename = 'face_key.bin'
img_filename = 'face.jpg'

DEST_IP = "127.0.0.1"       
DEST_PORT = 9090            
TUN_BUFFER_SIZE = 2048

def main():
    droid_cam_video(img_filename)
    landmarks = get_landmarks('face.jpg')
    if landmarks is None:
        print("❌ No landmarks found. Try again.")
        return

    features = get_features(landmarks=landmarks)
    password = getpass("🔑 Enter the password of the AES Key...")

    eye_bin = quantize(features[0], min_val=0.25, max_val=0.55, num_bins=5)
    nose_bin = quantize(features[1], min_val=0.40, max_val=0.80, num_bins=5)

    aes_key = bin_key(eye_bin, nose_bin, password=password, filename=key_filename)

    tun_fd, tun_name = create_tun_interface()
    print(f"[+] TUN interface '{tun_name}' created and ready.")

    sock = UDPSender()

    print("[*] Sender started. Reading from TUN and sending encrypted packets...")
    while True:
        try:
            packet = os.read(tun_fd, TUN_BUFFER_SIZE)
            print(f"[🐾] Read from TUN: {len(packet)} bytes")
            ciphertext, nonce = encrypt(packet, aes_key)

            packet_out = nonce + ciphertext

            sock.send(packet_out)

            print(f"[📤] Packet sent: {len(packet_out)} bytes")

        except KeyboardInterrupt:
            print("\n[!] Sender stopped by user.")
            break

if __name__ == "__main__":
    main()
