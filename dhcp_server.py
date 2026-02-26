import socket, time
from config import LOCALHOST, DHCP_PORT
from packets import pack, unpack

LEASE_SECS = 3600

# DHCP "ברמה בינונית" לסימולציה: מחלק IP אחד (localhost) + DNS-IP
# אפשר להרחיב לטווח 10.0.0.X אבל אז זה לא יעבוד לסוקט אמיתי על אותו מחשב.
OFFER_IP = "127.0.0.1"
DNS_IP   = "127.0.0.1"

# שומרים leases לפי client_id
leases = {}  # client_id -> {"ip":..., "expires_at":...}

def now():
    return time.time()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((LOCALHOST, DHCP_PORT))
    print(f"[DHCP] listening on {LOCALHOST}:{DHCP_PORT}")

    while True:
        data, addr = s.recvfrom(4096)
        msg = unpack(data)
        t = msg.get("type")

        if t == "DHCP_DISCOVER":
            xid = msg.get("xid")
            client_id = msg.get("client_id")
            if xid is None or not client_id:
                continue

            offer = {
                "type": "DHCP_OFFER",
                "xid": xid,
                "client_id": client_id,
                "your_ip": OFFER_IP,
                "dns_ip": DNS_IP,
                "lease": LEASE_SECS
            }
            s.sendto(pack(offer), addr)

        elif t == "DHCP_REQUEST":
            xid = msg.get("xid")
            client_id = msg.get("client_id")
            req_ip = msg.get("requested_ip")
            if xid is None or not client_id or not req_ip:
                continue

            # מאשרים רק את ה-IP שהשרת מציע
            if req_ip != OFFER_IP:
                nack = {
                    "type": "DHCP_NACK",
                    "xid": xid,
                    "client_id": client_id,
                    "reason": "IP_NOT_AVAILABLE"
                }
                s.sendto(pack(nack), addr)
                continue

            leases[client_id] = {"ip": req_ip, "expires_at": now() + LEASE_SECS}

            ack = {
                "type": "DHCP_ACK",
                "xid": xid,
                "client_id": client_id,
                "your_ip": req_ip,
                "dns_ip": DNS_IP,
                "lease": LEASE_SECS
            }
            s.sendto(pack(ack), addr)

if __name__ == "__main__":
    main()