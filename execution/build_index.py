#!/usr/bin/env python3
"""Regenerate index.html — the browsable archive of every issue ever published."""
import re, glob, os
from datetime import datetime

ISSUES = sorted(glob.glob("issues/*.html"), reverse=True)

def meta(path):
    """Pull issue number, date and the thesis line out of a published issue."""
    html = open(path, encoding="utf-8").read()
    day = os.path.basename(path).replace(".html", "")
    num = re.search(r"<span>Issue (\d+)</span>", html)
    counts = re.search(r"<span>(\d+) items screened[^<]*?(\d+) filed</span>", html)
    thesis = re.search(r'<p class="thesis">(.*?)</p>', html, re.S)
    text = ""
    if thesis:
        text = re.sub(r"<[^>]+>", "", thesis.group(1))
        text = re.sub(r"\s+", " ", text).strip()
        text = (text.replace("&mdash;", "—").replace("&rsquo;", "’")
                    .replace("&ldquo;", "“").replace("&rdquo;", "”")
                    .replace("&amp;", "&"))
    return {
        "day": day,
        "num": num.group(1) if num else "—",
        "screened": counts.group(1) if counts else None,
        "filed": counts.group(2) if counts else None,
        "thesis": text,
        "href": path,
        "pretty": datetime.strptime(day, "%Y-%m-%d").strftime("%a %-d %b %Y"),
    }

rows = [meta(p) for p in ISSUES]

cards = "\n".join(f"""    <a class="issue" href="{r['href']}">
      <div class="top">
        <span class="no">Issue {r['num']}</span>
        <span class="date">{r['pretty']}</span>
        {f'<span class="ct">{r["screened"]} screened · {r["filed"]} filed</span>' if r['screened'] else ''}
      </div>
      <p class="th">{r['thesis']}</p>
    </a>""" for r in rows)

html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Morning Brief — Archive</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{{--bg:#EFF2F4;--surface:#FBFCFD;--ink:#10161C;--ink2:#4B5764;--ink3:#78838F;
--rule:#D2D9DF;--rule2:#BEC7D0;--accent:#1B3A57}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0B0F13;--surface:#131A21;--ink:#E3E9F0;
--ink2:#8C99A7;--ink3:#66727F;--rule:#222C36;--rule2:#2E3A45;--accent:#84B4DE}}}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",-apple-system,sans-serif;
font-size:15.5px;line-height:1.6;margin:0;padding-block:0;padding-left:20px;padding-right:20px}}
.wrap{{max-width:70ch;margin:0 auto}}
header{{padding-block:38px 18px;border-bottom:2px solid var(--ink)}}
h1{{font-family:Newsreader,Georgia,serif;font-weight:600;font-size:clamp(2rem,7vw,2.9rem);
line-height:1;margin:0 0 12px;letter-spacing:-.015em}}
.sub{{display:flex;flex-wrap:wrap;gap:6px 18px;font-family:"IBM Plex Mono",monospace;
font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--ink2)}}
.lede{{font-family:Newsreader,Georgia,serif;font-size:1.12rem;line-height:1.5;color:var(--ink2);
margin:18px 0 0;padding-top:14px;border-top:1px solid var(--rule)}}
.list{{display:flex;flex-direction:column;gap:0;margin-block:8px 40px}}
a.issue{{display:block;text-decoration:none;color:inherit;padding:20px 0;
border-bottom:1px solid var(--rule)}}
a.issue:hover .th{{color:var(--ink)}}
a.issue:hover .no{{color:var(--accent)}}
.top{{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline;margin-bottom:7px}}
.no{{font-family:"IBM Plex Mono",monospace;font-size:.78rem;font-weight:600;
letter-spacing:.05em}}
.date{{font-family:"IBM Plex Mono",monospace;font-size:.72rem;color:var(--ink2)}}
.ct{{font-family:"IBM Plex Mono",monospace;font-size:.66rem;color:var(--ink3)}}
.th{{font-family:Newsreader,Georgia,serif;font-size:1.05rem;line-height:1.45;
color:var(--ink2);margin:0;text-wrap:pretty}}
footer{{border-top:2px solid var(--ink);padding-block:18px 46px;
font-family:"IBM Plex Mono",monospace;font-size:.7rem;color:var(--ink3);line-height:1.7}}
footer a{{color:var(--accent)}}
</style></head><body><div class="wrap">
<header>
  <h1>The Morning Brief</h1>
  <div class="sub"><span>Archive</span><span>{len(rows)} issue{'s' if len(rows)!=1 else ''}</span><span>daily · 10:00 IST</span></div>
  <p class="lede">Every issue, permanently. Newest first.</p>
</header>
<div class="list">
{cards}
</div>
<footer>
  Assembled daily from 13 live sources. Deterministic collection in Python,
  editorial judgment in Claude Code.<br>
  <a href="https://github.com/bansalsahadev25-tech/morning-brief">Source</a> ·
  <a href="https://github.com/bansalsahadev25-tech/morning-brief/tree/main/archive">Raw archive of every item ever screened</a>
</footer>
</div></body></html>
"""
open("index.html", "w", encoding="utf-8").write(html)
print(f"index.html — {len(rows)} issue(s): " + ", ".join(r['day'] for r in rows))
