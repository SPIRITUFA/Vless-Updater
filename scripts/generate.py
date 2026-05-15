import os
import re
import requests
import yaml
from urllib.parse import urlparse, parse_qs, unquote

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT_DIR = "output"
OUT = f"{OUT_DIR}/proxies.yaml"

os.makedirs(OUT_DIR, exist_ok=True)

print("[INFO] downloading...")

data = requests.get(URL, timeout=30).text

# ✅ важно: сначала режем комментарии (#)
raw_links = re.findall(r'vless://[^\s"]+', data)
links = sorted(set(l.split("#")[0] for l in raw_links))

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
    return "XX"

FLAGS = {
    "RU":"🇷🇺","DE":"🇩🇪","NL":"🇳🇱","FR":"🇫🇷","FI":"🇫🇮","JP":"🇯🇵",
    "US":"🇺🇸","GB":"🇬🇧","CN":"🇨🇳","XX":"🏳️"
}

def get_flag(cc):
    return FLAGS.get(cc, "🏳️")

proxies = []
seen = set()

for line in links:
    try:
        parsed = urlparse(line)

        uuid, server = parsed.netloc.split("@")
        host, port = server.split(":")
        port = int(port)

        qs = parse_qs(parsed.query)

        pbk = qs.get("pbk", [""])[0]
        sid = qs.get("sid", [""])[0]
        sni = qs.get("sni", [""])[0]

        # ❗ нормальный уникальный ключ
        key = f"{host}:{port}:{uuid}:{sni}"
        if key in seen:
            continue
        seen.add(key)

        cc = guess_country(host)
        flag = get_flag(cc)

        name = f"{flag} {cc} | {host}:{port}"

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
            }
        })

    except Exception:
        continue

with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump(
        {"proxies": proxies},
        f,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    )

print(f"[OK] generated {len(proxies)} proxies")
