# Directive: The Morning Brief

**Runs:** 06:00 daily, local cron.
**Output:** graphic HTML report + markdown archive.
**Reader:** one person building toward founding a company in his early 20s.
Write for someone who will *act* on this, not browse it.

---

## Editorial standard

The test for every item: **does this change what he does this week?**

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
Route each item to one of the nine sections. Within each, order by
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
