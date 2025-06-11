import socket

class UDPSender:
    def __init__(self, dest_ip='127.0.0.1', dest_port=9090):
        self.dest_addr = (dest_ip,dest_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send(self, data:bytes):
        self.sock.sendto(data, self.dest_addr)


class UDPReceiver:
    def __init__(self, listen_ip = '0.0.0.0', listen_port = 9090):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_ip,listen_port))
        self.sock.setblocking(False)

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            return data
        except BlockingIOError:
            return None
