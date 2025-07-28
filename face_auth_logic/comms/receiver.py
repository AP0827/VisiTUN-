import socket
import os
import time
from getpass import getpass
from network.tun_interface import create_tun_interface
from network.udp_handler import UDPReceiver
from crypto.encry_decry import decrypt
from facial.face_encrypt import load_key, cam_video
from facial.landmark_encoding import get_features, get_landmarks, quantize, bin_key
from threading import Thread, Lock

img_filename = 'live_captured_face.jpg'
key_filename = 'live_key.bin'
TUN_BUFFER_SIZE = 2048
LISTEN_PORT = 9090

auth_lock = Lock()
shared_state = {
    "aes_key": None,
    "authenticated": False,
    "terminate": False
}

def authenticate_face(shared_state, password, interval=5.0):
    while not shared_state["terminate"]:
        time.sleep(interval)

        cam_video(img_filename)
        landmarks = get_landmarks(img_filename)

        if landmarks is None:
            print("❌ Either No face or Multiple people. GET OUT OR GET BACK HERE.")
            continue

        try:
            features = get_features(landmarks=landmarks)

            eye_bin = quantize(features[0], min_val=0.30, max_val=0.52, num_bins=5)
            nose_len_bin = quantize(features[1], min_val=0.45, max_val=0.70, num_bins=5)
            nose_wid_bin = quantize(features[2], min_val=0.25, max_val=0.45, num_bins=5)
            v_shape_bin = quantize(features[3], min_val=1.5, max_val=2.3, num_bins=5)

            _ = bin_key(eye_bin, nose_len_bin, nose_wid_bin, v_shape_bin, password=password, filename=key_filename)
            new_key = load_key(key_filename)
            with auth_lock:
                shared_state["aes_key"] = new_key
                shared_state["authenticated"] = True

            print("✅ Face authenticated successfully.")

        except Exception as e:
            print(f"[Auth Error] {e}")
            with auth_lock:
                shared_state["authenticated"] = False

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
    print("📷 Adjust your camera, then press 'q' to capture.")
    cam_video(img_filename)

    password = getpass("🔑 Enter your AES password: ")
    print("🔁 Starting background face authentication...")

    auth_thread = Thread(target=authenticate_face, args=(shared_state, password), daemon=True)
    auth_thread.start()

    tun_fd, tun_name = create_tun_interface('tun1')
    print(f"[⚙️] TUN interface '{tun_name}' created. Configure it manually.")

    input("[⏳] Press Enter when ready to start packet reception...")

    sock = UDPReceiver(listen_port=LISTEN_PORT)
    sock.sock.settimeout(1.0)

    print(f"📡 Listening on UDP port {LISTEN_PORT}. Press Ctrl+C to exit.\n")

    try:
        while True:
            packet = None
            try:
                packet = sock.receive()
            except socket.timeout:
                continue

            if not packet or len(packet) < 12:
                continue

            nonce = packet[:12]
            ciphertext = packet[12:]

            with auth_lock:
                if not shared_state["authenticated"]:
                    print("[🔒] Skipping packet — not authenticated.")
                    continue
                current_key = shared_state["aes_key"]

            decrypted_data = decrypt(ciphertext, nonce, current_key)
            if not decrypted_data:
                print("[❌] Packet decryption failed.")
                continue

            payload = extract_payload(decrypted_data)
            print(f"[📥] Decrypted packet ({len(decrypted_data)} bytes): {payload}")

            os.write(tun_fd, decrypted_data)

    except KeyboardInterrupt:
        print("\n[🔴] Receiver terminated by user.")

    finally:
        shared_state["terminate"] = True
        print("💤 Shutting down cleanly...")

if __name__ == "__main__":
    main()
