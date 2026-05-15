import os
import re
import requests
import yaml

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT = "output/proxies.yaml"

os.makedirs("output", exist_ok=True)

print("[INFO] downloading...")

data = requests.get(URL, timeout=30).text

links = sorted(set(re.findall(r'vless://[^"]+', data)))

proxies = []
seen = set()

for line in links:

    try:
        uuid = re.search(r'vless://([^@]+)@', line).group(1)
        server = re.search(r'@([^:]+):', line).group(1)
        port = int(re.search(r':(\d+)', line).group(1))

        pbk = re.search(r'pbk=([^&]+)', line).group(1)
        sid = re.search(r'sid=([^&]+)', line).group(1)
        sni = re.search(r'sni=([^&#]+)', line).group(1)

    except:
        continue

    # =========================
    # CLEAN DATA (ВАЖНО)
    # =========================
    sid = sid.split("#")[0].split("%")[0]   # убираем мусор
    server = server.strip()
    sni = sni.split("#")[0]

    if server in seen:
        continue
    seen.add(server)

    # =========================
    # SIMPLE GEO (можешь улучшить позже)
    # =========================
    cc = "RU"
    if ".us" in server: cc = "US"
    elif ".de" in server: cc = "DE"
    elif ".nl" in server: cc = "NL"
    elif ".fi" in server: cc = "FI"
    elif ".fr" in server: cc = "FR"
    elif ".jp" in server: cc = "JP"
    elif ".sg" in server: cc = "SG"

    # =========================
    # FLAG SAFE MAP
    # =========================
    flags = {
        "RU": "🇷🇺",
        "US": "🇺🇸",
        "DE": "🇩🇪",
        "NL": "🇳🇱",
        "FI": "🇫🇮",
        "FR": "🇫🇷",
        "JP": "🇯🇵",
        "SG": "🇸🇬",
    }

    flag = flags.get(cc, "🏳️")

    # =========================
    # SAFE NODE NAME (CRITICAL)
    # =========================
    name = f"{flag} {cc} | {server}:{port}"

    proxies.append({
        "name": name,
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
# WRITE YAML (CLEAN)
# =========================
with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump(
        {"proxies": proxies},
        f,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

print(f"[OK] generated {len(proxies)} proxies")
