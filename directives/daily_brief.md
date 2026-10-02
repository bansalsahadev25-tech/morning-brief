# Directive: The Morning Brief

**Runs:** 06:00 daily, local cron.
**Output:** graphic HTML report + markdown archive.
**Reader:** one person building toward founding a company in his early 20s.
Write for someone who will *act* on this, not browse it.

---

## §0 — THE PROBLEM BOARD leads every issue

This is now the point of the brief. Everything else is context for it.

The reader's actual bottleneck is not information. It is that every
accelerator, grant and VC says "we fund people solving hard problems"
and **nobody tells him which problems**. Emergent Ventures says it.
YC says it. He cannot act on it. So the brief says it, specifically,
with sources and a research path.

**Every issue opens with two problems from `config/problems.yaml`:**
one `green`, one `amber` or `red`. Rotate; never repeat inside 21 days;
a `green` may repeat until he has acted on it.

Render each with all of:

```
THE PROBLEM       plain, concrete, no hype
WHO SAYS IT'S HARD  named source + link — never an unsourced assertion
WHY IT'S STILL OPEN what specifically defeats people
WHO'S ALREADY TRYING so he doesn't reinvent, and knows the competition
YOUR ANGLE        why HE specifically could or could not attack it
RESEARCH PATH     3 concrete next steps, each a link or a named action
```

**The grade is the most valuable thing on the page.** Be honest:

- `green` — start this month, solo, no capital, no credentials
- `amber` — real within 6-12 months, needs a team, hardware or access
- `red` — needs capital, clearance, a lab or a decade

Never inflate a grade to be encouraging. Telling a 19-year-old he can
go solve fusion wastes years of his life. A `red` is filed so he
recognises it later, not hidden.

**New problems** arrive from DARPA solicitations, Institute for Progress,
Marginal Revolution (Tyler Cowen runs Emergent Ventures — reading him is
reading the grader), XPRIZE, grants.gov, and a diff of YC's RFS page.
When YC's RFS changes, that is a §0 headline on its own: a pre-validated
idea with a funder attached.

When a problem in the board gets solved, funded away, or he rejects it —
edit `config/problems.yaml`. It is plain text on purpose.

---

## §W — THE WILDCARD, and the feedback loop

Every item on the page carries a thumbs up / thumbs down. Clicks POST to a
local server (`execution/server.py`, always running) and land in
`feedback/votes.jsonl`. Before each run, `execution/learn.py` digests them
into `config/interests.md` — **in plain English, never as a score.** He
rejected an opaque weighting model once and was right to; a number nobody
can read drifts somewhere nobody asked for. He can edit that file by hand,
and when he does, his words beat the counts.

§W is the exploration arm and is **exempt from all of it**. Its sources sit
outside the tech wire entirely, and it must stay strange: if the wildcard
gets curated toward what already scores well, it stops doing the one job it
has, which is finding interests that are not in the file yet. Roughly one
item in five across the whole brief should sit outside his known tastes.

A feed that only confirms what he already likes stops teaching him anything.

---

## Editorial standard

The test for every item: **does this change what he does this week?**

And the sharper version, since §0 now leads: **does this reveal a problem
worth solving, or tell him something he needs in order to solve one?**
A funding round matters because it shows where money believes a problem
is. A launch matters because it closes or opens a gap. Report the news
as evidence about problems, not as news.

An item earns its place if it gives him one of:
- an idea he could build
- a door he could walk through (competition, grant, application, job)
- a mental model he didn't have
- a fact that changes how he reads the next six months

Cut anything that is only interesting. Interesting is the enemy.
"Company raised money" is not a story. "Company raised money *because*
this technology crossed a threshold, and here's the next thing that
threshold unlocks" is a story.

**Never pad a section to fill it.** A short honest section beats a
long padded one. If nothing happened in funding today, say
"Quiet day. Three small rounds, none instructive." and move on.

---

## Pipeline

### 1. Collect (deterministic, parallel)
Pull every source in `config/sources.yaml` for the last 24h.
Failures are non-fatal — log the source, continue. A dead feed must
never kill the brief.

