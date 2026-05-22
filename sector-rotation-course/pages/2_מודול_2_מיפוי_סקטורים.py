"""Module 2 - Mapping the 11 SPDR Sector ETFs.

Reference module: per-ETF holdings, fundamental drivers, and cycle behavior.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.page import bootstrap
from utils.style import page_header
from utils.quiz import render_quiz
from utils.market import SECTORS, SECTOR_TICKERS, get_sector_prices


bootstrap("מודול 2 – מיפוי סקטורים")
page_header(
    "🗺️ מודול 2 – מיפוי 11 הסקטורים",
    "כל ה-SPDR Sector ETFs: מה הם מחזיקים, מה מניע אותם, ואיך הם מתנהגים במחזור",
)

# ---------------------------- OPENING ----------------------------

st.markdown(
    """
**11 SPDR sector ETFs** מכסים את כל ה-S&P 500. כל אחד עוקב אחרי סקטור GICS.
ביחד הם מסתכמים ל-~100% מ-SPY (עם סטיות קטנות, בגלל שיוכים שונים בשוליים).

זה **המודול הרפרנס** שלך. כשתראה ב-RRG (מודול 5) שסקטור מסוים מוביל,
תחזור לכאן כדי להבין *מה* בעצם מוביל – אילו חברות, אילו דרייברים פונדמנטליים,
ובאיזה שלב מחזור זה הגיוני.

⏱️ זמן קריאה: ~10–12 דק'.
"""
)


# ---------------------------- SECTION 1: OVERVIEW TABLE ----------------------------

st.markdown("### 1. מבט-על: 11 הסקטורים בטבלה אחת")

st.caption(
    "המשקלים ב-S&P 500 משתנים עם הזמן – אלה ערכי-קירוב לאחרונה. הסכום אינו בדיוק 100% בגלל עיגולים."
)

overview = pd.DataFrame(
    [
        ["XLK", "💻 טכנולוגיה", "~30%", "בינונית-נמוכה", "מחזורי-צמיחה"],
        ["XLF", "🏦 פיננסים", "~13%", "גבוהה (עקום)", "מחזורי מאוד"],
        ["XLV", "🩺 בריאות", "~12%", "נמוכה", "דפנסיבי"],
        ["XLY", "🛍️ צריכה לא-הכרחית", "~10%", "בינונית", "מחזורי מאוד"],
        ["XLC", "📡 תקשורת", "~9%", "בינונית", "מחזורי-צמיחה"],
        ["XLI", "🏭 תעשייה", "~8%", "בינונית", "מחזורי מאוד"],
        ["XLP", "🛒 צריכה בסיסית", "~6%", "בינונית", "דפנסיבי"],
        ["XLE", "⛽ אנרגיה", "~4%", "נמוכה", "מחזורי (סחורות)"],
        ["XLU", "💡 שירותים ציבוריים", "~2.5%", "גבוהה מאוד", "דפנסיבי"],
        ["XLRE", "🏢 נדל\"ן", "~2.5%", "גבוהה מאוד", "מחזורי-ריבית"],
        ["XLB", "🧱 חומרי גלם", "~2%", "בינונית", "מחזורי מאוד"],
    ],
    columns=["סמל", "סקטור", "משקל ב-S&P 500", "רגישות לריבית", "רגישות למחזור"],
)
st.dataframe(overview, use_container_width=True, hide_index=True)

st.markdown(
    """
**איך לקרוא את הטבלה:**

