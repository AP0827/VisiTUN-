import socket
import os
import time
from getpass import getpass
from network.tun_interface import create_tun_interface
from network.udp_handler import UDPReceiver
from crypto.encry_decry import decrypt
from facial.face_encrypt import load_key, cam_video
from facial.landmark_encoding import get_features, get_landmarks, hybrid_key, quantize, bin_key

img_filename='live_captured_face.jpg'
key_filename='live_key.bin'
TUN_BUFFER_SIZE = 2048
LISTEN_PORT = 9090

def extract_payload(ip_packet):
    try:
        version = ip_packet[0] >> 4
        if version != 4:
            return "[!] Not an IPv4 packet"
        ihl = ip_packet[0] & 0x0F
        ip_header_len = ihl * 4
        protocol = ip_packet[9]
        if protocol != 17:  # Not UDP
            return "[!] Not a UDP packet"
        udp_data = ip_packet[ip_header_len + 8:]
        return udp_data.decode(errors="ignore")
    except:
        return "[!] Payload decode failed"

def main():
    droid_cam_video(img_filename)
    landmarks = get_landmarks(img_filename)
    if landmarks is None:
        print("❌ No landmarks found. Try again.")
        return

    features = get_features(landmarks=landmarks)
    password = getpass("🔑 Enter the password of the AES Key...")

    eye_bin = quantize(features[0], min_val=0.25, max_val=0.55, num_bins=5)
    nose_bin = quantize(features[1], min_val=0.40, max_val=0.80, num_bins=5)

    aes_key = bin_key(eye_bin, nose_bin, password=password, filename=key_filename)

    aes_key = load_key('live_key.bin')
    if not aes_key:
        print("[❌] No key loaded. Exiting.")
        return

    tun_fd, tun_name = create_tun_interface('tun1')
    print(f"[⚙️] TUN interface '{tun_name}' created. Configure it in another terminal.")

    input("[⏳] Press Enter when ready to receive packets...")

    sock = UDPReceiver(listen_port=LISTEN_PORT)
    sock.sock.settimeout(1.0)  # Set timeout to avoid indefinite blocking

    print(f"[*] Listening on UDP port {LISTEN_PORT}... Press Ctrl+C to stop.\n")

    while True:
        try:
            packet = sock.receive()
            if not packet or len(packet) < 12:
                continue  # Ignore empty or invalid packets

            nonce = packet[:12]
            ciphertext = packet[12:]

            decrypted_data = decrypt(ciphertext, nonce, aes_key)
            if not decrypted_data:
                print("[!] Failed to decrypt packet.")
                continue

            payload = extract_payload(decrypted_data)
            print(f"[📥] Decrypted packet ({len(decrypted_data)} bytes) — Payload: {payload}")

            os.write(tun_fd, decrypted_data)

        except socket.timeout:
            # No packet received — just loop silently
            continue
        except KeyboardInterrupt:
            print("\n[🔴] Receiver stopped by user.")
            break
        except Exception as e:
            print(f"[⚠️] Unexpected error: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()
