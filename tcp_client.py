import socket
from config import LOCALHOST, APP_TCP_PORT

def main(server_ip="127.0.0.1"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, APP_TCP_PORT))

    while True:
        cmd = input("> ")
        if cmd == "exit":
            break

        s.sendall((cmd + "\n").encode())

        if cmd == "LIST":
            print(s.recv(4096).decode())

        elif cmd.startswith("GET "):
            header = b""
            while b"\n" not in header:
                part = s.recv(1)
                if not part:
                    print("Server closed connection")
                    break
                header += part

            header = header.decode().strip()

            if not header.startswith("OK "):
                print("Error from server")
                continue

            size = int(header.split()[1])

            data = b""
            while len(data) < size:
                chunk = s.recv(min(4096, size - len(data)))
                if not chunk:
                    print("Server closed connection early")
                    break
                data += chunk

            print("---- FILE CONTENT ----")
            print(data.decode(errors="ignore"))
            print("----------------------")

    s.close()

if __name__ == "__main__":
    main()