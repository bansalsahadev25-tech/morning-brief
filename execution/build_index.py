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



# ----------------------------------------------------------------------
# Issue navigation. Injected into EVERY issue file on every build, so old
# issues list new ones too. Bounded by markers and replaced idempotently,
# so re-running never stacks copies.
# ----------------------------------------------------------------------
NAV_START = "<!--ISSUE-NAV-START-->"
NAV_END = "<!--ISSUE-NAV-END-->"


def nav_html(rows, current_day):
    opts = "".join(
        '<option value="{href}"{sel}>Issue {num} &middot; {pretty}</option>'.format(
            href=os.path.basename(r["href"]),
            sel=" selected" if r["day"] == current_day else "",
            num=r["num"], pretty=r["pretty"])
        for r in rows)
    return f"""{NAV_START}
<style>
  #issuenav{{position:sticky;top:0;z-index:99;display:flex;align-items:center;
    gap:12px;flex-wrap:wrap;padding:9px 20px;margin:0 -20px 0;
    background:var(--surface,#FBFCFD);border-bottom:1px solid var(--rule,#D2D9DF);
    font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.7rem}}
  #issuenav a{{color:var(--accent,#1B3A57);text-decoration:none;border-bottom:0;
    text-transform:uppercase;letter-spacing:.09em;font-weight:600}}
  #issuenav a:hover{{text-decoration:underline}}
  #issuenav select{{font-family:inherit;font-size:.72rem;padding:4px 8px;
    background:var(--bg,#EFF2F4);color:var(--ink,#10161C);
    border:1px solid var(--rule2,#BEC7D0);border-radius:0;cursor:pointer;
    max-width:min(62vw,26rem)}}
  #issuenav .sp{{flex:1}}
  #issuenav .lbl{{color:var(--ink3,#78838F);text-transform:uppercase;
    letter-spacing:.1em}}
  /* keep the sticky bar from clipping whatever you jump to */
  section,.shead,.problem,.story{{scroll-margin-top:3.4rem}}
  @media print{{#issuenav{{display:none}}}}
</style>
<nav id="issuenav" aria-label="Issue navigation">
  <span class="lbl">Issue</span>
  <select id="issuepick" aria-label="Choose an issue">{opts}</select>
  <span class="sp"></span>
  <a href="index.html">All issues</a>
</nav>
<script>
  document.getElementById("issuepick").addEventListener("change", function (e) {{
    if (e.target.value) window.location.href = e.target.value;
  }});
</script>
{NAV_END}"""


CHARSET = ('<meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">')


def inject_nav(path, rows, day):
    html = open(path, encoding="utf-8").read()

    # Standalone issue files are served straight off GitHub Pages with no
    # wrapper, so without an explicit charset the browser falls back to
    # Latin-1 and every § — and every em dash — renders as mojibake.
    if "<meta charset" not in html.lower():
        html = CHARSET + "\n" + html

    block = nav_html(rows, day)
    if NAV_START in html and NAV_END in html:
        a = html.index(NAV_START)
        b = html.index(NAV_END) + len(NAV_END)
        html = html[:a] + block + html[b:]
    else:
        # Sit it just inside the page wrapper so it inherits the theme tokens.
        anchor = '<div class="wrap">'
        if anchor in html:
            html = html.replace(anchor, anchor + "\n" + block, 1)
        else:
            html = block + html
    open(path, "w", encoding="utf-8").write(html)




# ----------------------------------------------------------------------
# Feedback widgets. Injected into every rateable item on every build.
#
# Ids are derived from the issue date + the item's own text, so they are
# stable across rebuilds without the editorial pass having to know
# anything about them. Votes POST to the local server; on GitHub Pages
# (no server) the widgets hide themselves rather than silently failing.
# ----------------------------------------------------------------------
import hashlib

VOTE_START, VOTE_END = "<!--VOTE-CSS-START-->", "<!--VOTE-CSS-END-->"


def _vid(day, text):
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip().lower()[:300]
    return hashlib.sha1(f"{day}|{clean}".encode()).hexdigest()[:12]


def _widget(vid, title, section, day):
    t = html_escape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", title)).strip()[:200])
    return (f'<span class="vote" data-id="{vid}" data-title="{t}" '
            f'data-section="{section}" data-issue="{day}">'
            f'<button class="v-up" type="button" aria-label="More like this">&#9650;</button>'
            f'<button class="v-dn" type="button" aria-label="Less like this">&#9660;</button>'
            f'</span>')