### 2. Normalize + dedup
Everything becomes one item shape:
`{id, title, url, source, date, section_hint, raw_text}`
Dedup by URL, then by title similarity. One story reported by six
outlets = one item with `corroboration: 6`. High corroboration is a
ranking signal, not a quality signal — a story everyone covers is
usually a story with no edge left in it. Note it, don't over-weight it.

### 3. Triage into sections

The collector emits nine raw section tags. Three of them are new and do
not map one-to-one onto the published sections:

| tag | what it holds | where it goes |
|---|---|---|
| `learn` | Quanta, Nautilus, Aeon, MIT News, MIT Tech Review, IEEE Spectrum, Marginal Revolution, Construction Physics | §3 when it suggests something buildable; otherwise §9. **At least two `learn` items must reach the page every day** — this is the "cool stuff" tier and the reason he reads at all. |
| `watch` | lectures and talks: Stanford eCorner, Stanford Online, YC, Acquired, Asianometry, Veritasium, 3Blue1Brown, Lex Fridman, Everyday Astronaut, Real Engineering, a16z, Computerphile, Practical Engineering | §7. Alternate: some days a fresh talk from `watch`, other days a timeless item from `config/canon.yaml`. Never two fresh days in a row — the canon exists because new ≠ good. |
| `build` | Hackaday, Adafruit, r/rcplanes, r/Multicopter, r/diyelectronics, r/AskEngineers | §4, flagged when relevant to the tiltrotor. Hardware someone actually made beats hardware someone announced. |

`watch` and `learn` items are dated up to 30 and 10 days back on purpose.
A lecture does not expire; a funding headline does. Do not discard them
for being older than today.

Route the rest to their obvious section. Within each, order by
hard signals only:
- funding: round size, then stage novelty
- arena: **deadline proximity — soonest first, always**
- shipped: star velocity / HN points
- ideas: source authority (YC RFS outranks a Reddit thread)

### 4. Research pass — THE BIG THREE
Pick the three items with the highest "changes what he does" score.
For each, go out and actually research. Do not write from the headline.

Gather before writing:
- company site: `/about`, `/blog`, and **`/careers`** — job posts leak
  the real tech stack; press releases don't
- GitHub org: repos, languages, commit velocity, who they hired
- HN threads on the company: engineers saying what's actually hard
- **the founders**: prior companies, where they worked, what they
  studied, what they built before this. Podcasts and long-form
  interviews over press profiles.
- **origin of the idea**: what did they see that others didn't? Almost
  every good company starts with a founder having unusual access to a
  problem. Find that access. It is the most transferable thing in the
  entire brief.
- funding history, competitors, what the bear case is

Then write ~300-400 words per story in this shape:

```
WHAT THEY DO        plain English, no marketing language
THE TECH            what's actually under it, and what's hard about it
THE FOUNDERS        who, prior life, the unfair advantage they had
WHERE THE IDEA CAME FROM   the specific access or observation
WHY IT WORKS        the real mechanism, not the narrative
THE BEAR CASE       what kills this company
WHAT IT MEANS       for him specifically — adjacent openings this creates
```

### 5. Fill remaining sections
Sections 2-9 per `config/sections.md`. Brief, dense, linked.

### 6. Render
Graphic HTML. Dark. Typographic hierarchy doing the work, not
decoration. Deadlines in §5 render with **days remaining**, and go
red under 7 days.

### 7. Archive
`archive/YYYY-MM-DD.md` — full text, every item including the ones
that didn't make the report. Nothing is ever lost, it's just filed.
Grep-able years later.

---

## Tuning

No scoring model. No weights. One file: `config/preferences.md`.

When he says "more of this / less of that", edit that file in plain
English. The triage step reads it as instruction. That's the whole
system. It's legible, he can edit it himself, and it never drifts
somewhere he didn't ask it to go.

---

## Standing rules

- **Cite everything.** Every claim links to where it came from.
- **Separate fact from read.** Report the fact, then label the
  interpretation as interpretation. Never blur them.
- **Numbers or silence.** No "significant growth". Either the figure
  or nothing.
- **Kill the hype vocabulary.** No revolutionary, game-changing,
  disrupting. If the thing is impressive the facts will carry it.
- **Say when you don't know.** "Valuation not disclosed" beats a guess.
  A brief that hedges nothing is a brief that is lying somewhere.
