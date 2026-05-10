def parse_traceroute(output: str):
    hops = []
    for line in output.splitlines():
        parts = line.strip().split()
        if parts and parts[0].isdigit():
            hops.append({"hop": int(parts[0]), "raw": line.strip()})
    return hops

if __name__ == "__main__":
    sample = "1 router.local 1.2 ms\n2 10.0.0.1 4.5 ms"
    print(parse_traceroute(sample))
