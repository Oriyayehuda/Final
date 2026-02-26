import socket
from config import LOCALHOST, DNS_PORT
from packets import pack, unpack

DNS_TABLE = {
    "app.local": "127.0.0.1",
    "dns.local": "127.0.0.1"
}

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((LOCALHOST, DNS_PORT))
    print(f"[DNS] listening on {LOCALHOST}:{DNS_PORT}")

    while True:
        data, addr = s.recvfrom(4096)
        msg = unpack(data)

        if msg.get("type") != "DNS_QUERY":
            continue

        name = msg.get("name")
        xid = msg.get("xid")

        ip = DNS_TABLE.get(name)
        if ip is None:
            response = {
                "type": "DNS_RESPONSE",
                "xid": xid,
                "error": "NXDOMAIN"
            }
        else:
            response = {
                "type": "DNS_RESPONSE",
                "xid": xid,
                "ip": ip
            }

        s.sendto(pack(response), addr)

if __name__ == "__main__":
    main()