- **רגישות לריבית גבוהה** = XLU ו-XLRE. שניהם ממונפים, מחלקים דיבידנדים שמתחרים בתשואת אג"ח, וערכם הנוכחי של תזרים עתידי יורד כשהריבית עולה.
- **XLF (פיננסים) רגיש לעקום** – בנקים מרוויחים מהפרש בין ריבית קצרה (פיקדונות) לארוכה (הלוואות). עקום תלול = רווחי; עקום שטוח/הפוך = לחץ.
- **XLK (טכנולוגיה) – Long Duration** – חברות שצומחות לאט אבל עם תזרימים גדולים בעתיד. ריבית גבוהה מורידה את הערך הנוכחי שלהן (אבל פחות ממה שאינטואיציה אומרת – הענק החיובי על הרווחיות מרכך את הפגיעה).
- **דפנסיבי** = ביקוש לא-גמיש. אנשים קונים סבון ותרופות גם במיתון. XLP, XLV, XLU.
- **מחזורי** = ביקוש קופץ עם הצמיחה. XLY, XLI, XLB, XLF, XLE.
"""
)


# ---------------------------- SECTION 2: PER-ETF DETAIL ----------------------------

st.divider()
st.markdown("### 2. פירוט – כל אחד מ-11 הסקטורים")

ETF_DETAILS = [
    {
        "ticker": "XLK",
        "holdings": "Apple, Microsoft, Nvidia, Broadcom, Oracle",
        "what": "ענקיות טכנולוגיה: שבבים (Nvidia, Broadcom), תוכנה ושירותי ענן (Microsoft, Oracle), חומרה (Apple).",
        "drivers": "הוצאות IT של חברות (CapEx ענן ו-AI), מחזור המוליכים למחצה, ריבית (long-duration), רגולציה אנטי-טראסט.",
        "phase": "מוביל ב-**early/mid cycle** – כשחברות מרגישות בנוח להשקיע. נחלש ב-late כשהריבית עולה והוצאות מתקצצות.",
    },
    {
        "ticker": "XLF",
        "holdings": "JPMorgan, Berkshire, Bank of America, Wells Fargo, S&P Global",
        "what": "בנקים גדולים (JPM, BAC, WFC), ביטוח (Berkshire), בורסות ונתוני שוק (S&P Global, MSCI), חברות תשלומים.",
        "drivers": "מרווח עקום התשואות, איכות אשראי (NPL ratios), פעילות M&A, ריבית הפד, רגולציית הון (Basel III/IV).",
        "phase": "מוביל ב-**early cycle** – הפד מוריד ריבית, עקום מתלול, הלוואות צומחות. בעייתי בסוף מחזור (פשיטות רגל גוברות).",
    },
    {
        "ticker": "XLV",
        "holdings": "Lilly, J&J, UnitedHealth, AbbVie, Merck",
        "what": "פארמה גדולה (LLY, JNJ, MRK, ABBV), מבטחי בריאות (UNH), ציוד רפואי, ביוטק.",
        "drivers": "צינור התרופות (FDA approvals), מחירי תרופות (לחץ רגולטורי – Medicare), דמוגרפיה (הזדקנות), פטנטים שפגים.",
        "phase": "**דפנסיבי קלאסי** – מוביל ב-late cycle ובמיתון. ביקוש לא נעלם גם בהאטה.",
    },
    {
        "ticker": "XLY",
        "holdings": "Amazon, Tesla, Home Depot, McDonald's, Booking",
        "what": "ענקיות e-commerce (AMZN), רכב (TSLA), שיפוץ הבית (HD), מסעדות (MCD), נסיעות (BKNG).",
        "drivers": "הכנסה פנויה של הצרכן, ביטחון צרכנים, ריבית משכנתאות (משפיע על HD), מחיר דלק, שיעור החיסכון.",
        "phase": "מוביל ב-**early cycle** – אנשים חוזרים להוציא. נחלש ב-late כשהצרכן מותש. **שים לב:** AMZN+TSLA הם כ-40% מהסל, אז ה-ETF מתנהג חלקית כמו growth.",
    },
    {
        "ticker": "XLC",
        "holdings": "Meta, Alphabet (GOOGL+GOOG), Netflix, Disney, T-Mobile",
        "what": "מדיה דיגיטלית (META, GOOGL), סטרימינג (NFLX, DIS), טלקום (T-Mobile, Verizon).",
        "drivers": "תקציבי פרסום (מחזורי!), מנויים, רגולציית פלטפורמות, ריבית (חוב גבוה ב-טלקום).",
        "phase": "**צעיר כסקטור** (פוצל מ-Tech ב-2018). מתנהג כ-mid-cycle/growth – נע עם תקציבי פרסום וסנטימנט.",
    },
    {
        "ticker": "XLI",
        "holdings": "GE, Caterpillar, RTX, Honeywell, Union Pacific",
        "what": "תעופה ותעשייה (GE, HON, RTX), ציוד כבד (CAT), רכבות (UNP, CSX), לוגיסטיקה (UPS).",
        "drivers": "PMI Manufacturing, הזמנות סחורות (Durable Goods), הוצאות הגנה (RTX), סחר בינלאומי, מחיר דיזל.",
        "phase": "**מחזורי קלאסי** – מוביל ב-early cycle עם התאוששות. נחלש בסוף מחזור עם האטה תעשייתית.",
    },
    {
        "ticker": "XLP",
        "holdings": "Costco, Walmart, P&G, Coca-Cola, PepsiCo",
        "what": "רשתות גדולות (COST, WMT), מוצרי בית וטיפוח (PG, CL), משקאות ומזון (KO, PEP, MDLZ).",
        "drivers": "כוח תמחור מול אינפלציה, הוצאות צריכה בסיסיות (לא יורדות במיתון), שער הדולר (חברות גלובליות).",
        "phase": "**דפנסיבי קלאסי** – מוביל ב-late cycle ובמיתון. נחות ב-early/mid כשהצמיחה מהירה.",
    },
    {
        "ticker": "XLE",
        "holdings": "Exxon, Chevron, ConocoPhillips, EOG, Marathon Petroleum",
        "what": "Integrated (XOM, CVX), E&P (COP, EOG), זיקוק (MPC, PSX), שירותי שדה (SLB, HAL).",
        "drivers": "מחיר נפט וגז, מרווחי זיקוק (crack spreads), OPEC+, גיאופוליטיקה, רגולציית פליטות, הוצאות CapEx של החברות.",
        "phase": "מתנהג כסקטור **סחורתי** יותר ממחזורי-קלאסי. מוביל כשאינפלציה עולה (late cycle, סטגפלציה). מנותק חלקית מהמחזור הכלכלי הרגיל.",
    },
    {
        "ticker": "XLU",
        "holdings": "NextEra, Southern, Duke Energy, Constellation, Vistra",
        "what": "חברות חשמל מווסתות (SO, DUK), אנרגיה ירוקה (NEE), גרעין (CEG, VST).",
        "drivers": "ריבית (חוב כבד + תחרות מול אג\"ח), מחיר גז טבעי, רגולציית PUC, ביקוש חשמל (AI data centers – טריגר חדש).",
        "phase": "**דפנסיבי + רגיש לריבית.** מוביל במיתון וכשהפד מוריד. נחות כשהריבית עולה.",
    },
    {
        "ticker": "XLRE",
        "holdings": "Prologis, American Tower, Welltower, Equinix, Realty Income",
        "what": "REITs: לוגיסטיקה (PLD), תקשורת (AMT, CCI), בריאות (WELL), datacenters (EQIX, DLR), קמעונאות (O).",
        "drivers": "ריבית (קריטי – REITs ממונפים), שכר דירה (עם פיגור על אינפלציה), תפוסה, מבנה אגרות חוב.",
        "phase": "**הכי רגיש לריבית.** מוביל כשהפד מתחיל להוריד (early cycle). סובל מאוד כשהריבית עולה (late cycle).",
    },
    {
        "ticker": "XLB",
        "holdings": "Linde, Sherwin-Williams, Air Products, Freeport-McMoRan, Newmont",
        "what": "גזים תעשייתיים (LIN, APD), כימיקלים וצבעים (SHW, ECL), מתכות (FCX – נחושת, NEM – זהב).",
        "drivers": "מחירי סחורות (נחושת, אלומיניום, ליתיום), הסקטור הבנייה והתעשייה, סין (צרכן ענק), שער הדולר.",
        "phase": "**מחזורי-מוקדם.** מוביל בתחילת התאוששות (ביקוש לחומרי גלם קופץ). נחות במיתון.",
    },
]

for d in ETF_DETAILS:
    t = d["ticker"]
    meta = SECTORS[t]
    with st.expander(f"{meta['emoji']} **{t}** – {meta['name_he']} ({meta['name_en']})"):
        st.markdown(f"**5 ההחזקות הגדולות (לפי משקל, משתנה עם הזמן):**  \n_{d['holdings']}_")
        st.markdown(f"**איזה חברות?** {d['what']}")
        st.markdown(f"**דרייברים פונדמנטליים:** {d['drivers']}")
        st.markdown(f"**שלב מחזור אופייני:** {d['phase']}")


# ---------------------------- SECTION 3: LIVE SNAPSHOT ----------------------------

st.divider()
st.markdown("### 3. תמונת מצב חיה – תשואות שנה אחרונה")

try:
    prices = get_sector_prices(period="1y", interval="1wk")
    if prices is None or prices.empty:
        raise ValueError("empty")

    valid_cols = [c for c in SECTOR_TICKERS if c in prices.columns]
    if not valid_cols:
        raise ValueError("no_sectors")

    sub = prices[valid_cols].dropna(how="all")
    if len(sub) < 2:
        raise ValueError("not_enough_rows")

    first = sub.bfill().iloc[0]
    last = sub.ffill().iloc[-1]
    rets = ((last / first) - 1.0).dropna().sort_values()

    if rets.empty:
        raise ValueError("no_returns")

    labels_he = [f"{SECTORS[t]['emoji']} {t} – {SECTORS[t]['name_he']}" for t in rets.index]
    colors = ["#e74c3c" if v < 0 else "#2ecc71" for v in rets.values]
    text_labels = [f"{v * 100:+.1f}%" for v in rets.values]

    fig_rets = go.Figure(
        go.Bar(
            x=rets.values * 100,
            y=labels_he,
            orientation="h",
            marker_color=colors,
            text=text_labels,
            textposition="outside",
        )
    )
    fig_rets.update_layout(
        height=440,
        margin=dict(l=10, r=30, t=20, b=10),
        xaxis=dict(title="תשואה 12 חודשים (%)", zeroline=True, zerolinecolor="#666"),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        dragmode="pan",
    )
    st.plotly_chart(
        fig_rets,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False},
    )
    st.caption(
        "מקור: yfinance, נתונים שבועיים. תשואות מבוססות מחירי סגירה מתואמים (כולל דיבידנדים)."
    )
except Exception:  # noqa: BLE001
    st.info("נתונים חיים אינם זמינים כרגע. נסה שוב מאוחר יותר.")


# ---------------------------- SECTION 4: GICS HIERARCHY ----------------------------

st.divider()
st.markdown("### 4. היררכיית GICS – למה דווקא 11 סקטורים?")

st.markdown(
    """
