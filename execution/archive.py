#!/usr/bin/env python3
"""Write every collected item to a grep-able daily archive. Nothing is lost."""
import json, sys, glob
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(".tmp/raw_*.json"))[-1]
d = json.load(open(path))
day = path.split("raw_")[1].replace(".json", "")

by = defaultdict(list)
for i in d["items"]:
    by[i["section"]].append(i)

ORDER = ["funding", "ideas", "shipped", "arena", "macro", "deals"]
out = [f"# Archive — {day}", "",
       f"{d['count']} items from 13 sources. Everything screened, including what",
       "did not make the brief.", ""]

for sec in ORDER + [k for k in by if k not in ORDER]:
    if sec not in by:
        continue
    out.append(f"## {sec} ({len(by[sec])})\n")
    for i in sorted(by[sec], key=lambda x: x["source"]):
        m = i["meta"]
        bits = [f"`{i['source']}`"]
        if m.get("points"):    bits.append(f"{m['points']}pts")
        if m.get("prize_usd"): bits.append(f"${m['prize_usd']:,}")
        if m.get("days_left") is not None: bits.append(f"{m['days_left']}d left")
        out.append(f"- [{i['title']}]({i['url']}) — {' · '.join(bits)}")
    out.append("")

if d.get("errors"):
    out += ["## source errors (non-fatal)", ""] + [f"- {e}" for e in d["errors"]]

open(f"archive/{day}.md", "w").write("\n".join(out))
print(f"archive/{day}.md  ({d['count']} items)")
