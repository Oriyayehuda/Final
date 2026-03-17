import os, time, random, socket
from config import LOCALHOST, APP_RUDP_PORT, CHUNK_SIZE, WINDOW_SIZE, RUDP_TIMEOUT, LOSS_PROB, DELAY_MS
from packets import pack, unpack

ASSETS_DIR = "assets"

def maybe_drop_or_delay():
    if random.random() < LOSS_PROB:
        return True
    if DELAY_MS > 0:
        time.sleep(DELAY_MS / 1000.0)
    return False

def sendto_sim(sock, msg, addr):
    if maybe_drop_or_delay():
        return
    sock.sendto(pack(msg), addr)

def make_chunks(path):
    with open(path, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            yield data

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((LOCALHOST, APP_RUDP_PORT))
    s.settimeout(RUDP_TIMEOUT)
    print(f"[RUDP] listening on {LOCALHOST}:{APP_RUDP_PORT}")

    sessions = {}

    while True:
        try:
            data, addr = s.recvfrom(65535)
        except socket.timeout:
            now = time.time()
            for sess in sessions.values():
                for seq, pkt in list(sess["inflight"].items()):
                    if now - pkt["sent_at"] >= RUDP_TIMEOUT:
                        pkt["sent_at"] = now
                        sendto_sim(s, pkt["msg"], sess["addr"])
            continue

        msg = unpack(data)
        t = msg.get("type")

        if t == "CMD":
            cmd = msg.get("cmd", "")
            sid = msg.get("sid")
            if sid is None:
                continue

            sess = {
                "addr": addr,
                "sid": sid,
                "next_seq": 0,
                "base": 0,
                "inflight": {},
                "queue": [],
                "done": False
            }
            sessions[addr] = sess

            if cmd == "LIST":
                files = os.listdir(ASSETS_DIR)
                payload = ("\n".join(files)).encode("utf-8")
                sess["queue"] = build_data_packets(sid, payload)

            elif cmd.startswith("GET "):
                name = cmd[4:]
                path = os.path.join(ASSETS_DIR, name)
                if not os.path.isfile(path):
                    sendto_sim(s, {"type": "ERROR", "sid": sid, "reason": "NOFILE"}, addr)
                    sessions.pop(addr, None)
                    continue
                payload = open(path, "rb").read()
                sess["queue"] = build_data_packets(sid, payload)

            else:
                sendto_sim(s, {"type": "ERROR", "sid": sid, "reason": "UNKNOWN_CMD"}, addr)
                sessions.pop(addr, None)
                continue


            send_window(s, sess)

        elif t == "ACK":
            sid = msg.get("sid")
            ack = msg.get("ack")
            sess = sessions.get(addr)
            if not sess or sess["sid"] != sid:
                continue

            if ack in sess["inflight"]:
                sess["inflight"].pop(ack, None)


            while sess["base"] not in sess["inflight"] and sess["base"] < sess["next_seq"]:
                sess["base"] += 1

            send_window(s, sess)

            if not sess["queue"] and not sess["inflight"]:
                sendto_sim(s, {"type": "FIN", "sid": sid}, addr)
                sessions.pop(addr, None)

def build_data_packets(sid, payload: bytes):
    packets = []
    seq = 0
    for i in range(0, len(payload), CHUNK_SIZE):
        chunk = payload[i:i+CHUNK_SIZE]
        packets.append({"type": "DATA", "sid": sid, "seq": seq, "data": chunk.decode("latin1")})
        seq += 1
    packets.append({"type": "DATA_END", "sid": sid, "seq": seq, "size": len(payload)})
    return packets

def send_window(sock, sess):
    now = time.time()
    while len(sess["inflight"]) < WINDOW_SIZE and sess["queue"]:
        msg = sess["queue"].pop(0)
        seq = msg["seq"]
        sess["inflight"][seq] = {"msg": msg, "sent_at": now}
        sess["next_seq"] = max(sess["next_seq"], seq + 1)
        sendto_sim(sock, msg, sess["addr"])

if __name__ == "__main__":
    main()