**GICS** = *Global Industry Classification Standard*. תקן שיתופי של MSCI ו-S&P משנת 1999, שמסווג
כל חברה ציבורית בעולם להיררכיה של 4 רמות:

- **11 סקטורים** (Sectors) – הרמה הרחבה ביותר. זה מה ש-SPDR Select ETFs עוקבים.
- **25 קבוצות תעשייה** (Industry Groups) – למשל "Banks" בתוך Financials.
- **74 תעשיות** (Industries) – למשל "Regional Banks", "Diversified Banks".
- **163 תת-תעשיות** (Sub-Industries) – הרמה הכי גרעינית.

**מי עוד מציע ETFs לסקטורים?**

- **State Street – SPDR Select Sector** (XLK, XLF, ...) – המנהלים שלנו. נזילות גבוהה, דמי ניהול ~0.09%.
- **Vanguard – VGT/VFH/...** – דמי ניהול נמוכים יותר (~0.10%), חלוקה שונה במעט.
- **iShares – IYW/IYF/...** – יקרים יותר (~0.40%) אבל לפעמים בעלי הרכב יותר טהור.

**הסיבה שאנחנו משתמשים ב-XLx:** הם הסטנדרט המקצועי, בעלי הנזילות הכי גבוהה, ועוקבים את הסיווג של S&P 500 בלבד (כלומר 500 חברות גדולות בלבד – לא small caps).
"""
)


# ---------------------------- SECTION 5: LIMITATIONS ----------------------------

st.divider()
st.markdown("### 5. מגבלות של מודל 11-הסקטורים")

st.markdown(
    """
