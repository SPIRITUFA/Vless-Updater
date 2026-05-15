#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import json
import socket
import yaml
import requests
from urllib.parse import urlparse, parse_qs
from subprocess import run, PIPE

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
OUT = os.path.join(OUT_DIR, "proxies.yaml")
LAT_FILE = os.path.join("/tmp", "latency.txt")
CACHE_FILE = os.path.join("/tmp", "geo_cache.txt")

os.makedirs(OUT_DIR, exist_ok=True)

# =========================
# FLAGS
# =========================
get_flag() {
  case "$1" in
         # Europe
    AL) echo "🇦🇱" ;; AD) echo "🇦🇩" ;; AM) echo "🇦🇲" ;;
    AT) echo "🇦🇹" ;; AZ) echo "🇦🇿" ;; BY) echo "🇧🇾" ;;
    BE) echo "🇧🇪" ;; BA) echo "🇧🇦" ;; BG) echo "🇧🇬" ;;
    HR) echo "🇭🇷" ;; CY) echo "🇨🇾" ;; CZ) echo "🇨🇿" ;;
    DK) echo "🇩🇰" ;; EE) echo "🇪🇪" ;; FI) echo "🇫🇮" ;;
    FR) echo "🇫🇷" ;; GE) echo "🇬🇪" ;; DE) echo "🇩🇪" ;;
    GR) echo "🇬🇷" ;; HU) echo "🇭🇺" ;; IS) echo "🇮🇸" ;;
    IE) echo "🇮🇪" ;; IT) echo "🇮🇹" ;; LV) echo "🇱🇻" ;;
    LI) echo "🇱🇮" ;; LT) echo "🇱🇹" ;; LU) echo "🇱🇺" ;;
    MT) echo "🇲🇹" ;; MD) echo "🇲🇩" ;; MC) echo "🇲🇨" ;;
    ME) echo "🇲🇪" ;; NL) echo "🇳🇱" ;; MK) echo "🇲🇰" ;;
    NO) echo "🇳🇴" ;; PL) echo "🇵🇱" ;; PT) echo "🇵🇹" ;;
    RO) echo "🇷🇴" ;; RU) echo "🇷🇺" ;; SM) echo "🇸🇲" ;;
    RS) echo "🇷🇸" ;; SK) echo "🇸🇰" ;; SI) echo "🇸🇮" ;;
    ES) echo "🇪🇸" ;; SE) echo "🇸🇪" ;; CH) echo "🇨🇭" ;;
    TR) echo "🇹🇷" ;; UA) echo "🇺🇦" ;; GB) echo "🇬🇧" ;;
    VA) echo "🇻🇦" ;;

    # Asia
    AF) echo "🇦🇫" ;; BH) echo "🇧🇭" ;; BD) echo "🇧🇩" ;;
    BT) echo "🇧🇹" ;; BN) echo "🇧🇳" ;; KH) echo "🇰🇭" ;;
    CN) echo "🇨🇳" ;; HK) echo "🇭🇰" ;; IN) echo "🇮🇳" ;;
    ID) echo "🇮🇩" ;; IR) echo "🇮🇷" ;; IQ) echo "🇮🇶" ;;
    IL) echo "🇮🇱" ;; JP) echo "🇯🇵" ;; JO) echo "🇯🇴" ;;
    KZ) echo "🇰🇿" ;; KW) echo "🇰🇼" ;; KG) echo "🇰🇬" ;;
    LA) echo "🇱🇦" ;; LB) echo "🇱🇧" ;; MY) echo "🇲🇾" ;;
    MV) echo "🇲🇻" ;; MN) echo "🇲🇳" ;; MM) echo "🇲🇲" ;;
    NP) echo "🇳🇵" ;; KP) echo "🇰🇵" ;; KR) echo "🇰🇷" ;;
    OM) echo "🇴🇲" ;; PK) echo "🇵🇰" ;; PH) echo "🇵🇭" ;;
    QA) echo "🇶🇦" ;; SA) echo "🇸🇦" ;; SG) echo "🇸🇬" ;;
    LK) echo "🇱🇰" ;; SY) echo "🇸🇾" ;; TW) echo "🇹🇼" ;;
    TJ) echo "🇹🇯" ;; TH) echo "🇹🇭" ;; TM) echo "🇹🇲" ;;
    AE) echo "🇦🇪" ;; UZ) echo "🇺🇿" ;; VN) echo "🇻🇳" ;;
    YE) echo "🇾🇪" ;;

    # North America
    CA) echo "🇨🇦" ;; CR) echo "🇨🇷" ;; CU) echo "🇨🇺" ;;
    DO) echo "🇩🇴" ;; SV) echo "🇸🇻" ;; GT) echo "🇬🇹" ;;
    HT) echo "🇭🇹" ;; HN) echo "🇭🇳" ;; JM) echo "🇯🇲" ;;
    MX) echo "🇲🇽" ;; NI) echo "🇳🇮" ;; PA) echo "🇵🇦" ;;
    US) echo "🇺🇸" ;;

    # South America
    AR) echo "🇦🇷" ;; BO) echo "🇧🇴" ;; BR) echo "🇧🇷" ;;
    CL) echo "🇨🇱" ;; CO) echo "🇨🇴" ;; EC) echo "🇪🇨" ;;
    GY) echo "🇬🇾" ;; PY) echo "🇵🇾" ;; PE) echo "🇵🇪" ;;
    SR) echo "🇸🇷" ;; UY) echo "🇺🇾" ;; VE) echo "🇻🇪" ;;

    # Africa
    DZ) echo "🇩🇿" ;; AO) echo "🇦🇴" ;; CM) echo "🇨🇲" ;;
    EG) echo "🇪🇬" ;; ET) echo "🇪🇹" ;; GH) echo "🇬🇭" ;;
    KE) echo "🇰🇪" ;; LY) echo "🇱🇾" ;; MA) echo "🇲🇦" ;;
    NG) echo "🇳🇬" ;; ZA) echo "🇿🇦" ;; TN) echo "🇹🇳" ;;
    UG) echo "🇺🇬" ;; ZW) echo "🇿🇼" ;;

    # Oceania
    AU) echo "🇦🇺" ;; NZ) echo "🇳🇿" ;; FJ) echo "🇫🇯" ;;
  esac
}

