#!/usr/bin/env python3
"""
Collect raw items for The Morning Brief.

Keyless sources only. Every collector is independently fault-tolerant:
a dead feed logs a warning and the brief still ships. Output is one
normalized JSON array at .tmp/raw_YYYY-MM-DD.json
"""
import json, re, sys, time, html
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import requests, feedparser

UA = "MorningBrief/1.0 (personal research digest; contact: local)"
HDRS = {"User-Agent": UA}
TIMEOUT = 20
NOW = datetime.now(timezone.utc)
CUTOFF = NOW - timedelta(hours=36)   # 36h so a late-night run misses nothing

items, errors = [], []


def add(section, title, url, source, *, date=None, text="", meta=None):
    if not title or not url:
        return
    items.append({
        "section": section,
        "title": html.unescape(title.strip())[:300],
        "url": url,
        "source": source,
        "date": (date or NOW).isoformat(),
        "text": re.sub(r"<[^>]+>", " ", text or "")[:4000],
        "meta": meta or {},
    })


def guard(fn):
    """Run a collector; never let it kill the run."""
    def wrapped():
        name = fn.__name__
        try:
            t0 = time.time()
            n0 = len(items)
            fn()
            print(f"  ok   {name:<22} +{len(items)-n0:<4} {time.time()-t0:.1f}s")
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__}: {e}")
            print(f"  FAIL {name:<22} {type(e).__name__}: {e}")
    return wrapped


# News expires fast; ideas do not. A Quanta essay or a Stanford lecture is
# worth surfacing a week later, a funding headline is not.
WINDOW = {"learn": 10, "build": 7, "watch": 30, "deals": 14, "problems": 21}


def rss(url, section, source, limit=25, days=None):
    days = days if days is not None else WINDOW.get(section)
    cutoff = (NOW - timedelta(days=days)) if days else CUTOFF
    d = feedparser.parse(requests.get(url, headers=HDRS, timeout=TIMEOUT).content)
    for e in d.entries[:limit]:
        dt = None
        if getattr(e, "published_parsed", None):
            dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
        if dt and dt < cutoff:
            continue
        add(section, e.get("title", ""), e.get("link", ""), source,
            date=dt, text=e.get("summary", ""))


# ----------------------------- collectors -----------------------------

@guard
def hn_frontpage():
    r = requests.get("http://hn.algolia.com/api/v1/search",
                     params={"tags": "front_page", "hitsPerPage": 50},
                     headers=HDRS, timeout=TIMEOUT).json()
    for h in r.get("hits", []):
        pts = h.get("points") or 0
        if pts < 50:
            continue
        add("shipped", h.get("title", ""),
            h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
            "Hacker News",
            text=h.get("story_text", ""),
            meta={"points": pts, "comments": h.get("num_comments"),
                  "hn": f"https://news.ycombinator.com/item?id={h['objectID']}"})


@guard
def hn_show():
    r = requests.get("http://hn.algolia.com/api/v1/search_by_date",
                     params={"tags": "show_hn", "hitsPerPage": 40},
                     headers=HDRS, timeout=TIMEOUT).json()
    for h in r.get("hits", []):
        if (h.get("points") or 0) < 15:
            continue
        add("shipped", h.get("title", ""),
            h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
            "Show HN", text=h.get("story_text", ""),
            meta={"points": h.get("points"), "comments": h.get("num_comments")})


@guard
def hn_ask():
    """Ask HN threads = people describing problems they'd pay to remove."""
    r = requests.get("http://hn.algolia.com/api/v1/search_by_date",
                     params={"tags": "ask_hn", "hitsPerPage": 40},
                     headers=HDRS, timeout=TIMEOUT).json()
    for h in r.get("hits", []):
        if (h.get("points") or 0) < 20:
            continue
        add("ideas", h.get("title", ""),
            f"https://news.ycombinator.com/item?id={h['objectID']}",
            "Ask HN", text=h.get("story_text", ""),
            meta={"points": h.get("points"), "comments": h.get("num_comments")})


MONEY = re.compile(
    r"(\brais(e|es|ed|ing)\b|\bsecures?\b|\bSeries\s+[A-J]\b|\bseed round\b|"
    r"\bpre-seed\b|\bvaluation\b|\bvalued at\b|\bfunding\b|\bIPO\b|"
    r"\bacquir(e|es|ed|ing)\b|\bacquisition\b|\binvest(s|ed|ment|or)\b|"
    r"\bfund\b|\$\s?\d+(\.\d+)?\s?(M|B|bn|billion|million)\b)", re.I)

