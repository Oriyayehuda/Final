#TCP
import socket
import os

# הגדרות שרת - חובה להשתמש בנתיבים כלליים
SERVER_IP = "127.0.0.1"
PORT = 8080
ASSETS_DIR = "assets"  # תיקייה יחסית


def run_tcp_app_server():
    # יצירת Socket מסוג TCP (SOCK_STREAM) [cite: 45, 46]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((SERVER_IP, PORT))
        server.listen(5)
        print(f"TCP Application Server (DASH) is listening on port {PORT}...")
    except Exception as e:
        print(f"Error starting server: {e}")
        return

    while True:
        # קבלת חיבור חדש מהלקוח
        client_sock, addr = server.accept()
        print(f"Connection established with {addr}")

        try:
            # קבלת הבקשה (למשל: "movie1:high:1.jpg") [cite: 63]
            request = client_sock.recv(1024).decode()
            if not request:
                continue

            print(f"Request received: {request}")
            movie, quality, frame = request.split(":")

            # בניית נתיב לקובץ בתוך תיקיית ה-assets
            file_path = os.path.join(ASSETS_DIR, movie, quality, frame)

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    content = f.read()
                    # שליחת גודל הקובץ ב-Header קבוע של 16 בתים
                    client_sock.sendall(str(len(content)).encode().ljust(16))
                    # שליחת תוכן הקובץ (התמונה)
                    client_sock.sendall(content)
                    print(f"Sent {frame} in {quality} quality to {addr}")
            else:
                # טיפול במקרה קצה - קובץ לא קיים
                print(f"Error: File {file_path} not found")
                client_sock.sendall("ERROR".encode().ljust(16))

        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            # סגירת החיבור בסיום העברת הפרייים [cite: 28, 29]
            client_sock.close()


if __name__ == "__main__":
    run_tcp_app_server()