def html_escape(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


VOTE_CSS = """<!--VOTE-CSS-START-->
<style>
  .vote{display:inline-flex;gap:3px;margin-left:9px;vertical-align:middle;
    opacity:.3;transition:opacity .15s}
  h3:hover .vote,li:hover .vote,.vote:hover,.vote.voted{opacity:1}
  .vote button{font-family:inherit;font-size:.62rem;line-height:1;cursor:pointer;
    padding:3px 6px;border:1px solid var(--rule2,#BEC7D0);background:transparent;
    color:var(--ink3,#78838F);border-radius:2px}
  .vote button:hover{border-color:var(--ink2,#4B5764);color:var(--ink,#10161C)}
  .vote button.on.v-up{background:#0D6A5E;border-color:#0D6A5E;color:#fff}
  .vote button.on.v-dn{background:#A33E12;border-color:#A33E12;color:#fff}
  body.no-server .vote{display:none}
  #fbnote{font-family:"IBM Plex Mono",monospace;font-size:.64rem;
    color:var(--ink3,#78838F);padding:7px 0;border-bottom:1px solid var(--rule,#D2D9DF)}
  body.no-server #fbnote{display:none}
</style>
<!--VOTE-CSS-END-->"""

VOTE_JS = r"""
<script>
(function () {
  var local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  if (!local) { document.body.classList.add("no-server"); return; }
  var day = (document.querySelector(".vote") || {}).dataset
          ? document.querySelector(".vote").dataset.issue : "";

  function paint(el, vote) {
    el.querySelector(".v-up").classList.toggle("on", vote === "up");
    el.querySelector(".v-dn").classList.toggle("on", vote === "down");
    el.classList.toggle("voted", vote === "up" || vote === "down");
  }

  fetch("/fb/state?issue=" + encodeURIComponent(day))
    .then(function (r) { return r.json(); })
    .then(function (state) {
      document.querySelectorAll(".vote").forEach(function (el) {
        if (state[el.dataset.id]) paint(el, state[el.dataset.id]);
      });
    })
    .catch(function () { document.body.classList.add("no-server"); });

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".v-up, .v-dn");
    if (!btn) return;
    var el = btn.closest(".vote");
    var want = btn.classList.contains("v-up") ? "up" : "down";
    var already = btn.classList.contains("on");
    var vote = already ? "clear" : want;
    paint(el, already ? null : want);
    fetch("/fb", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: el.dataset.id, vote: vote, title: el.dataset.title,
        section: el.dataset.section, issue: el.dataset.issue
      })
    }).catch(function () {});
  });
})();
</script>"""


def inject_votes(path, day):
    doc = open(path, encoding="utf-8").read()
    if "VOTE-CSS-START" in doc:                      # strip old pass first
        a = doc.index(VOTE_START)
        b = doc.index(VOTE_END) + len(VOTE_END)
        doc = doc[:a] + doc[b:]
    doc = re.sub(r'<span class="vote".*?</span>', "", doc, flags=re.S)
    doc = re.sub(r"<script>\s*\(function \(\) \{\s*var local.*?</script>", "",
                 doc, flags=re.S)

    def sect_of(pos):
        head = doc.rfind('<span class="snum">', 0, pos)
        if head == -1:
            return "unknown"
        m = re.match(r'<span class="snum">([^<]+)</span>', doc[head:head + 80])
        return (m.group(1).strip() if m else "unknown")

    out, last, n = [], 0, 0
    for m in re.finditer(r"</h3>", doc):
        start = doc.rfind("<h3", 0, m.start())
        if start == -1:
            continue
        title = doc[start:m.start()]
        vid = _vid(day, title)
        out.append(doc[last:m.end()])
        out.append(_widget(vid, title, sect_of(start), day))
        last = m.end()
        n += 1
    doc = "".join(out) + doc[last:]

    # feed list items too — one line each, but they are most of the page
    def li_sub(mm):
        nonlocal n
        inner = mm.group(1)
        if 'class="vote"' in inner or len(re.sub(r"<[^>]+>", "", inner).strip()) < 15:
            return mm.group(0)
        n += 1
        return ("<li>" + inner + _widget(_vid(day, inner), inner, "feed", day)
                + "</li>")

    doc = re.sub(r"<li>(.*?)</li>", li_sub, doc, flags=re.S)
    doc = doc.replace("</style>", "</style>\n" + VOTE_CSS, 1)
    doc = doc.rstrip() + VOTE_JS + "\n"
    open(path, "w", encoding="utf-8").write(doc)
    return n



total_votes = 0
for r in rows:
    inject_nav(r["href"], rows, r["day"])
    total_votes += inject_votes(r["href"], r["day"])
print(f"nav injected into {len(rows)} issue(s); {total_votes} vote widgets")


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

# latest.html — the one permanent link. Always the newest issue, so it can be
# bookmarked once and never change. (The artifact URL cannot do this: the
# headless `claude -p` run that builds the brief has no Artifact tool.)
if ISSUES:
    newest = ISSUES[0]
    import shutil
    shutil.copyfile(newest, "latest.html")
    print(f"latest.html -> {newest}")

print(f"index.html — {len(rows)} issue(s): " + ", ".join(r['day'] for r in rows))
