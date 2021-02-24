import struct
import socket

from .constants import UDP_READSIZE, IGMP_ADDRESS, IGMP_PORT, VERB_ANSWER, \
    VERB_DISCOVER


def createsocket(timeout=None):
    """Create a udp socket for IGMP multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if timeout:
        sock.settimeout(timeout)

    return sock


def readpacket(sock):
    data, host = sock.recvfrom(UDP_READSIZE)
    return data[0], data[1:].decode(), host[0], host[1]


def createpacket(verb, data):
    header = struct.pack('>B', verb)
    return header + data.encode()


def resolve(hostname, timeout=None):
    sock = createsocket(timeout)
    sock.sendto(
        createpacket(VERB_DISCOVER, hostname),
        (IGMP_ADDRESS, IGMP_PORT)
    )
    while True:
        verb, name, addr, _ = readpacket(sock)
        if (verb == VERB_ANSWER) and (name == hostname):
            return addr


def sniff():
    sock = createsocket()
    sock.bind((IGMP_ADDRESS, IGMP_PORT))
    mreq = struct.pack(
        '4sl',
        socket.inet_aton(IGMP_ADDRESS),
        socket.INADDR_ANY
    )
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        yield readpacket(sock)


def find(pattern, timeout=None):
    sock = createsocket(timeout)
    sock.sendto(
        createpacket(VERB_DISCOVER, pattern),
        (IGMP_ADDRESS, IGMP_PORT)
    )
    while True:
        verb, name, addr, _ = readpacket(sock)
        if verb == VERB_ANSWER:
            yield name, addr


def answer(name, address=IGMP_ADDRESS, port=IGMP_PORT):
    sock = createsocket()
    sock.sendto(createpacket(VERB_ANSWER, name), (address, port))
