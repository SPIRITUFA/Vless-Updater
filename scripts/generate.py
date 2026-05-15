import os
import re
import requests
import yaml
from urllib.parse import urlparse, parse_qs

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT_DIR = "output"
OUT = f"{OUT_DIR}/proxies.yaml"

os.makedirs(OUT_DIR, exist_ok=True)

print("[INFO] downloading...")

data = requests.get(URL, timeout=30).text

# =========================
# extract vless links (strip #comments)
# =========================
raw_links = re.findall(r'vless://[^\s"]+', data)
links = sorted(set(l.split("#")[0] for l in raw_links))

# =========================
# country guess (simple fallback)
# =========================
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
    if ".sg" in s: return "SG"
    if ".kr" in s: return "KR"
    if ".hk" in s: return "HK"
    if ".tr" in s: return "TR"
    if ".pl" in s: return "PL"
    if ".it" in s: return "IT"
    if ".es" in s: return "ES"
    return "XX"

# =========================
# AUTO FLAGS (ALL COUNTRIES)
# =========================
def get_flag(cc: str) -> str:
    if not cc or len(cc) != 2:
        return "🏳️"
    cc = cc.upper()
    return chr(0x1F1E6 + ord(cc[0]) - 65) + chr(0x1F1E6 + ord(cc[1]) - 65)

proxies = []
seen = set()

# =========================
# PARSE
# =========================
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

        # cleanup
        sid = sid.split("#")[0]
        sni = sni.split("#")[0]

        # better dedup (not just server)
        key = f"{uuid}@{host}:{port}@{sni}"
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

# =========================
# WRITE YAML
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
