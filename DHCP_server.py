import socket


def run_DHCP_server():
    # יצירת Socket UDP
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # האזנה לפורט 67 (סטנדרטי ל-DHCP)
    server.bind(('0.0.0.0', 67))

    print("DHCP Server is running and waiting for Discover...")

    while True:
        data, addr = server.recvfrom(1024)
        message = data.decode()

        if message == "DHCP_DISCOVER":
            print(f"Received Discover from {addr}")
            # שליחת Offer עם כתובת IP "מוצעת"
            offered_ip = "192.168.1.50"
            server.sendto(f"DHCP_OFFER:{offered_ip}".encode(), addr)
            print(f"Sent Offer: {offered_ip}")


if __name__ == "__main__":
    run_DHCP_server()