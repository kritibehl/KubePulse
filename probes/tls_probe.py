import socket
import ssl
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 443

context = ssl.create_default_context()

try:
    with socket.create_connection((host, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls:
            cert = tls.getpeercert()
            print({
                "probe": "tls",
                "host": host,
                "port": port,
                "tls_version": tls.version(),
                "cipher": tls.cipher()[0] if tls.cipher() else None,
                "certificate_subject": cert.get("subject"),
                "certificate_issuer": cert.get("issuer"),
                "not_after": cert.get("notAfter"),
                "healthy": True
            })
except Exception as exc:
    print({
        "probe": "tls",
        "host": host,
        "port": port,
        "healthy": False,
        "error": str(exc)
    })
    raise SystemExit(1)
