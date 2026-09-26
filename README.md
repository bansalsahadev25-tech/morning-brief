# The Morning Brief

A daily intelligence briefing assembled from 13 live sources, built for one
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

Keyless: Hacker News (Algolia), Show HN, Ask HN, TechCrunch, arXiv
(cs.AI/LG/CL), GitHub Trending, Devpost, YC Requests for Startups,
Reddit (RSS), Stratechery, McKinsey, Class Central, a16z / Sequoia /
First Round.

No API keys. No paid services.

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
