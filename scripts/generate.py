import requests
import yaml
import re

URL = "https://raw.githubusercontent.com/tiagorrg/vless-checker/main/docs/keys.json"

OUT = "output/proxies.yaml"

FLAGS = {
    "RU": "🇷🇺",
    "US": "🇺🇸",
    "DE": "🇩🇪",
    "NL": "🇳🇱",
    "FI": "🇫🇮",
    "FR": "🇫🇷",
    "GB": "🇬🇧",
}

resp = requests.get(URL, timeout=20)
data = resp.text

links = sorted(set(re.findall(r'vless://[^"]+', data)))

proxies = []

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

    cc = "RU"

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

with open(OUT, "w", encoding="utf-8") as f:
    yaml.dump(
        {"proxies": proxies},
        f,
        allow_unicode=True,
        sort_keys=False
    )

print(f"Generated {len(proxies)} proxies")
