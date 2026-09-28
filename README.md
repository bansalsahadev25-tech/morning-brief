# The Morning Brief

A daily intelligence briefing assembled from ~60 live feeds, built for one
reader: an undergraduate trying to build a company and short on evidence.

Runs every morning at 10:00 IST as a scheduled Claude Code cloud agent.
Republishes to the same URL each day, so there is one permanent link.

## Why it exists

Newsletters are a bad interface for staying informed. Thirty of them carry
maybe eight real stories, each repeated six times, and none of them go
deeper than the headline. This collapses the duplicates, then goes out and
actually researches the few stories that matter — company, technology,
founders, where the idea came from, the bear case.

It also tracks the things newsletters never cover: competitions with
deadlines, fellowships that don't check your major, and one curated thing
worth reading that isn't from this week.

## Sections

| § | Section | Contents |
|---|---|---|
| 1 | The Big Three | 3 stories, researched properly |
| 2 | Money Moved | rounds, with what they signify |
| 3 | Problems Worth Solving | YC RFS, arXiv→product gaps, pain threads |
| 4 | Shipped | launches, releases, repos going vertical |
| 5 | The Arena | competitions and deadlines, days-left in red |
| 5b | Open Doors | fellowships, internship cycles |
| 6 | Skill | one skill, one free resource |
| 7 | The Canon | one lecture or book, rotating, with its why |
| 8 | Deals | free windows, course discounts |
| 9 | Also | everything else, one line each |

Empty sections say so. Padding a section is worse than leaving it short.

## Architecture

```
collect.py   13 sources in parallel, ~25s, every collector fault-tolerant
   ↓         a dead feed logs a warning; the brief still ships
archive.py   every item to archive/YYYY-MM-DD.md, grep-able forever
   ↓
editorial    triage → research top 3 → render → publish   (Claude Code)
```

Deterministic work in Python, judgment in the model. Nothing in between.

## Sources

24 collectors, ~60 feeds, **zero API keys**:

- **Wire** — Hacker News (front page, Best, Show, Ask), Lobsters, TechCrunch,
  Techmeme, Ars Technica, The Verge, 404 Media
- **Money** — Crunchbase News, Sifted, Inc42, YourStory, a16z, Sequoia,
  First Round, YC
- **Research** — arXiv (cs.AI/LG/CL), Simon Willison, Interconnects, Import AI
- **Shipped** — GitHub Trending, Hugging Face trending models + datasets,
  Anthropic / Google / Hugging Face blogs
- **Learn** — Quanta, Nautilus, Aeon, MIT News, MIT Tech Review,
  IEEE Spectrum, Marginal Revolution, Construction Physics
- **Watch** — 14 YouTube channels via RSS: Stanford eCorner, Stanford Online,
  YC, Acquired, Asianometry, Veritasium, 3Blue1Brown, Lex Fridman,
  Everyday Astronaut, Real Engineering, a16z, Two Minute Papers,
  Computerphile, Practical Engineering
- **Build** — Hackaday, Adafruit, r/rcplanes, r/Multicopter,
  r/diyelectronics, r/AskEngineers
- **Doors** — Devpost, YC Requests for Startups, Class Central

YouTube runs on channel RSS, so no YouTube Data API key is needed.
Time windows differ by section: news 36h, learning 10 days,
lectures 30 days. An essay does not expire; a funding headline does.

## Run it

```bash
pip install feedparser requests pyyaml
./execution/run.sh
```

## Layout

```
config/       sources.yaml · profile.md · canon.yaml
directives/   daily_brief.md — the editorial SOP
execution/    collect.py · archive.py · run.sh
archive/      every item ever screened
```

## Editorial standard

One test for every item: **does this change what the reader does this
week?** Anything that is merely interesting gets cut. Interesting is the
enemy — it's what makes you feel informed while nothing happens.

## Known limitation: cloud environments

The collectors need outbound network access to 13 source hosts. Sandboxed
environments with a network egress allowlist (including Claude Code cloud
routines by default) block all of them, and collection returns zero items.

`collect.py` exits non-zero below a floor of 30 items so that nothing
downstream improvises a brief from an empty run and publishes it over a good
one. If you run this in a sandbox, allowlist these hosts:

```
hn.algolia.com        techcrunch.com       export.arxiv.org
devpost.com           reddit.com           ycombinator.com
github.com            stratechery.com      classcentral.com
a16z.com              sequoiacap.com       review.firstround.com
mckinsey.com          huggingface.co       blog.google
```
