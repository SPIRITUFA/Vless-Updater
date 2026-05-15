import os
import re
import requests
import yaml

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"
OUT = "output/proxies.yaml"

os.makedirs("output", exist_ok=True)

print("[INFO] downloading...")

data = requests.get(URL, timeout=30).text

links = list(set(re.findall(r'vless://[^"\s]+', data)))

proxies = []

# =========================
# REAL GEO MAP (domain-based fallback)
# =========================
def detect_country(server):
    s = server.lower()

    if any(x in s for x in ["ru", "moscow", "msk"]):
        return "RU"
    if any(x in s for x in ["de", "germany", "fra", "berlin"]):
        return "DE"
    if any(x in s for x in ["nl", "netherlands", "amsterdam"]):
        return "NL"
    if any(x in s for x in ["fr", "france", "paris"]):
        return "FR"
    if any(x in s for x in ["us", "ny", "usa", "miami", "la"]):
        return "US"
    if any(x in s for x in ["jp", "tokyo"]):
        return "JP"
    if any(x in s for x in ["sg", "singapore"]):
        return "SG"
    if any(x in s for x in ["fi", "finland", "helsinki"]):
        return "FI"

    return "XX"

# =========================
# FLAGS
# =========================
flags = {
    "RU": "🇷🇺","US": "🇺🇸","DE": "🇩🇪","NL": "🇳🇱",
    "FR": "🇫🇷","JP": "🇯🇵","SG": "🇸🇬","FI": "🇫🇮",
    "XX": "🌍"
}

print("[INFO] parsing nodes...")

for i, line in enumerate(links):

    try:
        uuid = re.search(r'vless://([^@]+)@', line).group(1)
        server = re.search(r'@([^:]+):', line).group(1)
        port = int(re.search(r':(\d+)', line).group(1))

        pbk = re.search(r'pbk=([^&]+)', line)
        sid = re.search(r'sid=([^&]+)', line)
        sni = re.search(r'sni=([^&#]+)', line)

        if not (pbk and sid and sni):
            continue

        pbk = pbk.group(1)
        sid = sid.group(1).split("#")[0]
        sni = sni.group(1).split("#")[0]

    except:
        continue

    cc = detect_country(server)
    flag = flags.get(cc, "🌍")

    # ⚠️ ВАЖНО: НЕ режем по server (это убивало разнообразие)
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

print("[INFO] total before dedup:", len(proxies))

# =========================
# SMART DEDUP (NOT KILLING VARIETY)
# =========================
unique = []
seen = set()

for p in proxies:
    key = (p["server"], p["port"], p["uuid"])
    if key in seen:
        continue
    seen.add(key)
    unique.append(p)

# =========================
# WRITE YAML
# =========================
with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump(
        {"proxies": unique},
        f,
        allow_unicode=True,
        sort_keys=False
    )

print(f"[OK] final proxies: {len(unique)}")
