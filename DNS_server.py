import socket

# טבלת תרגום שמות (DNS Records)
DNS_TABLE = {
    "my.dash.server": "127.0.0.1"
}


def run_DNS_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('127.0.0.1', 53))  # פורט 53 סטנדרטי ל-DNS

    print("DNS Server is running...")

    while True:
        data, addr = server.recvfrom(1024)
        domain_name = data.decode()
        print(f"DNS Query received for: {domain_name}")

        # חיפוש בטבלה
        ip_address = DNS_TABLE.get(domain_name, "Not Found")
        server.sendto(ip_address.encode(), addr)


if __name__ == "__main__":
    run_DNS_server()