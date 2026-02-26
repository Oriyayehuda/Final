import socket, random
from config import LOCALHOST, DHCP_PORT, TIMEOUT
from packets import pack, unpack

def dhcp_get_config() -> dict:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)

    xid = random.randint(1, 1_000_000)
    client_id = f"client-{random.randint(1, 1_000_000)}"

    # 1) DISCOVER
    discover = {"type": "DHCP_DISCOVER", "xid": xid, "client_id": client_id}
    s.sendto(pack(discover), (LOCALHOST, DHCP_PORT))

    data, _ = s.recvfrom(4096)
    offer = unpack(data)

    if offer.get("type") != "DHCP_OFFER" or offer.get("xid") != xid or offer.get("client_id") != client_id:
        raise RuntimeError("DHCP bad offer")

    your_ip = offer.get("your_ip")
    dns_ip = offer.get("dns_ip")
    if not your_ip or not dns_ip:
        raise RuntimeError("DHCP offer missing fields")

    # 2) REQUEST
    req = {
        "type": "DHCP_REQUEST",
        "xid": xid,
        "client_id": client_id,
        "requested_ip": your_ip
    }
    s.sendto(pack(req), (LOCALHOST, DHCP_PORT))

    data, _ = s.recvfrom(4096)
    resp = unpack(data)

    if resp.get("xid") != xid or resp.get("client_id") != client_id:
        raise RuntimeError("DHCP xid/client mismatch")

    if resp.get("type") == "DHCP_NACK":
        raise RuntimeError("DHCP NACK: " + resp.get("reason", "unknown"))

    if resp.get("type") != "DHCP_ACK":
        raise RuntimeError("DHCP bad ack")

    return {
        "client_ip": resp["your_ip"],
        "dns_ip": resp["dns_ip"],
        "lease": resp.get("lease", 0)
    }