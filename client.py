import socket


def start_connection():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # --- שלב DHCP ---
    print("Step 1: DHCP Discover...")
    client.sendto("DHCP_DISCOVER".encode(), ('<broadcast>', 67))
    data, addr = client.recvfrom(1024)
    my_ip = data.decode().split(":")[1]
    print(f"Acquired IP: {my_ip}")

    # --- שלב DNS ---
    print("\nStep 2: DNS Query...")
    target_server = "my.dash.server"
    client.sendto(target_server.encode(), ('127.0.0.1', 53))
    data, addr = client.recvfrom(1024)
    server_ip = data.decode()
    print(f"Server {target_server} is at {server_ip}")

    return server_ip


if __name__ == "__main__":
    start_connection()