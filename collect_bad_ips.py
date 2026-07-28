from __future__ import annotations
import re
import requests
import ipaddress
from datetime import datetime, timezone
import os
import sys
import logging

FEEDS = {
    "spamhaus_drop": "https://www.spamhaus.org/drop/drop.txt",
    "dshield": "https://www.dshield.org/ipsascii.html",
}

HEADERS_BY_FEED = {
}

REQUEST_TIMEOUT = 20


CIDR_RE = re.compile(r'\b(?:\d{1,3}(?:\.\d{1,3}){3}|[0-9A-Fa-f:]+:[0-9A-Fa-f:]+)\/\d{1,3}\b')
IP_RE = re.compile(r'\b(?:\d{1,3}(?:\.\d{1,3}){3}|[0-9A-Fa-f:]+:[0-9A-Fa-f:]+)\b')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_headers_for_feed(name, feed_cfg):
    headers = {}
    headers.update(HEADERS_BY_FEED.get(name, {}))
    if isinstance(feed_cfg, dict) and "headers_env" in feed_cfg:
        envvar = feed_cfg["headers_env"]
        key = os.getenv(envvar)
        if key:
            if "abuseipdb" in name.lower():
                headers["Key"] = key
                headers["Accept"] = "application/json"
            else:
                headers["Authorization"] = f"Bearer {key}"
    return headers or None

def fetch_text(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logging.warning("Erreur fetch %s : %s", url, e)
        return ""

def extract_ips_and_cidrs(text):
    results = set()
    if not text:
        return results
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith(("#", ";", "//"))]
    cleaned = "\n".join(lines)
    for m in CIDR_RE.finditer(cleaned):
        candidate = m.group(0)
        try:
            net = ipaddress.ip_network(candidate, strict=False)
            results.add(str(net))
        except Exception:
            continue
    for m in IP_RE.finditer(cleaned):
        candidate = m.group(0)
        try:
            ip = ipaddress.ip_address(candidate)
            results.add(str(ip))
        except Exception:
            continue
    return results

def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_entries = {} 

    for name, cfg in FEEDS.items():
        if isinstance(cfg, str):
            url = cfg
            feed_type = "text"
            feed_cfg = {}
        else:
            url = cfg.get("url")
            feed_type = cfg.get("type", "text")
            feed_cfg = cfg

        logging.info("Fetching %s -> %s", name, url)
        headers = get_headers_for_feed(name, feed_cfg)
        text = fetch_text(url, headers=headers)
        entries = extract_ips_and_cidrs(text)
        logging.info(" -> %d entrées trouvées dans %s", len(entries), name)
        for entry in entries:
            if entry not in all_entries:
                all_entries[entry] = {"source": name, "first_seen": timestamp}

    sorted_entries = sorted(all_entries.items(), key=lambda kv: kv[0])

    out_txt = "bad_ips.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        for entry, meta in sorted_entries:
            f.write(entry + "\n")
    logging.info("Écrit %d entrées dans %s", len(sorted_entries), out_txt)

    out_csv = "bad_ips_with_meta.csv"
    with open(out_csv, "w", encoding="utf-8") as f:
        f.write("entry,source,first_seen\n")
        for entry, meta in sorted_entries:
            f.write(f'"{entry}","{meta["source"]}","{meta["first_seen"]}"\n')
    logging.info("Écrit %d entrées dans %s", len(sorted_entries), out_csv)

if __name__ == "__main__":
    main()
