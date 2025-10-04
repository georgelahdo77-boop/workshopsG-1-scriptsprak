
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ---- Files 
JSON_FILE = Path("network_devices.json")
OUTPUT_FILE = Path("report.txt")

# ---- Thresholds ----
LOW_UPTIME_DAYS = 30          # devices with uptime below this are flagged as "low uptime"
HIGH_UTIL_THRESHOLD = 80.0    # switch port utilization considered "high" (%)


def load_data(path: Path):
    """Load JSON, handling potential UTF-8 BOM."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path.resolve()}")
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
    """Safe percentage calculation."""
    return (used / total * 100.0) if total else 0.0

def fmt_table(rows, headers):
    """Simple monospace table for .txt reports."""
    rows = [[str(x) for x in r] for r in rows]
    widths = [len(h) for h in headers]
    CAP = 36  # max column width so tables remain readable
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = min(max(widths[i], len(c)), CAP)

    def trunc(s, w): return s if len(s) <= w else s[: w-1] + "…"
    line = "+".join("-" * (w + 2) for w in widths)
    out = []
    out.append(line)
    out.append("| " + " | ".join(trunc(h,widths[i]).ljust(widths[i]) for i, h in enumerate(headers)) + " |")
    out.append(line)
    for r in rows:
        out.append("| " + " | ".join(trunc(r[i], widths[i]).ljust(widths[i]) for i in range(len(headers))) + " |")
    out.append(line)
    return "\n".join(out)

def sec(t): return f"\n{t}\n" + "=" * len(t) + "\n"
def sub(t): return f"\n{t}\n" + "-" * len(t) + "\n"

def generate_report(json_path: Path, out_path: Path): 
    data =load_data(json_path)


    company = data.get("company", "okänt företag")
    last_update = data.get("last_update", "")
    try:
        last_fmt = datetime.fromisoformat(last_update).strftime("%Y-%m-%d %H:%M")
    except Exception:
        last_fmt = last_update or "okänt"


    devices = flatten_devices(data)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")


    ow = [d for d in devices if d.get("ststus") in {"offline", "warning"}]


    counts_type = Counter(d.get("type", "okänd") for d in devices)

    low_uptime =[d for d in devices if d.get("uptime_days", 0) < LOW_UPTIME_DAYS]

    switches = [d for d in devices if d.get("type") == "switch" and isinstance(d.get("ports"), dict)]
    used_total = sum(d["ports"].get("used", 0) for d in switches)
    total_ports = sum(d["ports"].get("total", 0) for d in switches)
    port_util_pct = percent(used_total, total_ports)


    unique_vlans = sorted({v for d in devices for v in d.get("vlans", [])})

    by_loc = defaultdict(list)
    for d in devices:
        by_loc[d.get("site", "okänd")].append(d)
    loc_rows = []
    for site, items in sorted(by_loc.items()):
        online = sum(1 for d in items if d.get("status") == "online")
        warning = sum(1 for d in items if d.get("status") == "warning")
        offline = sum(1 for d in items if d.get("status") == "offline")
        loc_rows.append([site, len(items), online, warning, offline])


        high_util = []
        for d in switches:
            u, t = d["ports"].get("used" 0), d["ports"].get("total", 0)
            p = percent(u, t)
            if p >= HIGH_UTIL_THRESHOLD:
                high_util.append((d, p))




        

