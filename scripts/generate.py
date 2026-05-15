import requests
import yaml
import re
import os

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT = "output/proxies.yaml"

# =========================
# CREATE OUTPUT DIR
# =========================
os.makedirs("output", exist_ok=True)

# =========================
# FLAGS
# =========================
FLAGS = {
    "RU": "🇷🇺",
    "US": "🇺🇸",
    "DE": "🇩🇪",
    "NL": "🇳🇱",
    "FI": "🇫🇮",
    "FR": "🇫🇷",
    "GB": "🇬🇧",
    "SG": "🇸🇬",
    "JP": "🇯🇵",
    "KR": "🇰🇷",
    "HK": "🇭🇰",
    "TR": "🇹🇷",
}

# =========================
# DOWNLOAD JSON
# =========================
print("[INFO] Downloading keys.json...")

resp = requests.get(URL, timeout=30)
resp.raise_for_status()

data = resp.text

# =========================
# PARSE LINKS
# =========================
links = sorted(set(re.findall(r'vless://[^"]+', data)))

print(f"[INFO] Found {len(links)} links")

proxies = []
seen = set()

# =========================
# PARSE NODES
# =========================
for line in links:

    try:
        uuid = re.search(r'vless://([^@]+)@', line).group(1)

        server = re.search(r'@([^:]+):', line).group(1)

        port = int(re.search(r':(\d+)', line).group(1))

        pbk = re.search(r'pbk=([^&]+)', line).group(1)

        sid = re.search(r'sid=([^&]+)', line).group(1)

        sni = re.search(r'sni=([^&#]+)', line).group(1)

    except Exception:
        continue

    # =========================
    # VALIDATION
    # =========================
    if not all([uuid, server, port, pbk, sid, sni]):
        continue

    if server in seen:
        continue

    seen.add(server)

    # =========================
    # COUNTRY DETECT
    # =========================
    cc = "RU"

    if ".jp" in server:
        cc = "JP"

    elif ".sg" in server:
        cc = "SG"

    elif ".hk" in server:
        cc = "HK"

    elif ".kr" in server:
        cc = "KR"

    elif ".tr" in server:
        cc = "TR"

    elif ".de" in server:
        cc = "DE"

    elif ".nl" in server:
        cc = "NL"

    elif ".fi" in server:
        cc = "FI"

    elif ".fr" in server:
        cc = "FR"

    elif ".uk" in server or ".gb" in server:
        cc = "GB"

    elif ".us" in server:
        cc = "US"

    flag = FLAGS.get(cc, "🏳️")

    proxies.append({
        "name": f"{flag} {cc} | {server}:{port}",
        "type": "vless",
        "server": server,
        "port": port,
        "uuid": uuid,
        "network": "tcp",
        "tls": True,
        "udp": True,
        "servername": sni,
        "flow": "xtls-rprx-vision",
        "client-fingerprint": "chrome",
        "reality-opts": {
            "public-key": pbk,
            "short-id": sid
        }
    })

# =========================
# SAVE YAML
# =========================
yaml_data = {
    "proxies": proxies
}

with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump(
        yaml_data,
        f,
        allow_unicode=True,
        sort_keys=False
    )

print(f"[INFO] Generated {len(proxies)} proxies")
print(f"[INFO] Saved to {OUT}")
