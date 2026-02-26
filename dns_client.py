import socket, random
from config import DNS_PORT, TIMEOUT
from packets import pack, unpack

def dns_resolve(name: str, dns_ip: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)

    xid = random.randint(1, 1_000_000)

    query = {
        "type": "DNS_QUERY",
        "xid": xid,
        "name": name
    }

    s.sendto(pack(query), (dns_ip, DNS_PORT))
    data, _ = s.recvfrom(4096)
    resp = unpack(data)

    if resp.get("xid") != xid:
        raise RuntimeError("DNS xid mismatch")

    if "ip" not in resp:
        raise RuntimeError("DNS error")

    return resp["ip"]