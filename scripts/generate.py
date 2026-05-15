import os
import re
import requests
import yaml
import socket
import time
from urllib.parse import urlparse, parse_qs

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT_DIR = "output"
OUT = f"{OUT_DIR}/proxies.yaml"

os.makedirs(OUT_DIR, exist_ok=True)

print("[INFO] downloading...")
data = requests.get(URL, timeout=30).text

raw_links = re.findall(r'vless://[^\s"]+', data)
links = sorted(set(l.split("#")[0] for l in raw_links))


# =========================
# COUNTRY DETECTION
# =========================
def guess_region(host: str):
    host = host.lower()

    if ".ru" in host:
        return "RU"
    if any(x in host for x in [".de", ".fr", ".nl", ".pl", ".it", ".es", ".fi"]):
        return "EU"
    if any(x in host for x in [".jp", ".kr", ".cn", ".sg", ".hk", ".in"]):
        return "ASIA"
    return "OTHER"


def get_flag(region):
    return {
        "RU": "🇷🇺",
        "EU": "🇪🇺",
        "ASIA": "🌏",
        "OTHER": "🌐"
    }.get(region, "🌐")


# =========================
# LATENCY CHECK
# =========================
def check_latency(host, port, timeout=2.5):
    try:
        start = time.time()
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return round((time.time() - start) * 1000)
    except:
        return None


proxies = []
seen = set()

print("[INFO] testing nodes...")

for line in links:
    try:
        parsed = urlparse(line)

        uuid, hostport = parsed.netloc.split("@")
        host, port = hostport.split(":")
        port = int(port)

        qs = parse_qs(parsed.query)

        pbk = qs.get("pbk", [""])[0]
        sid = qs.get("sid", [""])[0]
        sni = qs.get("sni", [""])[0]

        key = f"{uuid}@{host}:{port}@{sni}"
        if key in seen:
            continue
        seen.add(key)

        latency = check_latency(host, port)

        # ❌ skip dead nodes
        if latency is None:
            continue

        region = guess_region(host)
        flag = get_flag(region)

        name = f"{flag} {region} | {host}:{port} | {latency}ms"

        proxies.append({
            "name": name,
            "type": "vless",
            "server": host,
            "port": port,
            "uuid": uuid,
            "network": "tcp",
            "tls": True,
            "udp": True,
            "servername": sni,
            "flow": "xtls-rprx-vision",
            "client-fingerprint": "chrome",
            "reality-opts": {
                "public-key": pbk or "",
                "short-id": sid or ""
            },
            "_latency": latency,
            "_region": region
        })

    except:
        continue


# =========================
# SORT BY PING
# =========================
proxies.sort(key=lambda x: x["_latency"])


# =========================
# GROUPS
# =========================
grouped = {
    "RU": [],
    "EU": [],
    "ASIA": [],
    "OTHER": []
}

for p in proxies:
    r = p["_region"]
    p.pop("_latency", None)
    p.pop("_region", None)
    grouped[r].append(p)


# =========================
# FINAL OUTPUT
# =========================
final = []
for k in ["RU", "EU", "ASIA", "OTHER"]:
    final.extend(grouped[k])

with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump(
        {"proxies": final},
        f,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

print(f"[OK] live proxies: {len(final)}")
