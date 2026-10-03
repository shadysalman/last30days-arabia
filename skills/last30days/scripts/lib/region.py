"""Middle East / Arab-world regional focus (``--region``).

A region preset tells the engine where the conversation it should surface
actually happens for a given country: the local subreddits, the national and
pan-Arab news sites, the country code web-search and ad-library APIs expect,
and the Arabic name of the country (so the host planner can write Arabic
subqueries). Nothing here calls the network; ``apply_region`` only stashes
the resolved preset on the run config, and the source adapters read it.

Accepted values (comma-separated, case-insensitive):

- ISO country codes: ``ae`` (UAE), ``sa``, ``qa``, ``kw``, ``bh``, ``om``,
  ``jo`` (Jordan), ``lb``, ``ps``, ``sy``, ``iq``, ``eg``, ``ly``, ``tn``,
  ``dz``, ``ma``, ``sd``, ``ye``
- Common names/aliases: ``uae``, ``dubai``, ``abu-dhabi``, ``jordan``,
  ``amman``, ``saudi``, ``ksa``, ``egypt`` ...
- Groups: ``gcc``, ``levant``, ``maghreb`` / ``north-africa``, ``mena`` /
  ``arab`` / ``middle-east`` (every country above)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Country:
    code: str                      # ISO 3166-1 alpha-2, lower-case
    name: str                      # English name used in search queries
    name_ar: str                   # Arabic name for Arabic subqueries
    subreddits: tuple[str, ...] = ()
    news_domains: tuple[str, ...] = ()


# Pan-Arab communities and outlets that are relevant to every country preset.
PAN_ARAB_SUBREDDITS = ("arabs", "MiddleEast")
PAN_ARAB_DOMAINS = (
    "aljazeera.net", "alarabiya.net", "skynewsarabia.com", "asharq.com",
    "aawsat.com", "cnbcarabia.com", "independentarabia.com",
    "arabnews.com", "thenationalnews.com", "zawya.com", "arabianbusiness.com",
    "agbi.com", "magnitt.com", "wamda.com",
)

COUNTRIES: dict[str, Country] = {c.code: c for c in (
    Country("ae", "UAE", "الإمارات",
            ("dubai", "UAE", "abudhabi", "Sharjah"),
            ("gulfnews.com", "khaleejtimes.com", "thenationalnews.com",
             "wam.ae", "albayan.ae", "emaratalyoum.com", "alkhaleej.ae",
             "alittihad.ae", "arabianbusiness.com", "zawya.com")),
    Country("sa", "Saudi Arabia", "السعودية",
            ("saudiarabia", "riyadh", "jeddah"),
            ("arabnews.com", "saudigazette.com.sa", "spa.gov.sa",
             "okaz.com.sa", "sabq.org", "aleqt.com", "argaam.com",
             "alriyadh.com")),
    Country("qa", "Qatar", "قطر",
            ("qatar", "doha"),
            ("thepeninsulaqatar.com", "gulf-times.com", "qna.org.qa",
             "raya.com", "al-sharq.com", "dohanews.co")),
    Country("kw", "Kuwait", "الكويت",
            ("kuwait",),
            ("kuwaittimes.com", "arabtimesonline.com", "kuna.net.kw",
             "alqabas.com", "alraimedia.com")),
    Country("bh", "Bahrain", "البحرين",
            ("Bahrain",),
            ("gdnonline.com", "bna.bh", "alayam.com", "alwatannews.net")),
    Country("om", "Oman", "عمان",
            ("Oman",),
            ("timesofoman.com", "omanobserver.om", "alroya.om",
             "omannews.gov.om", "atheer.om")),
    Country("jo", "Jordan", "الأردن",
            ("jordan", "amman"),
            ("jordantimes.com", "petra.gov.jo", "alghad.com", "alrai.com",
             "ammonnews.net", "royanews.tv", "addustour.com", "jo24.net")),
    Country("lb", "Lebanon", "لبنان",
            ("lebanon", "beirut"),
            ("lorientlejour.com", "naharnet.com", "annahar.com",
             "lbcgroup.tv", "the961.com")),
    Country("ps", "Palestine", "فلسطين",
            ("Palestine",),
            ("wafa.ps", "maannews.net", "alquds.com")),
    Country("sy", "Syria", "سوريا",
            ("Syria",),
            ("sana.sy", "enabbaladi.net", "syriadirect.org")),
    Country("iq", "Iraq", "العراق",
            ("Iraq", "baghdad"),
            ("ina.iq", "shafaq.com", "rudaw.net", "alsumaria.tv")),
    Country("eg", "Egypt", "مصر",
            ("Egypt", "cairo"),
            ("ahram.org.eg", "egyptindependent.com", "youm7.com",
             "masrawy.com", "enterprise.press", "dailynewsegypt.com",
             "almasryalyoum.com")),
    Country("ly", "Libya", "ليبيا",
            ("libya",),
            ("libyaobserver.ly", "alwasat.ly", "libyaherald.com")),
    Country("tn", "Tunisia", "تونس",
            ("Tunisia",),
            ("tap.info.tn", "businessnews.com.tn", "kapitalis.com")),
    Country("dz", "Algeria", "الجزائر",
            ("algeria",),
            ("aps.dz", "echoroukonline.com", "tsa-algerie.com")),
    Country("ma", "Morocco", "المغرب",
            ("Morocco",),
            ("hespress.com", "moroccoworldnews.com", "le360.ma",
             "medias24.com")),
    Country("sd", "Sudan", "السودان",
            ("Sudan",),
            ("suna-sd.net", "sudantribune.com", "dabangasudan.org")),
    Country("ye", "Yemen", "اليمن",
            ("Yemen",),
            ("sabanew.net", "almasdaronline.com")),
)}

GROUPS: dict[str, tuple[str, ...]] = {
    "gcc": ("ae", "sa", "qa", "kw", "bh", "om"),
    "gulf": ("ae", "sa", "qa", "kw", "bh", "om"),
    "levant": ("jo", "lb", "ps", "sy", "iq"),
    "maghreb": ("ma", "dz", "tn", "ly"),
    "north-africa": ("eg", "ly", "tn", "dz", "ma", "sd"),
    "mena": tuple(COUNTRIES),
    "arab": tuple(COUNTRIES),
    "arab-world": tuple(COUNTRIES),
    "middle-east": tuple(COUNTRIES),
}

ALIASES: dict[str, str] = {
    "uae": "ae", "emirates": "ae", "dubai": "ae", "abu-dhabi": "ae",
    "abudhabi": "ae", "sharjah": "ae",
    "ksa": "sa", "saudi": "sa", "saudi-arabia": "sa", "riyadh": "sa",
    "qatar": "qa", "doha": "qa",
    "kuwait": "kw", "bahrain": "bh", "oman": "om", "muscat": "om",
    "jordan": "jo", "amman": "jo",
    "lebanon": "lb", "beirut": "lb", "palestine": "ps", "syria": "sy",
    "iraq": "iq", "egypt": "eg", "cairo": "eg", "libya": "ly",
    "tunisia": "tn", "algeria": "dz", "morocco": "ma", "sudan": "sd",
    "yemen": "ye",
}

# Per-country caps keep a broad group (e.g. ``mena``) from fanning out into
# dozens of extra Reddit and web calls.
_MAX_SUBREDDITS = 8
_MAX_DOMAINS = 10


@dataclass(frozen=True)
class RegionFocus:
    """A resolved ``--region`` value."""

    label: str
    countries: tuple[Country, ...]
    language: str = "ar"
    subreddits: tuple[str, ...] = field(default=())
    news_domains: tuple[str, ...] = field(default=())

    @property
    def country_code(self) -> str | None:
        """Two-letter upper-case code when the focus is a single country."""
        if len(self.countries) == 1:
            return self.countries[0].code.upper()
        return None

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.countries]

    @property
    def names_ar(self) -> list[str]:
        return [c.name_ar for c in self.countries]


def _dedupe(values) -> tuple[str, ...]:
    seen: dict[str, str] = {}
    for value in values:
        key = value.lower()
        if key not in seen:
            seen[key] = value
    return tuple(seen.values())


def parse_region(value: str | None) -> RegionFocus | None:
    """Resolve a ``--region`` string; raise ValueError on unknown tokens."""
    if not value or not value.strip():
        return None
    codes: list[str] = []
    for raw in value.split(","):
        token = raw.strip().lower().replace("_", "-").replace(" ", "-")
        if not token:
            continue
        if token in GROUPS:
            codes.extend(GROUPS[token])
        elif token in COUNTRIES:
            codes.append(token)
        elif token in ALIASES:
            codes.append(ALIASES[token])
        else:
            known = sorted(set(COUNTRIES) | set(GROUPS) | set(ALIASES))
            raise ValueError(
                f"Unknown region {raw.strip()!r}. Use a country code, name or "
                f"group, e.g. ae, jordan, gcc, levant, mena. Known: {', '.join(known)}"
            )
    codes = list(dict.fromkeys(codes))
    if not codes:
        return None
    countries = tuple(COUNTRIES[c] for c in codes)
    multi = len(countries) > 1
    # Single country: its own communities first, then pan-Arab ones.
    # Group: the first subreddit of each country (its main community) so a
    # broad group stays within the call budget.
    subs = [s for c in countries for s in (c.subreddits[:1] if multi else c.subreddits)]
    doms = [d for c in countries for d in (c.news_domains[:2] if multi else c.news_domains)]
    subreddits = _dedupe(subs + list(PAN_ARAB_SUBREDDITS))[:_MAX_SUBREDDITS]
    news_domains = _dedupe(doms + list(PAN_ARAB_DOMAINS))[:_MAX_DOMAINS]
    return RegionFocus(
        label=value.strip(),
        countries=countries,
        subreddits=subreddits,
        news_domains=news_domains,
    )


def apply_region(config: dict, focus: RegionFocus | None) -> None:
    """Stash the region on the run config and set country-aware defaults.

    Country codes are only filled in when the user has not already pinned
    them, so an explicit ``LAST30DAYS_PERPLEXITY_COUNTRY`` still wins.
    """
    if focus is None:
        return
    config["_region"] = focus
    code = focus.country_code
    if code:
        if not config.get("LAST30DAYS_PERPLEXITY_COUNTRY"):
            config["LAST30DAYS_PERPLEXITY_COUNTRY"] = code
        if (config.get("LAST30DAYS_META_ADS_COUNTRY") or "US").upper() == "US":
            config["LAST30DAYS_META_ADS_COUNTRY"] = code


def merge_subreddits(existing: list[str] | None, focus: RegionFocus | None) -> list[str] | None:
    """Append the region's subreddits to any the host already resolved."""
    if focus is None:
        return existing
    merged = list(existing or []) + list(focus.subreddits)
    return list(_dedupe(merged)) or None


def regional_web_query(query: str, focus: RegionFocus) -> str:
    """Restrict a web query to the region's news sites with ``site:`` ORs."""
    sites = " OR ".join(f"site:{d}" for d in focus.news_domains)
    return f"{query} ({sites})"


def describe(focus: RegionFocus) -> str:
    """One-line human summary for progress output."""
    names = ", ".join(focus.names)
    return (
        f"Region focus: {names} | {len(focus.subreddits)} regional subreddits, "
        f"{len(focus.news_domains)} regional news sites"
    )