def classify(title, text):
    """TechCrunch covers everything; only money events belong in §2."""
    blob = f"{title} {text[:600]}"
    if re.search(r"(TechCrunch Disrupt|Expo\+|deal for your|Save \$)", blob, re.I):
        return None                      # their own event marketing
    if MONEY.search(blob):
        return "funding"
    return "macro"


@guard
def techcrunch():
    for u in ["https://techcrunch.com/feed/",
              "https://techcrunch.com/category/startups/feed/"]:
        d = feedparser.parse(requests.get(u, headers=HDRS, timeout=TIMEOUT).content)
        for e in d.entries[:30]:
            dt = None
            if getattr(e, "published_parsed", None):
                dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            if dt and dt < CUTOFF:
                continue
            sec = classify(e.get("title", ""), e.get("summary", ""))
            if sec:
                add(sec, e.get("title", ""), e.get("link", ""), "TechCrunch",
                    date=dt, text=e.get("summary", ""))


@guard
def vc_blogs():
    for u, name in [("https://a16z.com/feed/", "a16z"),
                    ("https://www.sequoiacap.com/feed/", "Sequoia"),
                    ("https://review.firstround.com/feed", "First Round Review"),
                    ("https://www.ycombinator.com/blog/rss", "YC Blog")]:
        try:
            rss(u, "ideas", name, limit=10)
        except Exception as e:
            errors.append(f"vc_blogs/{name}: {e}")


@guard
def labs():
    for u, name in [("https://openai.com/blog/rss.xml", "OpenAI"),
                    ("https://huggingface.co/blog/feed.xml", "Hugging Face"),
                    ("https://blog.google/technology/ai/rss/", "Google AI")]:
        try:
            rss(u, "shipped", name, limit=10)
        except Exception as e:
            errors.append(f"labs/{name}: {e}")


@guard
def arxiv():
    """Where the tech comes from ~18mo before the startup exists."""
    r = requests.get("http://export.arxiv.org/api/query", params={
        "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
        "sortBy": "submittedDate", "sortOrder": "descending",
        "max_results": 60}, headers=HDRS, timeout=TIMEOUT)
    d = feedparser.parse(r.content)
    for e in d.entries:
        add("ideas", e.get("title", "").replace("\n", " "),
            e.get("link", ""), "arXiv", text=e.get("summary", ""))


@guard
def github_trending():
    h = requests.get("https://github.com/trending?since=daily",
                     headers=HDRS, timeout=TIMEOUT).text
    # no official API; parse the repo anchors
    for m in re.finditer(r'<h2 class="h3 lh-condensed">\s*<a href="/([^"]+)"', h):
        repo = m.group(1)
        add("shipped", repo, f"https://github.com/{repo}", "GitHub Trending",
            meta={"kind": "repo"})


def _money(s):
    """Devpost returns prize as HTML. Pull the number out."""
    if not s:
        return 0
    digits = re.sub(r"[^\d]", "", re.sub(r"<[^>]+>", "", str(s)))
    n = int(digits) if digits else 0
    if "\u20b9" in str(s):        # INR -> rough USD so thresholds compare
        n = n // 85
    return n


def _deadline(s):
    """'Sep 25 - 26, 2026' / 'Aug 27 - Sep 26, 2026' -> end datetime."""
    if not s:
        return None
    txt = re.sub(r"<[^>]+>", "", str(s)).strip()
    parts = re.split(r"\s+-\s+", txt)
    end = parts[-1]
    yr = re.search(r"(\d{4})", end)
    year = int(yr.group(1)) if yr else NOW.year
    mon = re.search(r"([A-Z][a-z]{2})", end)
    if not mon:                                  # month omitted: reuse start's
        mon = re.search(r"([A-Z][a-z]{2})", parts[0])
    day = re.search(r"\b(\d{1,2})\b", re.sub(r"\d{4}", "", end))
    if not (mon and day):
        return None
    try:
        return datetime.strptime(f"{mon.group(1)} {int(day.group(1))} {year}",
                                 "%b %d %Y").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


