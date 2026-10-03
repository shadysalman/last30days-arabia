"""Arabic language support, --region presets, and flexible --period/--from."""

import argparse
import datetime

import pytest
from lib import arabic, dates, grounding, planner, query, region, relevance

# --- Arabic normalization / detection -------------------------------------

def test_has_arabic():
    assert arabic.has_arabic("الذكاء الاصطناعي في دبي")
    assert arabic.has_arabic("AI في الإمارات")
    assert not arabic.has_arabic("AI in Dubai")
    assert not arabic.has_arabic("")


def test_normalize_folds_spelling_variants():
    # hamza-alef vs bare alef, diacritics, tatweel, taa marbuta
    assert arabic.normalize("الإصطناعي") == arabic.normalize("الاصطناعي")
    assert arabic.normalize("مُحَمَّد") == "محمد"
    assert arabic.normalize("جمـــيل") == "جميل"
    assert arabic.normalize("مدرسة") == arabic.normalize("مدرسه")
    assert arabic.normalize("٢٠٢٦") == "2026"


def test_normalize_leaves_latin_text_untouched():
    text = "Dubai RTA, AI-driven transport!"
    assert arabic.normalize(text) is text


def test_detect_language_arabic_and_hebrew():
    assert planner.detect_language("هيئة الطرق والمواصلات") == "ar"
    assert planner.detect_language("מה חדש") == "he"
    assert planner.detect_language("Dubai metro") is None


def test_relevance_matches_across_arabic_spellings():
    score = relevance.token_overlap_relevance(
        "الذكاء الإصطناعي",
        "مستقبل الذكاء الاصطناعي في الحكومة",
    )
    assert score >= 0.5


def test_arabic_stopwords_dropped_from_tokens():
    tokens = relevance.tokenize("ما هو أفضل الذكاء الاصطناعي في دبي")
    assert "في" not in tokens
    assert arabic.normalize("دبي") in tokens


def test_core_subject_strips_arabic_prefix():
    core = query.extract_core_subject("ماذا يقول الناس عن مترو دبي")
    assert "مترو" in core and "دبي" in core
    assert "يقول" not in core


def test_fallback_plan_elevates_web_for_arabic():
    plan = planner._fallback_plan(
        "النقل الذكي في دبي", ["reddit", "x", "grounding"], None, "default",
    )
    assert plan.subqueries[0].sources[0] == "grounding"


# --- --region presets -------------------------------------------------------

def test_parse_region_single_country():
    focus = region.parse_region("UAE")
    assert focus.country_code == "AE"
    assert "dubai" in focus.subreddits
    assert "gulfnews.com" in focus.news_domains
    assert focus.names_ar == ["الإمارات"]


def test_parse_region_aliases_and_codes():
    assert region.parse_region("jordan").country_code == "JO"
    assert region.parse_region("amman").country_code == "JO"
    assert region.parse_region("KSA").country_code == "SA"
    assert region.parse_region("jo").country_code == "JO"


def test_parse_region_groups_and_lists():
    gcc = region.parse_region("gcc")
    assert {c.code for c in gcc.countries} == {"ae", "sa", "qa", "kw", "bh", "om"}
    assert gcc.country_code is None
    combo = region.parse_region("uae,jordan")
    assert [c.code for c in combo.countries] == ["ae", "jo"]
    mena = region.parse_region("mena")
    assert len(mena.countries) >= 15
    # broad groups stay inside the call budget
    assert len(mena.subreddits) <= 8
    assert len(mena.news_domains) <= 10


def test_parse_region_rejects_unknown():
    with pytest.raises(ValueError):
        region.parse_region("atlantis")
    assert region.parse_region("") is None
    assert region.parse_region(None) is None


def test_apply_region_sets_country_defaults_without_overriding():
    config = {"LAST30DAYS_META_ADS_COUNTRY": "US"}
    region.apply_region(config, region.parse_region("jordan"))
    assert config["LAST30DAYS_PERPLEXITY_COUNTRY"] == "JO"
    assert config["LAST30DAYS_META_ADS_COUNTRY"] == "JO"
    assert config["_region"].country_code == "JO"

    pinned = {"LAST30DAYS_PERPLEXITY_COUNTRY": "GB", "LAST30DAYS_META_ADS_COUNTRY": "FR"}
    region.apply_region(pinned, region.parse_region("uae"))
    assert pinned["LAST30DAYS_PERPLEXITY_COUNTRY"] == "GB"
    assert pinned["LAST30DAYS_META_ADS_COUNTRY"] == "FR"


