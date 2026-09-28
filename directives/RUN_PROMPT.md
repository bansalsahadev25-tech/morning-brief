Produce today's issue of The Morning Brief. Collection has already run —
`.tmp/raw_<today>.json` and `archive/<today>.md` exist. Work in order.

**STOP CONDITION — read this first.** If collection exited non-zero, or the
raw JSON holds fewer than 30 items, the environment is broken (almost always
blocked network egress), not the news. In that case: **publish nothing.** Do
not hand-assemble a brief from web search, do not overwrite the existing
artifact, do not write an issue file. Report what failed and stop. A missing
issue is recoverable; a thin issue published over a good one is not.

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

**5. Fill the rest.** Sections 2–9. Dense, linked, short. An empty section
says so — "Quiet day, nothing worth your money" beats padding. Arena
deadlines render with days remaining, red under 7. Section 6: one skill, one
free resource. Section 7: one canon item not seen recently, with its
relevance stated.

**6. Publish.** Write the complete HTML to `brief.html`, then publish with
the Artifact tool passing url
`https://claude.ai/artifact/VqyUysjjQhpUjSFhhmMUQJ` so it updates in place
and the bookmark keeps working. Do not create a new artifact. Do not pass a
favicon. Update the masthead: issue number incremented, today's date, real
counts of items screened and filed. Keep the title tag exactly
`The Morning Brief`.

**7. Archive the issue permanently.** Copy the exact HTML you just published
to `issues/<YYYY-MM-DD>.html`, then run `python3 execution/build_index.py` to
regenerate `index.html`. This is what makes every past issue readable forever
at the GitHub Pages site — the artifact URL only ever shows today.

**8. Commit.** `git add archive/ issues/ index.html && git commit && git push`.
End commit messages with
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

If a step fails, finish every other step and say plainly what broke. A brief
that ships with a gap beats no brief.