@guard
def devpost():
    """Worth-entering only: real prize or real scale, and time to build."""
    seen_urls = set()
    plans = [("prize-amount", p) for p in (1, 2)] + \
            [("deadline", p) for p in range(1, 7)] + \
            [("recently-added", p) for p in (1, 2)]
    for order, page in plans:
        r = requests.get("https://devpost.com/api/hackathons",
                         params={"order_by": order, "status[]": "open",
                                 "page": page},
                         headers=HDRS, timeout=TIMEOUT).json()
        for h in r.get("hackathons", []):
            url = h.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            prize = _money(h.get("prize_amount"))
            regs = h.get("registrations_count") or 0
            dl = _deadline(h.get("submission_period_dates"))
            days = (dl - NOW).days if dl else None
            # need time to actually build, and a reason to bother
            if days is not None and days < 3:
                continue
            if prize < 1000 and regs < 400:
                continue
            add("arena", re.sub(r"<[^>]+>", "", h.get("title", "")), url, "Devpost",
                text=f"prize ${prize:,} | {regs} registered",
                meta={"deadline": dl.strftime("%Y-%m-%d") if dl else None,
                      "days_left": days, "prize_usd": prize,
                      "registrations": regs,
                      "themes": [t.get("name") for t in h.get("themes", [])],
                      "builds": "competition win"})


@guard
def yc_rfs():
    """YC saying 'we will fund X' = pre-validated idea with a buyer."""
    t = requests.get("https://www.ycombinator.com/rfs",
                     headers=HDRS, timeout=TIMEOUT).text
    txt = re.sub(r"<script.*?</script>", " ", t, flags=re.S)
    txt = re.sub(r"<[^>]+>", "\n", txt)
    txt = re.sub(r"\n{2,}", "\n", txt)
    add("ideas", "YC Requests for Startups — current list",
        "https://www.ycombinator.com/rfs", "Y Combinator",
        text=txt[:4000], meta={"kind": "rfs", "diff_me": True})


@guard
def reddit_pain():
    """Founders describing problems they would pay to remove."""
    for sub in ["startups", "SaaS", "Entrepreneur", "smallbusiness"]:
        try:
            r = requests.get(f"https://www.reddit.com/r/{sub}/top.rss",
                             params={"t": "day"}, headers=HDRS, timeout=TIMEOUT)
            d = feedparser.parse(r.content)
            for e in d.entries[:12]:
                title = re.sub(r'["\u201c\u201d]?I will not promote["\u201c\u201d]?', "",
                               e.get("title", ""), flags=re.I).strip(" -\u2014")
                add("ideas", title, e.get("link", ""), f"r/{sub}",
                    text=e.get("summary", ""))
        except Exception as ex:
            errors.append(f"reddit/{sub}: {ex}")


@guard
def macro():
    for u, name in [("https://stratechery.com/feed/", "Stratechery"),
                    ("https://www.mckinsey.com/insights/rss", "McKinsey")]:
        try:
            rss(u, "macro", name, limit=12)
        except Exception as e:
            errors.append(f"macro/{name}: {e}")


@guard
def class_central():
    rss("https://www.classcentral.com/report/feed/", "deals",
        "Class Central", limit=15)




# ======================================================================
#  EXPANSION — learning, deep tech, making, and things worth watching.
#  All keyless. Sections: learn / watch / build feed §3, §4, §7 and §9.
# ======================================================================

def feeds(pairs, section, limit=12):
    """Run a batch of RSS feeds into one section; one dead feed never
    kills the batch."""
    for url, name in pairs:
        try:
            rss(url, section, name, limit=limit)
        except Exception as e:
            errors.append(f"{section}/{name}: {type(e).__name__}")


@guard
def hn_best():
    """hnrss.org/best — the week's best, not just today's noisiest."""
    rss("https://hnrss.org/best", "shipped", "HN Best", limit=30)


@guard
def lobsters():
    """Higher signal-to-noise than HN for deep technical work."""
    rss("https://lobste.rs/rss", "shipped", "Lobsters", limit=25)


@guard
def techmeme():
    """Aggregator of aggregators — catches what everything else missed."""
    rss("https://www.techmeme.com/feed.xml", "macro", "Techmeme", limit=15)


@guard
def science_and_ideas():
    """The 'cool stuff' tier: real science writing, not press releases."""
    feeds([
        ("https://api.quantamagazine.org/feed/",        "Quanta"),
        ("https://nautil.us/feed/",                     "Nautilus"),
        ("https://aeon.co/feed.rss",                    "Aeon"),
        ("https://news.mit.edu/rss/feed",               "MIT News"),
        ("https://www.technologyreview.com/feed/",      "MIT Tech Review"),
        ("https://spectrum.ieee.org/feeds/feed.rss",    "IEEE Spectrum"),
        ("https://marginalrevolution.com/feed",         "Marginal Revolution"),
        ("https://www.construction-physics.com/feed",   "Construction Physics"),
    ], "learn", limit=10)