לפני שאתה לוקח את זה לבנק, חשוב להבין מה המודל **לא** עושה טוב:

1. **המודל אמריקאי-במהותו.** הסיווג של GICS לפי החברות ב-S&P 500. רוטציה בינלאומית עובדת אחרת:
   - באירופה, פיננסים שולטים (בנקים גדולים) ויש פחות tech.
   - בקנדה/אוסטרליה, אנרגיה וחומרי גלם דומיננטיים.
   - בשווקים מתעוררים, הסקטור המוביל לרוב אנרגיה/פיננסים/חומרים – לא tech.

2. **ETF סקטוריאלי הוא *סל*.** XLE יכול לעלות גם אם רק XOM ו-CVX עולים (שני שליש מהמשקל). אתה לא קונה "אנרגיה" – אתה קונה ביצועים-משוקללים-לפי-שווי-שוק של חברות אנרגיה.

3. **המשקלים *לא* שווים.**
   - **XLK ~30%** מ-S&P 500.
   - **XLB ~2%** מ-S&P 500.
   - יחס של **15:1**. רוטציה מ-XLK ל-XLB לא משמעותית ברמת התיק כולו.

4. **ריכוזיות בתוך הסקטורים.**
   - XLY: AMZN+TSLA = ~40% מהסל. אז XLY בעצם מתנהג כמו growth-tech-hybrid, לא כמו צרכן-מסורתי.
   - XLC: META+GOOGL = ~40%+. דומה.
   - XLK: AAPL+MSFT+NVDA = ~50%+.

