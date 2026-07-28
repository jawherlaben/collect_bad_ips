"# collect_bad_ips" 
=======
# collect_bad_ips

`collect_bad_ips` is a Python script that collects malicious IP addresses and CIDR ranges from public Threat Intelligence feeds, removes duplicates, validates the extracted entries, and exports them into reusable formats for security tools such as firewalls, SIEMs, IDS/IPS, and automation pipelines.

## Features

- Collects Indicators of Compromise (IOCs) from multiple public Threat Intelligence feeds.
- Supports IPv4, IPv6, IPv4 CIDR, and IPv6 CIDR extraction.
- Automatically validates and deduplicates collected entries.
- Exports a plain text blacklist (`bad_ips.txt`).
- Exports a CSV file with metadata (`bad_ips_with_meta.csv`).
- Simple logging for monitoring the collection process.
- Easily extensible to support additional Threat Intelligence feeds.

## Supported Threat Intelligence Feeds

- Spamhaus DROP
- DShield

## Project Structure

```text
collect_bad_ips/
├── collect_bad_ips.py
├── README.md
├── bad_ips.txt                 # Generated after execution
└── bad_ips_with_meta.csv       # Generated after execution
```

## Requirements

- Python 3.9+
- requests

## Installation

Clone the repository:

```bash
git clone https://github.com/jawherlaben/collect_bad_ips
cd collect_bad_ips
```

Install the required dependency:

```bash
pip install requests
```

## Usage

Run the script:

```bash
python collect_bad_ips.py
```

## Output Files

### `bad_ips.txt`

A plain text file containing unique malicious IP addresses and CIDR ranges.

Example:

```text
1.2.3.4
5.6.7.8
8.8.8.0/24
2001:db8::/32
```

### `bad_ips_with_meta.csv`

A CSV file containing each IOC along with its source and collection timestamp.

| entry | source | first_seen |
|-------|--------|------------|
| 1.2.3.4 | spamhaus_drop | 2026-07-28T09:30:12Z |
| 8.8.8.0/24 | dshield | 2026-07-28T09:30:12Z |

## Adding New Feeds

New Threat Intelligence sources can be added by extending the `FEEDS` dictionary.

Example:

```python
FEEDS = {
    "spamhaus_drop": "https://...",
    "dshield": "https://...",
    "new_feed": "https://..."
}
```

The parser automatically extracts:

- IPv4 addresses
- IPv6 addresses
- IPv4 CIDR ranges
- IPv6 CIDR ranges

No additional parsing logic is required for standard text-based feeds.

## Use Cases

- Threat Intelligence
- IOC Collection
- Security Automation
- Firewall Blocklists
- SIEM Enrichment
- IDS/IPS
- SOC Operations
- DFIR

## Future Improvements

- Support additional Threat Intelligence feeds (AbuseIPDB, AlienVault OTX, Emerging Threats, etc.)
- JSON export
- STIX/TAXII support
- Malicious domain collection
- Malicious URL collection
- MISP integration
- Scheduled execution (Cron/GitHub Actions)
- Parallel feed downloads
- Retry mechanism and enhanced error handling


## Author

Developed as part of a Threat Intelligence automation project for collecting and managing malicious IP indicators.
