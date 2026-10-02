Produce today's issue of The Morning Brief. Collection has already run —
`.tmp/raw_<today>.json` and `archive/<today>.md` exist. Work in order.

**STOP CONDITION — read this first.** If collection exited non-zero, or the
raw JSON holds fewer than 30 items, the environment is broken (almost always
blocked network egress), not the news. In that case: **publish nothing.** Do
not hand-assemble a brief from web search, do not overwrite the existing
artifact, do not write an issue file. Report what failed and stop. A missing
issue is recoverable; a thin issue published over a good one is not.

**0. Read what he actually likes.** `config/interests.md` is regenerated
from his thumbs up/down before every run. Treat it as **direction, not a
filter** — never drop a whole topic over a few downvotes, and keep roughly
one item in five outside everything it mentions. If it says there is not
enough signal yet, ignore it and keep the mix broad. He can edit that file
by hand; if he has, his words win over the counts.

**1. Read the rules.** `directives/daily_brief.md` (editorial SOP — follow it
exactly), `config/profile.md` (who this is for), `config/canon.yaml` (the
rotating canon). The single test for every item: *does this change what the
reader does this week?* Cut anything merely interesting.

**2. Read yesterday's issue.** Artifact tool, `action: "read"`, url
`https://claude.ai/artifact/VqyUysjjQhpUjSFhhmMUQJ`. Required before you may
publish to it, and it hands you the established design system — Newsreader +
IBM Plex Sans/Mono, the light/dark token set, the section layout. Reuse that
CSS as-is. Do not redesign: this is a daily publication and should look
identical issue to issue. Note which canon item and which skill ran, so
today's differ.

**2b. Build §0 — THE PROBLEM BOARD. This leads the issue.**
Read `config/problems.yaml`. Pick two problems: one `green`, one `amber`
or `red`. Check the last few files in `issues/` so you do not repeat one
inside 21 days (a `green` may repeat until he acts on it). Render each
with: THE PROBLEM / WHO SAYS IT'S HARD (named source + link) / WHY IT'S
STILL OPEN / WHO'S ALREADY TRYING / YOUR ANGLE / RESEARCH PATH (3
concrete steps). Show the grade prominently and honestly — never inflate
one to be encouraging.

Then check for NEW problems in today's raw JSON: items from DARPA,
Institute for Progress, Marginal Revolution, or any change in YC's
Requests for Startups. A changed YC RFS is a §0 headline on its own.
If you find a genuinely new hard problem worth keeping, append it to
`config/problems.yaml` with the same fields and a grade.

**3. Triage.** Read `.tmp/raw_*.json` (today's). Route into the nine
sections per the SOP. Order within each section by hard signals only —
funding by round size, arena by deadline proximity (soonest first, always),
shipped by HN points or star velocity, ideas by source authority. Collapse
duplicate stories, note corroboration count.

**4. Research the Big Three.** Pick the three items that most change what
the reader does. For each, use WebSearch and WebFetch to actually research
before writing a word. Do not write from the headline and do not rely on
training data for recent events. Gather: what the company really does, the
technology and what's hard about it, the founders and their prior unfair
advantage, where the idea came from, funding history, competitors, the bear
case. Prefer primary sources — SEC filings, the company's own site, its
**careers page** (job posts leak the real stack), engineer commentary on HN.
Then ~300–400 words per story in the SOP's labelled structure. Every factual
claim carries a real link. Numbers or silence — never "significant growth".
Say plainly when something is undisclosed.

**4b. §W — THE WILDCARD.** Six to eight items from the `wildcard` section
of the raw JSON (Atlas Obscura, Public Domain Review, Longreads, Kottke,
Astral Codex Ten, 99% Invisible, Rest of World, MetaFilter, Works in
Progress, The Diff, Palladium, Noema, Scientific American, and arXiv in
economics / neuroscience / social physics).

This section exists to find interests he does not know he has, so:
**do not curate it toward what he already likes.** Pick for genuine
strangeness and range — history, biology, design, obscurity, global
reporting, one thing that seems to belong in no section at all. One line
of why it caught your eye, no justification of usefulness. It is the only
section where "this is merely interesting" is the correct reason to
include something. Never let `config/interests.md` narrow it.

**5. Fill the rest.** Sections 2–9. Dense, linked, short. An empty section
says so — "Quiet day, nothing worth your money" beats padding. Arena
deadlines render with days remaining, red under 7. Section 6: one skill, one
free resource. Section 7: one canon item not seen recently, with its
relevance stated.

**6. Publish.** Write the complete HTML to `brief.html`.

Then, *only if* an `Artifact` tool exists in this session, publish it with url
`https://claude.ai/artifact/VqyUysjjQhpUjSFhhmMUQJ` (read it first — that is
required — do not create a new artifact, do not pass a favicon). **A headless
`claude -p` run does NOT have this tool. That is expected: skip it silently,
do not retry, do not treat it as a failure.** The published site below is the
real deliverable.

**7. Archive the issue permanently.** Copy the exact HTML to
`issues/<YYYY-MM-DD>.html`, then run `python3 execution/build_index.py`. That
regenerates `index.html` and `latest.html` — `latest.html` is the permanent
link the reader actually uses, so this step is not optional.

**8. Commit.** `git add archive/ issues/ index.html && git commit && git push`.
End commit messages with
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

If a step fails, finish every other step and say plainly what broke. A brief
that ships with a gap beats no brief.
