import fcntl
import os
import struct
import select

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_NO_PI = 0x1000


def create_tun_interface(name='tun0'):
    tun = os.open('/dev/net/tun', os.O_RDWR)

    ifr = struct.pack('16sH', name.encode(), IFF_NO_PI|IFF_TUN)

    fcntl.ioctl(tun,TUNSETIFF,ifr)

    return tun, name