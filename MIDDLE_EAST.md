# Middle East & Arabic edition

This fork adds Arabic-language support, Middle East coverage, and research windows other than 30 days:

```
/last30days RTA Dubai autonomous taxis --region=uae
/last30days الذكاء الاصطناعي في الحكومة --region=uae,jordan --period=3m
/last30days fintech regulation --region=gcc --from=2026-01-01 --as-of=2026-06-30
/last30days Amman smart city --region=jordan --period=1y
```

- **`--region`**: `uae`, `jordan`, `saudi`, `qatar`, `kuwait`, `bahrain`, `oman`, `egypt`, `lebanon`, `iraq`, `palestine`, `syria`, `morocco`, `tunisia`, `algeria`, `libya`, `sudan`, `yemen`, or the groups `gcc`, `levant`, `maghreb`, `north-africa`, `mena`. It adds local subreddits (r/dubai, r/UAE, r/jordan, r/amman, r/saudiarabia, r/arabs...) and a second web pass over regional news (Gulf News, Khaleej Times, The National, WAM, Al Bayan, Jordan Times, Al Ghad, Petra, Arab News, Asharq Al-Awsat, Al Jazeera, Al Arabiya, Sky News Arabia, Zawya...).
- **Arabic topics** are detected and normalized (أ/إ/آ, ة/ه, ى/ي, diacritics), so different spellings of the same word match. The agent writes an extra Arabic subquery for X, YouTube, TikTok, Instagram and the web.
- **Any period**: `--period=7d|2w|3m|6m|1y` (or `week`, `month`, `quarter`, `year`, `أسبوع`, `شهر`, `سنة`), `--days=N`, or `--from=YYYY-MM-DD` with an optional `--as-of` end date. You can also just ask in plain language: "...over the last quarter" / "خلال آخر ثلاثة أشهر".
- **Defaults** in `~/.config/last30days/.env`: `LAST30DAYS_REGION=uae,jordan` and `LAST30DAYS_DEFAULT_DAYS=90`.
- **Best results**: add a web search key (`BRAVE_API_KEY`, 2,000 free queries/month) for the regional news pass, and a `SCRAPECREATORS_API_KEY` for TikTok, Instagram and LinkedIn, where most Gulf conversation happens.

Full option reference: [CONFIGURATION.md → Middle East region](CONFIGURATION.md#middle-east-region-last30days_region---region).

## النسخة العربية

<div dir="rtl">

تضيف هذه النسخة إلى أداة ‎/last30days‎ ثلاث قدرات:

- **التغطية الإقليمية (‎--region‎):** الإمارات، الأردن، السعودية، قطر، الكويت، البحرين، عُمان، مصر، لبنان، العراق، فلسطين، سوريا، المغرب، تونس، الجزائر، ليبيا، السودان، اليمن، أو مجموعات مثل ‎gcc‎ (الخليج)، ‎levant‎ (بلاد الشام)، ‎maghreb‎، ‎mena‎ (العالم العربي كاملاً). تضيف مجتمعات Reddit المحلية، وجولة بحث ثانية في المواقع الإخبارية الوطنية والعربية (البيان، الإمارات اليوم، وام، الغد، بترا، الشرق الأوسط، الجزيرة، العربية، سكاي نيوز عربية...).
- **دعم اللغة العربية:** يتم التعرف على المواضيع المكتوبة بالعربية تلقائياً، وتوحيد الإملاء (أ/إ/آ، ة/ه، ى/ي، التشكيل والتطويل) حتى تتطابق الكتابات المختلفة للكلمة نفسها، ويكتب المساعد استعلاماً عربياً إضافياً لمنصات X ويوتيوب وتيك توك وإنستغرام والويب.
- **أي فترة زمنية:** ليس فقط آخر 30 يوماً. استخدم ‎--period=7d‎ (أسبوع)، ‎--period=3m‎ (ثلاثة أشهر)، ‎--period=1y‎ (سنة)، أو ‎--from=2026-01-01 --as-of=2026-03-31‎ لفترة محددة. ويمكنك ببساطة أن تكتب الطلب بلغتك: «خلال آخر ثلاثة أشهر» أو «منذ بداية العام».

</div>

```
/last30days هيئة الطرق والمواصلات التاكسي ذاتي القيادة --region=uae
/last30days التحول الرقمي الحكومي --region=uae,jordan --period=3m
/last30days الذكاء الاصطناعي في الخليج --region=gcc --period=1y
```

<div dir="rtl">

**إعدادات افتراضية** في الملف ‎~/.config/last30days/.env‎:

</div>

```
LAST30DAYS_REGION=uae,jordan
LAST30DAYS_DEFAULT_DAYS=90
BRAVE_API_KEY=...
```