@guard
def makers():
    """Hardware, electronics, people building physical things.
    Directly relevant to the tiltrotor build."""
    feeds([
        ("https://hackaday.com/blog/feed/",  "Hackaday"),
        ("https://blog.adafruit.com/feed/",  "Adafruit"),
    ], "build", limit=15)


@guard
def reddit_build():
    """Where people fly, crash and debug the thing he is building."""
    for sub in ["rcplanes", "Multicopter", "diyelectronics", "AskEngineers"]:
        try:
            r = requests.get(f"https://www.reddit.com/r/{sub}/top.rss",
                             params={"t": "week"}, headers=HDRS, timeout=TIMEOUT)
            d = feedparser.parse(r.content)
            for e in d.entries[:10]:
                add("build", e.get("title", ""), e.get("link", ""), f"r/{sub}",
                    text=e.get("summary", ""))  # weekly top; no date filter
        except Exception as ex:
            errors.append(f"reddit_build/{sub}: {type(ex).__name__}")


@guard
def ai_practitioners():
    """People who actually ship with this stuff, not press about it."""
    feeds([
        ("https://simonwillison.net/atom/everything/", "Simon Willison"),
        ("https://www.interconnects.ai/feed",          "Interconnects"),
        ("https://importai.substack.com/feed",         "Import AI"),
    ], "ideas", limit=10)


@guard
def newsrooms():
    """Broader tech desks — catches consumer, policy and weird."""
    feeds([
        ("https://feeds.arstechnica.com/arstechnica/index", "Ars Technica"),
        ("https://www.theverge.com/rss/index.xml",          "The Verge"),
        ("https://www.404media.co/rss/",                    "404 Media"),
    ], "macro", limit=12)


@guard
def money_desks():
    """Funding coverage beyond TechCrunch, including where he lives."""
    feeds([
        ("https://news.crunchbase.com/feed/", "Crunchbase News"),
        ("https://sifted.eu/feed",            "Sifted"),
        ("https://inc42.com/feed/",           "Inc42"),
        ("https://yourstory.com/feed",        "YourStory"),
    ], "funding", limit=12)


# Channel ids are stable; resolving handles at runtime is slower and brittle.
YT = [
    ("UCctkeBNtFIOn7Yl_9TTj_4w", "Stanford eCorner"),
    ("UCcefcZRL2oaA_uBNeo5UOWg", "Y Combinator"),
    ("UCBa5G_ESCn8Yd4vw5U-gIcg", "Stanford Online"),
    ("UC1LpsuAUaKoMzzJSEt5WImw", "Asianometry"),
    ("UCyFqFYfTW2VoIQKylJ04Rtw", "Acquired"),
    ("UCHnyfMqiRRG1u-2MsSQLbXA", "Veritasium"),
    ("UCYO_jab_esuFRV4b17AJtAw", "3Blue1Brown"),
    ("UCSHZKyawb77ixDdsGog4iWA", "Lex Fridman"),
    ("UC6uKrU_WqJ1R2HMTY3LIx5Q", "Everyday Astronaut"),
    ("UCR1IuLEqb6UEA_zQ81kwXfg", "Real Engineering"),
    ("UC9cn0TuPq4dnbTY-CBsm8XA", "a16z"),
    ("UCbfYPyITQ-7l4upoX8nvctg", "Two Minute Papers"),
    ("UC9-y-6csu5WGm29I7JiwpnA", "Computerphile"),
    ("UCMOqf8ab-42UUQIdVoKwjlQ", "Practical Engineering"),
]


# YouTube 404s unfamiliar user-agents on the feed endpoint, and does it
# intermittently — it served MorningBrief/1.0 fine one day and refused it
# the next. Always ask as a browser, and retry once on a 404.
BROWSER_UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/125.0 Safari/537.36"}