# =========================
# GEO CACHE
# =========================
def get_country(server):
    if not os.path.exists(CACHE_FILE):
        open(CACHE_FILE, "w").close()
    with open(CACHE_FILE, "r") as f:
        for line in f:
            if line.startswith(f"{server}|"):
                return line.strip().split("|")[1]
    try:
        geo = requests.get(f"http://ip-api.com/json/{server}", timeout=2).json()
        cc = geo.get("countryCode", "XX")
    except:
        cc = "XX"
    with open(CACHE_FILE, "a") as f:
        f.write(f"{server}|{cc}\n")
    return cc

# =========================
# LATENCY
# =========================
def get_latency(host, port, sni):
    try:
        start = time.time()
        # OpenSSL check
        cmd = ["timeout", "2", "openssl", "s_client", "-connect", f"{host}:{port}", "-servername", sni]
        run(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        return int((time.time() - start)*1000)
    except:
        return 2000  # fallback high latency

# =========================
# DOWNLOAD LINKS
# =========================
print("[INFO] downloading JSON...")
resp = requests.get(URL, timeout=10)
data = resp.text
links = sorted(set(re.findall(r'vless://[^\s"]+', data)))

print("[INFO] parsing nodes...")

proxies = []
latencies = []

for line in links:
    try:
        parsed = urlparse(line)
        if "@" not in parsed.netloc:
            continue
        uuid, hostport = parsed.netloc.split("@")
        host, port = hostport.split(":")
        port = int(port)
        qs = parse_qs(parsed.query)
        pbk = qs.get("pbk", [""])[0]
        sid = qs.get("sid", [""])[0].split("#")[0]
        sni = qs.get("sni", [""])[0].split("#")[0]

        if not all([uuid, host, port, pbk, sid, sni]):
            continue

        ms = get_latency(host, port, sni)
        if ms > 1200:
            continue

        cc = get_country(host)
        flag = get_flag(cc)

        latencies.append((ms, cc, host, port, uuid, pbk, sid, sni, flag))
    except Exception as e:
        continue

# =========================
# SORT BY LATENCY + UNIQUE
# =========================
seen = set()
latencies.sort()
latencies_unique = []
for item in latencies:
    if item[2] not in seen:
        seen.add(item[2])
        latencies_unique.append(item)

# =========================
# WRITE YAML
# =========================
with open(OUT, "w", encoding="utf-8") as f:
    proxies_yaml = []
    for ms, cc, server, port, uuid, pbk, sid, sni, flag in latencies_unique:
        proxies_yaml.append({
            "name": f"{flag} {cc} | {server}:{port} ({ms} ms)",
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
    yaml.dump({"proxies": proxies_yaml}, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

print(f"[OK] generated {len(proxies_yaml)} proxies")
