from network.udp_handler import UDPSender, UDPReceiver
import time

# Start receiver
receiver = UDPReceiver()
sender = UDPSender()

# Send a test message
sender.send(b"hello world")

# Give it a moment to travel
time.sleep(0.1)

# Try receiving
msg = receiver.receive()
if msg:
    print("✅ Received:", msg.decode())
else:
    print("❌ No data")
