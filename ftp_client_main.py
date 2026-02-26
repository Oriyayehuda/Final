from dhcp_client import dhcp_get_config
from dns_client import dns_resolve
from tcp_client import main as tcp_main
from rudp_client import main as rudp_main

def main():
    cfg = dhcp_get_config()
    print("[DHCP] got:", cfg)

    app_ip = dns_resolve("app.local", cfg["dns_ip"])
    print("[DNS] app.local ->", app_ip)

    proto = input("Choose protocol (tcp/rudp): ").strip().lower()
    if proto == "tcp":
        tcp_main(app_ip)
    elif proto == "rudp":
        rudp_main()  # ואם עשית שינוי לקבל server_ip, תעבירי: rudp_main(app_ip)
    else:
        print("Invalid. choose tcp or rudp")

if __name__ == "__main__":
    main()