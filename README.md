# 🔐 Encrypted TUN Communication with Facial-AES Key Auth

## 🧠 Overview

This project is a secure, low-level network communication system that:

- Creates virtual TUN interfaces on sender and receiver sides.
- Encrypts data packets using AES-GCM with a key derived from facial features.
- Transmits encrypted packets over UDP.
- Uses the TUN interface to simulate actual IP packet transmission.
- Decrypts packets only if the correct face is authenticated.

> Only the verified face of the intended user can decrypt the communication, ensuring physical access-level security.

---

## 📂 Project Structure

.
├── crypto/
│ └── encry_decry.py # AES-GCM encryption and decryption
├── facial/
│ └── face_encrypt.py # Facial feature extraction and AES key handling
├── network/
│ ├── tun_interface.py # Virtual TUN interface setup
│ └── udp_handler.py # UDP sender and receiver wrappers
├── sender.py # Sender script: reads from tun0, encrypts and sends
├── receiver.py # Receiver script: receives, decrypts and writes to tun1
├── send_custom_packet.py # Scapy tool to craft custom packets for testing
├── requirements.txt # Python dependencies
└── README.md # You're here!

yaml
Copy
Edit

---

## 📦 Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/face-secure-tun.git
   cd face-secure-tun
   Create and activate a virtual environment:
   ```

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
✅ Ensure you're running on Linux/WSL with sudo access and TUN support.

🔧 TUN Setup (WSL/Linux)
Enable TUN if not already:

bash
Copy
Edit
sudo modprobe tun
🧪 Usage
1️⃣ Generate a Face-Based AES Key
Run this once to generate a key from your face:

bash
Copy
Edit
python3 -c "from facial.face_encrypt import face_cap_ret_key; face_cap_ret_key()"
This creates a file called face_key.bin or live_key.bin.

2️⃣ Start the Receiver
bash
Copy
Edit
sudo python3 receiver.py
When prompted, configure tun1 in a new terminal:

bash
Copy
Edit
sudo ip addr add 10.8.0.1/24 dev tun1
sudo ip link set tun1 up
3️⃣ Start the Sender
In a separate terminal:

bash
Copy
Edit
sudo python3 sender.py
Configure tun0:

bash
Copy
Edit
sudo ip addr add 10.8.0.2/24 dev tun0
sudo ip link set tun0 up
4️⃣ Send Test Packet (Optional)
To test from user-level interface without TUN injection:

bash
Copy
Edit
sudo python3 send_custom_packet.py
Enter text messages and they’ll be encrypted and sent.

🔍 How It Works
sender.py reads raw IP packets from tun0, encrypts them using an AES key derived from facial features, and sends them over UDP.

receiver.py listens on UDP, decrypts the packets using the same facial key, and injects them into tun1.

You can use Scapy or applications to generate actual IP traffic for the sender to encrypt.

⚠️ Notes
Both sender.py and receiver.py require root privileges (sudo).

TUN interfaces are virtual and simulate the Linux networking stack.

Facial authentication is done once to generate the AES key.

📌 Future Additions
🔁 Face re-authentication every session

📸 Webcam fallback for facial key generation

📊 Logging system and dashboard for visualizing decrypted payloads

🌐 Remote connection support (currently local or bridged virtual network)

✅ Requirements
See requirements.txt:

txt
Copy
Edit
face_recognition
numpy
opencv-python
cryptography
scapy
Install with:

bash
Copy
Edit
pip install -r requirements.txt
🧠 Credits
face_recognition by @ageitgey

Virtual TUN concepts from Linux manpages

Cryptography using Python's cryptography library

📄 License
MIT License — use, modify, and share freely.

🙋‍♂️ Author
Aayush Pandey
Project for educational and security research.
📧 [Add contact if needed]

markdown
Copy
Edit

---

### ✅ Final Checklist Before Commit

- [ ] Save `README.md` to your repo root.
- [ ] Make sure `.gitignore` ignores any `.bin` key files.
- [ ] Add `live_key.bin` or `face_key.bin` manually to `.gitignore`.
- [ ] Test all scripts from scratch using the above instructions.

Let me know if you want help deploying this live on a GitHub repo or want a `gh-pages` doc preview!
