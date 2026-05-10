import subprocess

def curl_check(url: str):
    result = subprocess.run(
        ["curl", "-I", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
        capture_output=True,
        text=True,
    )
    return {"url": url, "http_status": result.stdout.strip()}

if __name__ == "__main__":
    print(curl_check("https://example.com"))
