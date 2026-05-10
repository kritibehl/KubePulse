import socket

def check_dns(host: str):
    try:
        ip = socket.gethostbyname(host)
        return {"host": host, "resolved_ip": ip, "status": "resolved"}
    except Exception as e:
        return {"host": host, "status": "dns_failed", "error": str(e)}

if __name__ == "__main__":
    print(check_dns("example.com"))
