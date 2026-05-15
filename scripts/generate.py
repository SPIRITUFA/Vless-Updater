#!/usr/bin/env python3
import os
import json
import requests
import subprocess
import time
import yaml
from pathlib import Path

# =========================
# Параметры
# =========================
URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"
OUT = "/opt/etc/mihomo/proxy-providers/proxies.yaml"
TMP = "/tmp/proxies.yaml"
CACHE_FILE = "/tmp/geo_cache.txt"

# Создаем директории
Path(os.path.dirname(OUT)).mkdir(parents=True, exist_ok=True)
Path(CACHE_FILE).touch(exist_ok=True)

# =========================
# Флаги по коду страны
# =========================
FLAGS = {
    "RU":"🇷🇺","DE":"🇩🇪","FR":"🇫🇷","PL":"🇵🇱","US":"🇺🇸","GB":"🇬🇧","FI":"🇫🇮","JP":"🇯🇵",
    "XX":"🌐"  # fallback
}

def get_flag(cc):
    return FLAGS.get(cc.upper(), "🌐")

# =========================
# GEO CACHE
# =========================
geo_cache = {}
with open(CACHE_FILE, "r") as f:
    for line in f:
        if "|" in line:
            server, cc = line.strip().split("|")
            geo_cache[server] = cc

def get_country(server):
    if server in geo_cache:
        return geo_cache[server]
    try:
        resp = requests.get(f"http://ip-api.com/json/{server}", timeout=5)
        data = resp.json()
        cc = data.get("countryCode", "XX")
    except:
        cc = "XX"
    geo_cache[server] = cc
    # save to cache
    with open(CACHE_FILE, "a") as f:
        f.write(f"{server}|{cc}\n")
    return cc

# =========================
# TLS latency
# =========================
def get_latency(host, port, sni):
    start = time.time()
    try:
        subprocess.run([
            "openssl", "s_client", "-connect", f"{host}:{port}", "-servername", sni
        ], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
    except:
        return 9999
    end = time.time()
    return int((end - start) * 1000)

# =========================
# Скачиваем JSON
# =========================
print("[INFO] Downloading JSON...")
r = requests.get(URL, timeout=10)
r.raise_for_status()
json_data = r.json()

nodes = []

# =========================
# Парсим ноды
# =========================
for node_str in set(json_data):
    if not node_str.startswith("vless://") or "@" not in node_str:
        continue
    try:
        # Разбор строки
        parts = node_str.split("@")
        uuid = parts[0].replace("vless://","")
        server_port = parts[1].split("?")[0]
        server, port = server_port.split(":")
        port = int(port)
        query = parts[1].split("?")[1] if "?" in parts[1] else ""
        pbk = sid = sni = ""
        for q in query.split("&"):
            if q.startswith("pbk="): pbk = q[4:]
            if q.startswith("sid="): sid = q[4:]
            if q.startswith("sni="): sni = q[4:]
        if not sni: sni = server
        if not pbk or not sid: continue

        print(f"[TEST] {server}:{port}")
        latency = get_latency(server, port, sni)
        if latency > 1200:
            continue

        cc = get_country(server)
        flag = get_flag(cc)

        nodes.append({
            "name": f"{flag} {cc} | {server}:{port} ({latency} ms)",
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
            },
            "latency": latency
        })
    except Exception as e:
        continue

# =========================
# Сортируем по latency
# =========================
nodes.sort(key=lambda x: x["latency"])

# =========================
# Генерация YAML
# =========================
with open(TMP, "w") as f:
    yaml.dump({"proxies": nodes}, f, sort_keys=False, allow_unicode=True)

# =========================
# Применяем если есть изменения
# =========================
if not Path(OUT).exists() or open(TMP).read() != open(OUT).read():
    if Path(OUT).exists():
        Path(OUT + ".bak").write_text(open(OUT).read())
    Path(TMP).replace(OUT)
    print("[INFO] YAML UPDATED")
    # reload mihomo
    try:
        requests.post("http://127.0.0.1:9090/proxies", timeout=2)
        print("[INFO] Mihomo reloaded")
    except:
        pass
else:
    Path(TMP).unlink()
    print("[INFO] no changes")

print(f"[INFO] total nodes: {len(nodes)}")