@guard
def youtube():
    """Lectures and long-form, keyless via channel RSS. Feeds §7.
    Window is wider than 36h — a good lecture does not expire."""
    window = NOW - timedelta(days=30)
    live = 0
    for cid, name in YT:
        got = 0
        for attempt in (1, 2):
            try:
                r = requests.get("https://www.youtube.com/feeds/videos.xml",
                                 params={"channel_id": cid},
                                 headers=BROWSER_UA, timeout=TIMEOUT)
                d = feedparser.parse(r.content)
                if not d.entries:
                    if attempt == 1:
                        time.sleep(4.0)          # transient rate limit
                        continue
                    errors.append(f"youtube/{name}: HTTP {r.status_code}, no entries")
                    break
                for e in d.entries[:8]:
                    dt = None
                    if getattr(e, "published_parsed", None):
                        dt = datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
                    if dt and dt < window:
                        continue
                    add("watch", e.get("title", ""), e.get("link", ""), name,
                        date=dt, meta={"kind": "video"})
                    got += 1
                break
            except Exception as ex:
                errors.append(f"youtube/{name}: {type(ex).__name__}")
                break
        if got:
            live += 1
        time.sleep(2.0)                          # YouTube rate-limits hard
    # Silent emptiness is the failure mode that cost a whole section
    # yesterday. If no channel answered, that is a fault, not a quiet week.
    if live == 0:
        raise RuntimeError("all 14 YouTube channels returned nothing")


@guard
def hf_trending():
    """What the open-weights world is actually downloading this week."""
    for kind in ("models", "datasets"):
        try:
            r = requests.get(f"https://huggingface.co/api/{kind}",
                             params={"sort": "trendingScore", "direction": -1,
                                     "limit": 15},
                             headers=HDRS, timeout=TIMEOUT).json()
            for m in r:
                mid = m.get("id", "")
                add("shipped", f"{mid}", f"https://huggingface.co/{mid}",
                    f"HF trending {kind[:-1]}",
                    meta={"likes": m.get("likes"),
                          "downloads": m.get("downloads")})
        except Exception as ex:
            errors.append(f"hf/{kind}: {type(ex).__name__}")


@guard
def problem_sources():
    """Places that publish HARD PROBLEMS rather than news. Feeds §0.
    Window is wide — a hard problem does not expire in 36 hours."""
    feeds([
        ("https://www.darpa.mil/rss.xml", "DARPA"),
        ("https://ifp.org/feed/",         "Institute for Progress"),
    ], "problems", limit=15)


COLLECTORS = [
    # core wire
    hn_frontpage, hn_show, hn_ask, hn_best, lobsters, techcrunch, techmeme,
    newsrooms, vc_blogs, labs, money_desks,
    # research + ideas
    arxiv, ai_practitioners, yc_rfs, reddit_pain, macro,
    # shipped + trending
    github_trending, hf_trending,
    # learning, watching, making
    science_and_ideas, youtube, makers, reddit_build, problem_sources,
    # doors
    devpost, class_central,
]

if __name__ == "__main__":
    print(f"collecting  {NOW:%Y-%m-%d %H:%M} UTC")
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda f: f(), COLLECTORS))

    # dedup by url
    seen, uniq = set(), []
    for it in items:
        k = it["url"].split("?")[0].rstrip("/")
        if k in seen:
            continue
        seen.add(k)
        uniq.append(it)

    out = f".tmp/raw_{NOW:%Y-%m-%d}.json"
    json.dump({"generated": NOW.isoformat(), "count": len(uniq),
               "errors": errors, "items": uniq},
              open(out, "w"), indent=1)

    from collections import Counter
    print(f"\n{len(uniq)} unique items -> {out}")
    for s, n in Counter(i["section"] for i in uniq).most_common():
        print(f"   {s:<10} {n}")
    if errors:
        print(f"\n{len(errors)} source errors (non-fatal):")
        for e in errors[:12]:
            print("   -", e)

    # ---- collection floor -------------------------------------------------
    # A normal run returns 100-150 items. Anything near zero means the
    # environment is broken (network egress blocked, DNS down, proxy), NOT
    # that the news was quiet. Fail loudly so nothing downstream tries to
    # improvise a brief and publish it over a good one.
    FLOOR = 30
    if len(uniq) < FLOOR:
        dead = len(errors)
        print(f"\nFATAL: only {len(uniq)} items (floor {FLOOR}), "
              f"{dead} collectors failed.")
        print("This is an environment failure, not a quiet news day.")
        print("Most likely: network egress is blocked for the source hosts.")
        print("DO NOT publish a brief from this run.")
        sys.exit(2)
