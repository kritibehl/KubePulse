import socket

def check_tcp(host: str, port: int, timeout: float = 3.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"host": host, "port": port, "status": "connected"}
    except Exception as e:
        return {"host": host, "port": port, "status": "failed", "error": str(e)}

if __name__ == "__main__":
    print(check_tcp("example.com", 443))