5. **GICS משתנה מדי פעם.** ב-2018, "Communication Services" (XLC) נוצר מחדש: META ו-GOOGL הועברו מ-Tech ל-XLC, ו-DIS, NFLX הועברו מ-Consumer Discretionary. אם אתה מסתכל על נתונים היסטוריים של XLK לפני 2018, הם **לא** ברי-השוואה למה שאתה רואה היום.

**מה לעשות עם המגבלות?**

- אל תתייחס ל-rotation בין סקטורים כפסק דין, אלא כ-tilt קטן (10–30% מהתיק) מעל קור של מדד רחב.
- בדוק את ההחזקות העיקריות של ה-ETF לפני שאתה קונה אותו (יש [קישור באתר SSGA](https://www.ssga.com/us/en/intermediary/etfs/the-spdr-sector-etfs)).
- אם אתה רוצה חשיפה גלובלית, השתמש ב-ETFs בינלאומיים (למשל EWG לגרמניה, EWJ ליפן) ולא רק ב-XLx.
"""
)


# ---------------------------- QUIZ ----------------------------

st.divider()
render_quiz(
    "sector_map",
    [
        {
            "q": "איזה ETF עוקב אחרי סקטור הפיננסים?",
            "options": ["XLF", "XLE", "XLP", "XLY"],
            "answer": 0,
            "explain": "XLF = Financials. JPM, BRK.B, BAC, WFC, S&P Global הם 5 ההחזקות הגדולות.",
        },
        {
            "q": "אילו 3 סקטורים נחשבים *דפנסיביים* קלאסיים?",
            "options": [
                "XLK, XLY, XLF",
                "XLP, XLV, XLU",
                "XLE, XLB, XLI",
                "XLRE, XLC, XLK",
            ],
            "answer": 1,
            "explain": "Staples (XLP), Healthcare (XLV), Utilities (XLU) – הביקוש שלהם לא גמיש, ולכן הם בולמים נפילות במיתון.",
        },
        {
            "q": "איזה סקטור הכי רגיש לריבית (REITs ממונפים + תשואת דיבידנד גבוהה)?",
            "options": ["XLK", "XLRE", "XLY", "XLB"],
            "answer": 1,
            "explain": "XLRE (נדל\"ן/REITs) – חוב כבד מגיב לעלויות מימון, ודיבידנדים מתחרים ישירות בתשואות אג\"ח. XLU רגיש דומה אבל פחות.",
        },
        {
            "q": "מהו הסקטור עם המשקל הגבוה ביותר ב-S&P 500?",
            "options": ["XLF פיננסים", "XLV בריאות", "XLK טכנולוגיה", "XLY צריכה לא-הכרחית"],
            "answer": 2,
            "explain": "XLK ~30% מהמדד – פי 15 בערך מ-XLB (חומרי גלם, ~2%). הריכוז ב-tech הוא המבנה הדומיננטי של ה-S&P היום.",
        },
        {
            "q": "למה רוטציה גלובלית עובדת שונה מרוטציה אמריקאית?",
            "options": [
                "כי GICS שונה בכל מדינה",
                "כי המבנה הסקטוריאלי שונה – למשל באירופה פיננסים גדולים יותר מ-tech, ובקנדה אנרגיה דומיננטית",
                "כי שווקים מתעוררים לא משתמשים ב-ETFs",
                "כי מטבעות זרים מבטלים את התנודתיות",
            ],
            "answer": 1,
            "explain": "מודל 11-הסקטורים מבוסס על המבנה של S&P 500. שווקים אחרים שונים – מה שמוביל בארה\"ב לא בהכרח מוביל באירופה/אסיה.",
        },
    ],
)
