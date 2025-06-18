# 🔐 Encrypted TUN Communication with Facial-AES Key Auth

## 🧠 Overview

This project is a **secure, low-level network communication** system that:

- Creates **virtual TUN interfaces** on sender and receiver sides.
- Encrypts data packets using AES-GCM with a key derived from facial landmark geometry (not volatile encodings).
- Transmits encrypted packets over UDP.
- Uses the TUN interface to simulate actual IP packet transmission.
- Decrypts packets only if the correct face and password are used to regenerate the key.

> Only the verified face of the intended user can decrypt the communication, ensuring physical access-level security.

This approach uses **quantized facial geometry** (like eye distance and nose-to-chin ratio normalized by face width) to produce **stable**, **reproducible** values, which are binned into discrete ranges. These bin values, **combined with a user password**, produce a **consistent AES key** even with minor facial variation — enabling reliable encryption and decryption.

---

## 📂 Project Structure

- crypto/
  - encry_decry.py # AES-GCM encryption and decryption
- facial/
  - face_encrypt.py # Facial feature extraction and AES key handling
  - landmark_encoding.py # Extract facial landmarks and quantize them to create the key
- network/
  - tun_interface.py # Virtual TUN interface setup
  - udp_handler.py # UDP sender and receiver wrappers
- comms/
  - sender.py # Sender script: reads from tun0, encrypts and sends
  - receiver.py # Receiver script: receives, decrypts and writes to tun1
  - send_custom_packet.py # Scapy tool to craft custom packets for testing
- requirements.txt
- README.md

---

## 📦 Installation

1. Clone this repo:

   ```bash
   git clone https://github.com/YOUR_USERNAME/face-secure-tun.git
   cd face-secure-tun
   ```

   Create and activate a virtual environment:

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   ✅ Ensure you're running on Linux/WSL with sudo access and TUN support.

3. TUN Setup (WSL/Linux)
   Enable TUN if not already:

   ```
   sudo modprobe tun
   ```

## 🧪 Usage

### 1️⃣ Start the Receiver

```
sudo python3 receiver.py
```

When prompted, configure tun1 in a new terminal:

```
sudo ip addr add 10.8.0.1/24 dev tun1
sudo ip link set tun1 up
```

The script will ask for your facial image (captured from DroidCam or webcam) and a password. It uses quantized landmark distances (e.g., eye distance, nose-to-chin length) mapped to discrete bins and hashed along with the password to derive a reproducible AES key.

### 2️⃣ Start the Sender

In a separate terminal:

```
sudo python3 sender.py
```

Configure tun0:

```
sudo ip addr add 10.8.0.2/24 dev tun0
sudo ip link set tun0 up
```

The sender script will also capture a facial image and request the same password. If the facial geometry and password match those used on the receiver, communication will succeed.

### 3️⃣ Send Custom Test Packet

To test from user-level interface without TUN injection:

```
sudo python3 send_custom_packet.py
```

Type a message, and it will be encrypted, transmitted via UDP, decrypted on the other end, and shown as the payload.

## 🔍 How It Works

- sender.py reads raw IP packets from tun0
- encrypts them using an AES key derived from facial features
- sends them over UDP

- receiver.py listens on UDP
- decrypts the packets using the same/live facial key
- injects them into tun1.

You can use Scapy or applications to generate actual IP traffic for the sender to encrypt.

## ⚠️ Notes

- Both sender.py and receiver.py require root privileges (sudo).
- TUN interfaces are virtual and simulate the Linux networking stack.
- Facial authentication is done once to generate the AES key.

## 📌 Future Additions

- 🔁 Face re-authentication every session
- 📸 Webcam fallback for facial key generation
- 📊 Logging system and dashboard for visualizing decrypted payloads
- 🌐 Remote connection support (currently local or bridged virtual network)

## 🧠 Credits

- face_recognition by @ageitgey

- Virtual TUN concepts from Linux manpages

- Cryptography using Python's cryptography library

## 🙋‍♂️ Author

Aayush Pandey

Project for educational and security research.

---