def test_merge_subreddits_keeps_host_resolved_first():
    focus = region.parse_region("uae")
    merged = region.merge_subreddits(["artificial", "Dubai"], focus)
    assert merged[0] == "artificial"
    assert [s.lower() for s in merged].count("dubai") == 1
    assert region.merge_subreddits(None, None) is None


def test_regional_web_query():
    focus = region.parse_region("jordan")
    q = region.regional_web_query("smart city", focus)
    assert q.startswith("smart city (")
    assert "site:jordantimes.com" in q


def test_web_search_runs_regional_pass(monkeypatch):
    calls = []

    def fake_brave(q, date_range, api_key, count=5, **kwargs):
        calls.append((q, kwargs))
        url = "https://gulfnews.com/a" if "site:" in q else "https://example.com/a"
        return ([{"id": "WB1", "url": url, "title": q, "snippet": "",
                  "date": "2026-10-01", "relevance": 0.8}],
                {"label": "brave", "webSearchQueries": [q], "resultCount": 1})

    monkeypatch.setattr(grounding, "brave_search", fake_brave)
    config = {"BRAVE_API_KEY": "k", "EXCLUDE_SOURCES": "reddit"}
    region.apply_region(config, region.parse_region("uae"))
    items, artifact = grounding.web_search(
        "RTA autonomous taxi", ("2026-09-01", "2026-10-01"), config)
    assert len(calls) == 2
    assert any("site:gulfnews.com" in q for q, _ in calls)
    assert {i["url"] for i in items} == {"https://example.com/a", "https://gulfnews.com/a"}
    assert len(artifact["webSearchQueries"]) == 2


def test_web_search_without_region_is_single_pass(monkeypatch):
    calls = []

    def fake_brave(q, date_range, api_key, count=5, **kwargs):
        calls.append(q)
        return [], {"label": "brave", "webSearchQueries": [q], "resultCount": 0}

    monkeypatch.setattr(grounding, "brave_search", fake_brave)
    grounding.web_search("topic", ("2026-09-01", "2026-10-01"),
                         {"BRAVE_API_KEY": "k"})
    assert calls == ["topic"]


# --- --period / --from ------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("7", 7), ("7d", 7), ("2w", 14), ("3m", 90), ("1y", 365),
    ("week", 7), ("month", 30), ("quarter", 90), ("year", 365),
    ("24h", 1), ("today", 1), ("6 months", 180), ("2 weeks", 14),
    ("أسبوع", 7), ("شهر", 30), ("سنة", 365),
])
def test_parse_period(value, expected):
    assert dates.parse_period(value) == expected


@pytest.mark.parametrize("value", ["", "0d", "-3", "soon", "5x"])
def test_parse_period_rejects_bad_values(value):
    with pytest.raises(ValueError):
        dates.parse_period(value)


def test_days_between_from_and_to():
    assert dates.days_between("2026-01-01", "2026-03-01") == 59
    with pytest.raises(ValueError):
        dates.days_between("2026-03-01", "2026-01-01")


def _ns(**kw):
    base = {"lookback_days": None, "period": None, "from_date": None, "as_of_date": None}
    base.update(kw)
    return argparse.Namespace(**base)


def test_resolve_period_args():
    import last30days as cli

    args = _ns(period=90)
    assert cli._resolve_period_args(args, {}) is None
    assert args.lookback_days == 90

    args = _ns(from_date="2026-01-01", as_of_date="2026-01-31")
    assert cli._resolve_period_args(args, {}) is None
    assert args.lookback_days == 30

    args = _ns()
    cli._resolve_period_args(args, {"LAST30DAYS_DEFAULT_DAYS": "14"})
    assert args.lookback_days == 14

    args = _ns()
    cli._resolve_period_args(args, {})
    assert args.lookback_days is None  # caller keeps its own default

    assert cli._resolve_period_args(_ns(period=7, lookback_days=7), {}) is not None
    assert cli._resolve_period_args(_ns(period=7, from_date="2026-01-01"), {}) is not None


def test_from_date_defaults_end_to_today():
    import last30days as cli

    today = datetime.datetime.now(datetime.timezone.utc).date()
    start = (today - datetime.timedelta(days=10)).isoformat()
    args = _ns(from_date=start)
    assert cli._resolve_period_args(args, {}) is None
    assert args.lookback_days in (9, 10, 11)  # UTC vs local date at midnight


def test_parser_accepts_new_flags():
    import last30days as cli

    args = cli.build_parser().parse_args(
        ["RTA", "--region", "uae,jordan", "--period", "3m"])
    assert args.region == "uae,jordan"
    assert args.period == 90
