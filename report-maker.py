import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

JSON_FILE = Path("network_devices.json")
OUTPUT_FILE = Path("report.txt")

LOW_UPTIME_DAYS = 30
HIGH_UTIL_THRESHOLD = 80.0

def load_data(path: Path):

    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)
    
def flatten_devices(data):
    devices = []
    for loc in data.get("locations", []):
        site = loc.get("site", "")
        city = loc.get("city", "")
        contact = loc.get("contact", "")
        for d in loc.get("devices", []):
            item = dict(d)
            item["site"] = site
            item["city"] = city
            item["contact"] = contact
            devices.append(item)
    return devices

def percent(used, total):
    return (used / total * 100.0) if total else 0.0

def fmt_table(rows, headers):
    cols = len(headers)
    rows =[[str(x) for x in r] for r in rows]
    widths = [len(str(h)) for h in headers]
    CAP = 36
    for r in rows:
        for i in range(cols):
            widths[i] = (min(max(widths[i]), len(r[i])), CAP)