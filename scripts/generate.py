import os
import re
import requests
import yaml

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT_DIR = "output"
OUT = f"{OUT_DIR}/proxies.yaml"

os.makedirs(OUT_DIR, exist_ok=True)

print("[INFO] downloading...")

data = requests.get(URL, timeout=30).text
links = sorted(set(re.findall(r'vless://[^"\s]+', data)))

# =========================
# FLAGS
# =========================
FLAGS = {
    "RU":"🇷🇺","US":"🇺🇸","DE":"🇩🇪","FR":"🇫🇷","NL":"🇳🇱","FI":"🇫🇮",
    "JP":"🇯🇵","KR":"🇰🇷","SG":"🇸🇬","HK":"🇭🇰","CN":"🇨🇳","GB":"🇬🇧",
    "PL":"🇵🇱","TR":"🇹🇷","GE":"🇬🇪","CY":"🇨🇾","XX":"🏳️"
}

def get_flag(cc):
    return FLAGS.get(cc, "🏳️")

def guess_country(server: str):
    s = server.lower()
    if ".ru" in s: return "RU"
    if ".de" in s: return "DE"
    if ".nl" in s: return "NL"
    if ".fr" in s: return "FR"
    if ".fi" in s: return "FI"
    if ".jp" in s: return "JP"
    if ".us" in s: return "US"
    if ".uk" in s: return "GB"
    if ".cn" in s: return "CN"
    if ".ge" in s: return "GE"
    return "XX"

def clean(x):
    if not x:
        return ""
    return x.split("#")[0].strip()

proxies = []
seen = set()

for line in links:
    try:
        uuid = re.search(r'vless://([^@]+)@', line).group(1)
        server = re.search(r'@([^:]+):', line).group(1)
        port = int(re.search(r':(\d+)', line).group(1))

        pbk = re.search(r'pbk=([^&]+)', line)
        sid = re.search(r'sid=([^&#]+)', line)
        sni = re.search(r'sni=([^&#]+)', line)

        pbk = pbk.group(1) if pbk else ""
        sid = sid.group(1) if sid else ""
        sni = sni.group(1) if sni else server

    except:
        continue

    server = clean(server)
    sni = clean(sni)
    sid = clean(sid)

    # IMPORTANT: dedupe by server+port (НЕ только server)
    key = f"{server}:{port}"
    if key in seen:
        continue
    seen.add(key)

    cc = guess_country(server)
    flag = get_flag(cc)

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
            "public-key": pbk or "",
            "short-id": sid or ""
        }
    })

with open(OUT, "w", encoding="utf-8") as f:
    yaml.safe_dump(
        {"proxies": proxies},
        f,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

print(f"[OK] generated {len(proxies)} proxies")
