import socket
import os

# הגדרות שרת - וודאו שהן תואמות להגדרות הלקוח שלכם
UDP_IP = "127.0.0.1"
UDP_PORT = 8081
ASSETS_DIR = "assets"


def send_file_rudp(file_path, client_addr, server_sock):
    if not os.path.exists(file_path):
        server_sock.sendto(b"ERROR", client_addr)
        return

    with open(file_path, "rb") as f:
        file_data = f.read()

    # פיצול הקובץ לחבילות של 32KB
    chunk_size = 32768
    chunks = [file_data[i:i + chunk_size] for i in range(0, len(file_data), chunk_size)]
    total_chunks = len(chunks)

    # שליחת מספר החבילות הכולל ללקוח
    server_sock.sendto(f"START:{total_chunks}".encode(), client_addr)

    for seq_num, chunk in enumerate(chunks):
        attempt = 0
        while attempt < 5:
            # בניית חבילה: מספר סידורי + נתונים
            packet = f"{seq_num}:".encode() + chunk
            server_sock.sendto(packet, client_addr)

            server_sock.settimeout(1.0)  # המתנה של שניה ל-ACK
            try:
                ack, _ = server_sock.recvfrom(1024)
                if ack.decode() == f"ACK:{seq_num}":
                    print(f"Received ACK for chunk {seq_num}")
                    break
            except socket.timeout:
                attempt += 1
                print(f"Timeout! Retransmitting chunk {seq_num} (Attempt {attempt})")
        else:
            print(f"Failed to send chunk {seq_num} after 5 attempts.")


def main():
    # יצירת Socket מסוג UDP
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        server_sock.bind((UDP_IP, UDP_PORT))
        print(f"RUDP Server is UP and listening on {UDP_IP}:{UDP_PORT}")
    except Exception as e:
        print(f"Error binding server: {e}")
        return

    while True:
        try:
            # המתנה לבקשה חדשה מהלקוח (למשל: "movie1:high:1.jpg")
            server_sock.settimeout(None)  # ביטול ה-timeout בזמן המתנה לבקשה חדשה
            data, addr = server_sock.recvfrom(1024)
            request = data.decode()
            print(f"Request received: {request} from {addr}")

            # פירוק הבקשה לנתיב קובץ
            # הנחה: הלקוח שולח פורמט של movie:quality:frame
            parts = request.split(":")
            if len(parts) == 3:
                movie, quality, frame = parts
                file_path = os.path.join(ASSETS_DIR, movie, quality, frame)

                # קריאה לפונקציית השליחה האמינה שלך
                send_file_rudp(file_path, addr, server_sock)
                print(f"🏁 Finished handling request for {frame}")

        except Exception as e:
            print(f" Error in main loop: {e}")


if __name__ == "__main__":
    main()
