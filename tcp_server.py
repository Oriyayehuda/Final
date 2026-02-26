import socket, os
from config import LOCALHOST, APP_TCP_PORT, CHUNK_SIZE

ASSETS_DIR = "assets"

def handle_client(conn):
    try:
        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                break

            if cmd == "LIST":
                files = os.listdir(ASSETS_DIR)
                response = "\n".join(files) + "\n"
                conn.sendall(response.encode())

            elif cmd.startswith("GET "):
                name = cmd[4:]
                path = os.path.join(ASSETS_DIR, name)

                if not os.path.isfile(path):
                    conn.sendall(b"ERROR\n")
                    continue

                size = os.path.getsize(path)
                conn.sendall(f"OK {size}\n".encode())

                with open(path, "rb") as f:
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        conn.sendall(chunk)

    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((LOCALHOST, APP_TCP_PORT))
    s.listen()
    print(f"[TCP] listening on {LOCALHOST}:{APP_TCP_PORT}")

    while True:
        conn, addr = s.accept()
        print("[TCP] client connected", addr)
        handle_client(conn)

if __name__ == "__main__":
    main()