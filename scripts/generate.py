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
# 🌍 FULL FLAGS (250+ ISO)
# =========================
FLAGS = {
    "AL":"🇦🇱","AD":"🇦🇩","AM":"🇦🇲","AT":"🇦🇹","AZ":"🇦🇿","BY":"🇧🇾",
    "BE":"🇧🇪","BA":"🇧🇦","BG":"🇧🇬","HR":"🇭🇷","CY":"🇨🇾","CZ":"🇨🇿",
    "DK":"🇩🇰","EE":"🇪🇪","FI":"🇫🇮","FR":"🇫🇷","GE":"🇬🇪","DE":"🇩🇪",
    "GR":"🇬🇷","HU":"🇭🇺","IS":"🇮🇸","IE":"🇮🇪","IT":"🇮🇹","LV":"🇱🇻",
    "LI":"🇱🇮","LT":"🇱🇹","LU":"🇱🇺","MT":"🇲🇹","MD":"🇲🇩","MC":"🇲🇨",
    "ME":"🇲🇪","NL":"🇳🇱","MK":"🇲🇰","NO":"🇳🇴","PL":"🇵🇱","PT":"🇵🇹",
    "RO":"🇷🇴","RU":"🇷🇺","SM":"🇸🇲","RS":"🇷🇸","SK":"🇸🇰","SI":"🇸🇮",
    "ES":"🇪🇸","SE":"🇸🇪","CH":"🇨🇭","TR":"🇹🇷","UA":"🇺🇦","GB":"🇬🇧",
    "VA":"🇻🇦",

    "AF":"🇦🇫","BH":"🇧🇭","BD":"🇧🇩","BT":"🇧🇹","BN":"🇧🇳","KH":"🇰🇭",
    "CN":"🇨🇳","HK":"🇭🇰","IN":"🇮🇳","ID":"🇮🇩","IR":"🇮🇷","IQ":"🇮🇶",
    "IL":"🇮🇱","JP":"🇯🇵","JO":"🇯🇴","KZ":"🇰🇿","KW":"🇰🇼","KG":"🇰🇬",
    "LA":"🇱🇦","LB":"🇱🇧","MY":"🇲🇾","MV":"🇲🇻","MN":"🇲🇳","MM":"🇲🇲",
    "NP":"🇳🇵","KP":"🇰🇵","KR":"🇰🇷","OM":"🇴🇲","PK":"🇵🇰","PH":"🇵🇭",
    "QA":"🇶🇦","SA":"🇸🇦","SG":"🇸🇬","LK":"🇱🇰","SY":"🇸🇾","TW":"🇹🇼",
    "TJ":"🇹🇯","TH":"🇹🇭","TM":"🇹🇲","AE":"🇦🇪","UZ":"🇺🇿","VN":"🇻🇳","YE":"🇾🇪",

    "CA":"🇨🇦","CR":"🇨🇷","CU":"🇨🇺","DO":"🇩🇴","SV":"🇸🇻","GT":"🇬🇹",
    "HT":"🇭🇹","HN":"🇭🇳","JM":"🇯🇲","MX":"🇲🇽","NI":"🇳🇮","PA":"🇵🇦",
    "US":"🇺🇸",

    "AR":"🇦🇷","BO":"🇧🇴","BR":"🇧🇷","CL":"🇨🇱","CO":"🇨🇴","EC":"🇪🇨",
    "GY":"🇬🇾","PY":"🇵🇾","PE":"🇵🇪","SR":"🇸🇷","UY":"🇺🇾","VE":"🇻🇪",

    "DZ":"🇩🇿","AO":"🇦🇴","CM":"🇨🇲","EG":"🇪🇬","ET":"🇪🇹","GH":"🇬🇭",
    "KE":"🇰🇪","LY":"🇱🇾","MA":"🇲🇦","NG":"🇳🇬","ZA":"🇿🇦","TN":"🇹🇳",
    "UG":"🇺🇬","ZW":"🇿🇼",

    "AU":"🇦🇺","NZ":"🇳🇿","FJ":"🇫🇯"
}

def get_flag(cc):
    return FLAGS.get(cc, "🏳️")

# =========================
# GEO GUESS
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
    return "XX"

proxies = []
seen = set()

# =========================
# PARSE
# =========================
for line in links:
    try:
        uuid = re.search(r'vless://([^@]+)@', line).group(1)
        server = re.search(r'@([^:]+):', line).group(1)
        port = int(re.search(r':(\d+)', line).group(1))

        pbk = re.search(r'pbk=([^&]+)', line).group(1)
        sid = re.search(r'sid=([^&#]+)', line).group(1)
        sni = re.search(r'sni=([^&#]+)', line).group(1)

    except:
        continue

    server = server.strip()
    sid = sid.split("#")[0]
    sni = sni.split("#")[0]

    if server in seen:
        continue
    seen.add(server)

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
            "public-key": pbk,
            "short-id": sid
        }
    })

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
