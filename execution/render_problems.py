#!/usr/bin/env python3
"""Render §0 THE PROBLEM BOARD from config/problems.yaml.

Usage: render_problems.py <issue.html> <problem-id> [<problem-id> ...]
Injects the section directly after the masthead, replacing any existing one.
"""
import sys, html, yaml, re

START, END = "<!--PROBLEM-BOARD-START-->", "<!--PROBLEM-BOARD-END-->"
GRADE = {
    "green": ("START THIS MONTH", "solo · no capital · no credentials", "#0D6A5E"),
    "amber": ("6–12 MONTHS OUT",  "needs a team, hardware or access",    "#A36A12"),
    "red":   ("NOT YOURS YET",    "needs capital, clearance or a lab",   "#A33E12"),
}


def esc(t):
    return html.escape(str(t).strip())


def block(p):
    label, caveat, colour = GRADE[p["grade"]]
    steps = "".join(f"<li>{esc(s)}</li>" for s in p.get("research_path", []))
    return f"""
  <article class="problem">
    <div class="pgrade" style="--g:{colour}">
      <span class="badge">{label}</span><span class="caveat">{esc(caveat)}</span>
    </div>
    <h3>{esc(p['title'])}</h3>
    <dl class="brief">
      <dt>The problem</dt><dd>{esc(p['problem'])}</dd>
      <dt>Who says it's hard</dt>
      <dd>{esc(p['who_says'])} — <a href="{esc(p['source'])}">source</a></dd>
      <dt>Why it's still open</dt><dd>{esc(p['why_open'])}</dd>
      <dt>Who's already trying</dt><dd>{esc(p['who_is_trying'])}</dd>
      <dt>Your angle</dt><dd class="foryou">{esc(p['your_angle'])}</dd>
      <dt>Research path</dt><dd><ol class="rpath">{steps}</ol></dd>
    </dl>
  </article>"""


def render(ids, cfg="config/problems.yaml"):
    by = {p["id"]: p for p in yaml.safe_load(open(cfg))["problems"]}
    missing = [i for i in ids if i not in by]
    if missing:
        sys.exit(f"unknown problem id(s): {', '.join(missing)}")
    return f"""{START}
<style>
  .problem{{padding-bottom:30px;margin-bottom:30px;border-bottom:1px solid var(--rule)}}
  .problem:last-child{{border-bottom:0;margin-bottom:0;padding-bottom:6px}}
  .pgrade{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:9px}}
  .pgrade .badge{{font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:600;
    letter-spacing:.11em;color:#fff;background:var(--g);padding:3px 8px}}
  .pgrade .caveat{{font-family:"IBM Plex Mono",monospace;font-size:.66rem;color:var(--ink3)}}
  .problem h3{{font-family:Newsreader,Georgia,serif;font-weight:600;
    font-size:clamp(1.3rem,4vw,1.7rem);line-height:1.18;margin:0 0 16px;
    letter-spacing:-.01em;text-wrap:balance}}
  ol.rpath{{margin:0;padding-left:1.1rem}}
  ol.rpath li{{margin-bottom:7px}}
  ol.rpath li:last-child{{margin-bottom:0}}
  .pintro{{font-family:Newsreader,Georgia,serif;font-size:1.06rem;line-height:1.5;
    color:var(--ink2);margin:0 0 26px;text-wrap:pretty}}
</style>
<section>
  <div class="shead"><span class="snum">§0</span><h2>The Problem Board</h2>
    <span class="scount">2 of {len(by)}</span></div>
  <p class="pintro">
    Every accelerator says it funds people “solving hard problems”, and not one
    of them tells you which. This does. Sourced, graded honestly, with somewhere
    to start reading.
  </p>
{"".join(block(by[i]) for i in ids)}
</section>
{END}"""


if __name__ == "__main__":
    path, ids = sys.argv[1], sys.argv[2:]
    doc = open(path, encoding="utf-8").read()
    sec = render(ids)
    if START in doc:
        doc = doc[:doc.index(START)] + sec + doc[doc.index(END) + len(END):]
    else:
        m = re.search(r"</header>", doc)
        if not m:
            sys.exit("no </header> found — cannot place the board")
        doc = doc[:m.end()] + "\n" + sec + doc[m.end():]
    open(path, "w", encoding="utf-8").write(doc)
    print(f"§0 Problem Board -> {path}: {', '.join(ids)}")
