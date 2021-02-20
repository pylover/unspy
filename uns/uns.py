import struct
import socket
import unittest


VERB_DISCOVER = 1
VERB_ANSWER = 2


GRP = '224.0.0.70'
PORT = 5333
TARGET = (GRP, PORT)
READSIZE = 128


def createsocket(timeout=None):
    """Create a udp socket for IGMP multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if timeout:
        sock.settimeout(timeout)

    return sock


def readpacket(sock):
    data, host = sock.recvfrom(READSIZE)
    return data[0], data[1:].decode(), host[0], host[1]


def createpacket(verb, data):
    header = struct.pack('>B', VERB_DISCOVER)
    return header + data.encode()


def resolve(hostname, timeout):
    sock = createsocket(timeout)
    sock.sendto(createpacket(VERB_DISCOVER, hostname), TARGET)
    while True:
        verb, name, addr, _ = readpacket(sock)
        if (verb == VERB_ANSWER) and (name == hostname):
            return name, addr
