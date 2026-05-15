import re
import os
import yaml
import requests
import time
import socket
from urllib.parse import parse_qs

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT = "output/proxies.yaml"
CACHE = "/tmp/geo_cache.txt"

os.makedirs("output", exist_ok=True)

# =========================
# FULL FLAGS MAP (ALL YOUR LIST)
# =========================
FLAGS = {
    # Europe
    "AL":"🇦🇱","AD":"🇦🇩","AM":"🇦🇲","AT":"🇦🇹","AZ":"🇦🇿","BY":"🇧🇾",
    "BE":"🇧🇪","BA":"🇧🇦","BG":"🇧🇬","HR":"🇭🇷","CY":"🇨🇾","CZ":"🇨🇿",
    "DK":"🇩🇰","EE":"🇪🇪","FI":"🇫🇮","FR":"🇫🇷","GE":"🇬🇪","DE":"🇩🇪",
    "GR":"🇬🇷","HU":"🇭🇺","IS":"🇮🇸","IE":"🇮🇪","IT":"🇮🇹","LV":"🇱🇻",
    "LI":"🇱🇮","LT":"🇱🇹","LU":"🇱🇺","MT":"🇲🇹","MD":"🇲🇩","MC":"🇲🇨",
    "ME":"🇲🇪","NL":"🇳🇱","MK":"🇲🇰","NO":"🇳🇴","PL":"🇵🇱","PT":"🇵🇹",
    "RO":"🇷🇴","RU":"🇷🇺","SM":"🇸🇲","RS":"🇷🇸","SK":"🇸🇰","SI":"🇸🇮",
    "ES":"🇪🇸","SE":"🇸🇪","CH":"🇨🇭","TR":"🇹🇷","UA":"🇺🇦","GB":"🇬🇧","VA":"🇻🇦",

    # Asia
    "AF":"🇦🇫","BH":"🇧🇭","BD":"🇧🇩","BT":"🇧🇹","BN":"🇧🇳","KH":"🇰🇭",
    "CN":"🇨🇳","HK":"🇭🇰","IN":"🇮🇳","ID":"🇮🇩","IR":"🇮🇷","IQ":"🇮🇶",
    "IL":"🇮🇱","JP":"🇯🇵","JO":"🇯🇴","KZ":"🇰🇿","KW":"🇰🇼","KG":"🇰🇬",
    "LA":"🇱🇦","LB":"🇱🇧","MY":"🇲🇾","MV":"🇲🇻","MN":"🇲🇳","MM":"🇲🇲",
    "NP":"🇳🇵","KP":"🇰🇵","KR":"🇰🇷","OM":"🇴🇲","PK":"🇵🇰","PH":"🇵🇭",
    "QA":"🇶🇦","SA":"🇸🇦","SG":"🇸🇬","LK":"🇱🇰","SY":"🇸🇾","TW":"🇹🇼",
    "TJ":"🇹🇯","TH":"🇹🇭","TM":"🇹🇲","AE":"🇦🇪","UZ":"🇺🇿","VN":"🇻🇳","YE":"🇾🇪",

    # North America
    "CA":"🇨🇦","CR":"🇨🇷","CU":"🇨🇺","DO":"🇩🇴","SV":"🇸🇻","GT":"🇬🇹",
    "HT":"🇭🇹","HN":"🇭🇳","JM":"🇯🇲","MX":"🇲🇽","NI":"🇳🇮","PA":"🇵🇦",
    "US":"🇺🇸",

    # South America
    "AR":"🇦🇷","BO":"🇧🇴","BR":"🇧🇷","CL":"🇨🇱","CO":"🇨🇴","EC":"🇪🇨",
    "GY":"🇬🇾","PY":"🇵🇾","PE":"🇵🇪","SR":"🇸🇷","UY":"🇺🇾","VE":"🇻🇪",

    # Africa
    "DZ":"🇩🇿","AO":"🇦🇴","CM":"🇨🇲","EG":"🇪🇬","ET":"🇪🇹","GH":"🇬🇭",
    "KE":"🇰🇪","LY":"🇱🇾","MA":"🇲🇦","NG":"🇳🇬","ZA":"🇿🇦","TN":"🇹🇳",
    "UG":"🇺🇬","ZW":"🇿🇼",

    # Oceania
    "AU":"🇦🇺","NZ":"🇳🇿","FJ":"🇫🇯"
}

def get_flag(cc):
    return FLAGS.get(cc, "🏳️ XX")

# =========================
# GEO CACHE
# =========================
geo_cache = {}
if os.path.exists(CACHE):
    with open(CACHE, "r") as f:
        for line in f:
            if "|" in line:
                s, c = line.strip().split("|")
                geo_cache[s] = c

def get_country(server):
    if server in geo_cache:
        return geo_cache[server]

    try:
        r = requests.get(f"http://ip-api.com/json/{server}", timeout=3).json()
        cc = r.get("countryCode", "XX")
    except:
        cc = "XX"

    geo_cache[server] = cc

    with open(CACHE, "a") as f:
        f.write(f"{server}|{cc}\n")

    return cc

# =========================
# LATENCY
# =========================
def latency(host, port):
    try:
        start = time.time()
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

# =========================
# PARSE
# =========================
def parse_vless(url):
    try:
        url = url.replace("vless://", "")
        user, rest = url.split("@")
        host_port, params = rest.split("?", 1)

        host, port = host_port.split(":")
        q = parse_qs(params)

        return {
            "uuid": user,
            "server": host,
            "port": int(port),
            "pbk": q.get("pbk", [""])[0],
            "sid": q.get("sid", [""])[0],
            "sni": q.get("sni", [""])[0],
        }
    except:
        return None

# =========================
# LOAD
# =========================
print("[INFO] downloading...")
data = requests.get(URL, timeout=30).text
links = list(set(re.findall(r'vless://[^"]+', data)))

proxies = []

# =========================
# BUILD
# =========================
for link in links:
    item = parse_vless(link)
    if not item:
        continue

    if not item["server"] or not item["port"]:
        continue

    ms = latency(item["server"], item["port"])
    if ms > 1200:
        continue

    cc = get_country(item["server"])
    flag = get_flag(cc)

    name = f"{flag} {cc} | {item['server']}:{item['port']} ({ms}ms)"

    proxies.append({
        "name": name,
        "type": "vless",
        "server": item["server"],
        "port": item["port"],
        "uuid": item["uuid"],
        "network": "tcp",
        "tls": True,
        "udp": True,
        "servername": item["sni"],
        "flow": "xtls-rprx-vision",
        "client-fingerprint": "chrome",
        "reality-opts": {
            "public-key": item["pbk"],
            "short-id": item["sid"]
        }
    })

# =========================
# SORT BEST FIRST
# =========================
proxies.sort(key=lambda x: int(re.search(r'\((\d+)ms\)', x["name"]).group(1)))

# =========================
# WRITE YAML
# =========================
with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump({"proxies": proxies}, f, allow_unicode=True, sort_keys=False)

print(f"[OK] generated {len(proxies)} proxies")
