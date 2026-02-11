import socket
import time


def start_connection():
    # יצירת Socket UDP עבור DHCP ו-DNS [cite: 42]
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

    client.close()  # סגירת ה-UDP לפני המעבר ל-TCP/RUDP
    return server_ip


def download_dash_stream(server_ip):
    movie = "movie1"
    quality = "high"  # מתחילה באיכות גבוהה [cite: 63]

    for i in range(1, 6):
        frame_name = f"{i}.jpg"
        start_time = time.time()

        # התחברות לשרת האפליקציה ב-TCP (דרישה אחת מהשתיים)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, 8080))

        # שליחת בקשה: "סרט:איכות:פריים" [cite: 63]
        request = f"{movie}:{quality}:{frame_name}"
        sock.sendall(request.encode())

        # קבלת גודל הקובץ
        size_data = sock.recv(16).decode().strip()
        if size_data == "ERROR":
            print(f"Frame {frame_name} not found.")
            sock.close()
            break

        file_size = int(size_data)
        content = b""
        while len(content) < file_size:
            content += sock.recv(4096)

        end_time = time.time()
        duration = end_time - start_time

        print(f"Downloaded {frame_name} ({quality}) in {duration:.2f}s")

        # לוגיקת DASH אדפטיבית - מעבר בין איכויות
        if duration > 0.5:
            print("Network slow, switching to low quality...")
            quality = "low"
        else:
            quality = "high"

        sock.close()


def download_rudp(server_ip, server_port, movie, quality, frame):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request = f"RUDP_REQ:{movie}:{quality}:{frame}"
    client_sock.sendto(request.encode(), (server_ip, server_port))

    # קבלת הודעת פתיחה
    data, addr = client_sock.recvfrom(1024)
    if data.decode().startswith("START"):
        total_chunks = int(data.decode().split(":")[1])
        received_data = {}

        while len(received_data) < total_chunks:
            packet, addr = client_sock.recvfrom(35000)  # גודל מעט גדול מה-chunk

            # הפרדת ה-Header מהנתונים
            header, content = packet.split(b":", 1)
            seq_num = int(header.decode())

            print(f"Received chunk {seq_num}")
            # שליחת אישור (ACK) [cite: 49]
            client_sock.sendto(f"ACK:{seq_num}".encode(), addr)

            received_data[seq_num] = content

        # הרכבת הקובץ מחדש לפי הסדר
        full_file = b"".join([received_data[i] for i in range(total_chunks)])
        return full_file


if __name__ == "__main__":
    # שלב 1 ו-2: חיבור לרשת ותרגום שם השרת (DHCP + DNS)
    server_address = start_connection()

    print("\n--- Phase 3: DASH Stream via TCP ---")
    # הפונקציה הקיימת שלכם
    download_dash_stream(server_address)

    print("\n--- Phase 4: DASH Stream via Reliable UDP (RUDP) ---")
    # הפונקציה החדשה שהוספנו
    # נגדיר פרמטרים לדוגמה: סרט 1, איכות גבוהה, פריים מס' 1
    movie = "movie1"
    quality = "high"
    frame = "1.jpg"

    # קריאה לפונקציית ה-RUDP (וודאו שפורט 8081 הוא הפורט של שרת ה-UDP שלכם)
    content = download_rudp(server_address, 8081, movie, quality, frame)

    if content:
        print(f"Successfully downloaded {frame} via RUDP. Size: {len(content)} bytes")