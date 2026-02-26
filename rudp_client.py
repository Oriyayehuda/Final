import socket, random, time
from config import LOCALHOST, APP_RUDP_PORT, RUDP_TIMEOUT
from packets import pack, unpack

def send(sock, msg, addr):
    sock.sendto(pack(msg), addr)

def rudp_cmd(cmd: str, server_ip="127.0.0.1") -> bytes:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(RUDP_TIMEOUT)
    addr = (server_ip, APP_RUDP_PORT)

    sid = random.randint(1, 1_000_000)
    send(s, {"type": "CMD", "sid": sid, "cmd": cmd}, addr)

    received = {}
    end_seq = None
    total_size = None

    while True:
        try:
            data, _ = s.recvfrom(65535)
        except socket.timeout:
            # just keep listening; server will retransmit
            continue

        msg = unpack(data)
        if msg.get("sid") != sid:
            continue

        if msg["type"] == "ERROR":
            raise RuntimeError(msg.get("reason", "ERROR"))

        if msg["type"] == "DATA":
            seq = msg["seq"]
            if seq not in received:
                received[seq] = msg["data"].encode("latin1")
            send(s, {"type": "ACK", "sid": sid, "ack": seq}, addr)

        elif msg["type"] == "DATA_END":
            end_seq = msg["seq"]
            total_size = msg["size"]
            send(s, {"type": "ACK", "sid": sid, "ack": end_seq}, addr)

        elif msg["type"] == "FIN":
            break

    # rebuild payload
    out = b""
    if end_seq is None:
        return b""
    for i in range(0, end_seq):
        out += received.get(i, b"")
    return out[:total_size]

def main():
    while True:
        cmd = input("> ")
        if cmd == "exit":
            break
        if cmd == "LIST":
            data = rudp_cmd("LIST")
            print(data.decode(errors="ignore"))
        elif cmd.startswith("GET "):
            data = rudp_cmd(cmd)
            print("---- FILE CONTENT ----")
            print(data.decode(errors="ignore"))
            print("----------------------")
        else:
            print("Commands: LIST | GET <file> | exit")

if __name__ == "__main__":
    main()