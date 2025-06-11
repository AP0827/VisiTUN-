from scapy.all import IP, UDP, Raw, send
import signal

running = True

def handle_exit(sig, frame):
    global running
    print("\n[!] Exiting...")
    running = False

signal.signal(signal.SIGINT, handle_exit)

SRC_IP = "10.8.0.1"
DST_IP = "10.8.0.2"
SRC_PORT = 1234
DST_PORT = 9090

print("📨 Type messages to send over the network. Ctrl+C to stop.\n")

while running:
    try:
        msg = input(">> ").strip()
        if not msg:
            continue
        pkt = IP(src=SRC_IP, dst=DST_IP) / UDP(sport=SRC_PORT, dport=DST_PORT) / Raw(load=msg.encode())
        send(pkt, verbose=False)
        print(f"[+] Packet sent: {len(msg)} bytes")
    except Exception as e:
        print(f"[x] Error: {e}")
