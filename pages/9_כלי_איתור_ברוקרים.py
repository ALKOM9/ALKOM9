"""Broker lookup tool – shows regulators, well-known brokers per country,
and a universal due-diligence checklist. EDUCATIONAL ONLY.

Nothing in this file is a recommendation. Each broker entry includes the
regulator's official lookup URL so the user can verify the licence
themselves.
"""
from __future__ import annotations

import streamlit as st

from utils.page import bootstrap, page_end


bootstrap("כלי איתור ברוקרים")

st.markdown("## 🔎 כלי איתור ברוקרי מט\"ח לפי מדינה")
st.caption("רשימה מבוססת מידע ציבורי על רגולטורים וברוקרים, לצרכי לימוד בלבד.")
st.divider()

st.error(
    "⛔ **חובה לקרוא לפני שימוש:**\n\n"
    "- **אינני יועץ פיננסי. הכלי אינו המלצה לבחור בברוקר כלשהו.**\n"
    "- המידע נכון לרגע כתיבת הקורס, מבוסס על פרסומים פומביים של הרגולטורים והברוקרים, וייתכן שהשתנה.\n"
    "- **חובה לאמת באופן עצמאי** את רישיון הברוקר דרך הקישור הרשמי לרגולטור, לפני כל הפקדה.\n"
    "- בחירת ברוקר היא החלטה פיננסית משמעותית – מומלץ להתייעץ עם בעל רישיון מתאים.\n"
    "- הכלי אינו מדרג ברוקרים. הסדר אלפביתי, לא לפי איכות."
)

st.divider()


COUNTRIES_DATA = {
    "ישראל": {
        "regulators": [
            {
                "name": "רשות ניירות ערך (ISA)",
                "name_en": "Israel Securities Authority",
                "what": "מפקחת על זירות סוחר מקומיות לפי חוק זירות סוחר (2010). זירות מורשות מנהלות מסחר ב-CFD/Forex לתושבי ישראל. מסחר באמצעות פלטפורמה זרה שלא רשומה ב-ISA – אינו חוקי לשיווק אקטיבי בעברית בארץ, אך תושב ישראל שיוזם עצמאית פנייה לברוקר זר אינו עובר עבירה.",
                "lookup_url": "https://www.isa.gov.il/Documents/Information/Trading_Arena/list.pdf",
            },
        ],
        "compensation": "אין במסגרת ה-ISA כיסוי ביטוחי לכספים המופקדים בזירת סוחר במקרה של חדלות פירעון. תושבי ישראל שסוחרים בברוקר זר נסמכים על תכנית הפיצוי של הרגולטור הזר (FSCS בריטניה, ICF קפריסין, וכד').",
        "tax": "רווחים ממסחר Forex/CFD מחויבים במס רווח הון בשיעור 25% (יחיד) – הרווח מחושב במונחי שקלים בעת המימוש. חובה לדווח גם אם החשבון בברוקר זר.",
        "warnings": [
            "**חוק זירות סוחר**: שיווק אקטיבי בעברית של ברוקר זר ללא רישיון ISA אינו חוקי. ברוקרים שעושים זאת – דגל אדום ברור.",
            "**רגולציה לא רלוונטית**: רגולציה של איי קיימן / וונואטו / סנט וינסנט והגרנדינים אינה ערובה לבטיחות. שורת רגולציה איכותית: FCA > ASIC > BaFin > CySEC > אחר.",
            "**דיווח לרשויות**: חשבונות בחו\"ל בסכומים מעל הסף – חובת דיווח לרשות המסים."
        ],
        "brokers": [
            {
                "name": "AvaTrade",
                "type": "Market Maker",
                "regulators": ["Central Bank of Ireland", "ASIC", "FSA Japan", "FSCA דרום אפריקה"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "0.9 pip (ספרד קבוע)",
                "website": "https://www.avatrade.com",
            },
            {
                "name": "eToro",
                "type": "Market Maker (Social Trading)",
                "regulators": ["CySEC", "FCA", "ASIC", "FinCEN"],
                "min_deposit": "$50 (משתנה לפי מדינה)",
                "avg_eurusd_spread": "1.0 pip (ספרד קבוע)",
                "website": "https://www.etoro.com",
            },
            {
                "name": "IC Markets",
                "type": "ECN / STP",
                "regulators": ["ASIC", "CySEC", "FSA Seychelles"],
                "min_deposit": "$200",
                "avg_eurusd_spread": "0.1 pip + עמלה $3.5 לכל leg",
                "website": "https://www.icmarkets.com",
            },
            {
                "name": "Interactive Brokers (IBKR)",
                "type": "ECN / Multi-asset",
                "regulators": ["SEC", "FINRA", "FCA", "IIROC"],
                "min_deposit": "אין מינימום (ישן מחייב)",
                "avg_eurusd_spread": "0.1-0.4 pip + עמלה",
                "website": "https://www.interactivebrokers.com",
            },
            {
                "name": "Pepperstone",
                "type": "ECN / STP",
                "regulators": ["ASIC", "FCA", "CySEC", "BaFin", "DFSA"],
                "min_deposit": "$200",
                "avg_eurusd_spread": "0.1 pip + עמלה $3.5 לכל leg (Razor)",
                "website": "https://pepperstone.com",
            },
            {
                "name": "Plus500",
                "type": "Market Maker (CFD)",
                "regulators": ["CySEC", "FCA", "ASIC", "ISA", "FSCA", "MAS"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "0.8 pip (ספרד דינמי)",
                "website": "https://www.plus500.com",
            },
        ],
    },

    "ארה\"ב (USA)": {
        "regulators": [
            {
                "name": "CFTC",
                "name_en": "Commodity Futures Trading Commission",
                "what": "הרגולטור הפדרלי האחראי על מסחר בעתידיים ו-FX קמעונאי בארה\"ב.",
                "lookup_url": "https://www.cftc.gov/",
            },
            {
                "name": "NFA",
                "name_en": "National Futures Association",
                "what": "ארגון הרישום הניהולי שמפקח ישירות על ברוקרי FX (RFEDs). כל ברוקר חייב להופיע ב-BasicNet.",
                "lookup_url": "https://www.nfa.futures.org/BasicNet/",
            },
        ],
        "compensation": "SIPC עד $500,000 (כולל $250,000 במזומן) – חל בעיקר על ברוקרי ני\"ע. רוב חשבונות ה-FX OTC אינם מכוסים. בדוק לפני הפקדה.",
        "tax": "רווחי FX קמעונאיים: ברירת מחדל לפי Section 988 (רגיל), אבל אפשר Section 1256 (60/40 לונג/שורט) – דורש בחירה ב-IRS. חובת דיווח שנתי.",
        "warnings": [
            "**מינוף מקסימלי**: 50:1 בזוגות Major, 20:1 ב-Minors. נמוך משמעותית ממה שמציעים ברוקרים זרים.",
            "**FIFO חובה**: סגירה לפי First-In-First-Out – מקשה על אסטרטגיות מסוימות.",
            "**Hedging אסור**: אסור להחזיק Long ו-Short באותו זוג בו-זמנית.",
            "**ברוקרים זרים**: אסור להם לקבל לקוחות אמריקאים בלי רישיון NFA. ברוקר זר ש'מקבל' אמריקאי – אסור חוקית."
        ],
        "brokers": [
            {
                "name": "FOREX.com (GAIN Capital / StoneX)",
                "type": "Market Maker / STP",
                "regulators": ["NFA", "CFTC"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "1.0-1.4 pip",
                "website": "https://www.forex.com",
            },
            {
                "name": "IG US",
                "type": "Market Maker",
                "regulators": ["NFA", "CFTC"],
                "min_deposit": "$0",
                "avg_eurusd_spread": "0.8-1.0 pip",
                "website": "https://www.ig.com/us",
            },
            {
                "name": "Interactive Brokers (IBKR)",
                "type": "ECN / Multi-asset",
                "regulators": ["SEC", "FINRA", "NFA", "CFTC"],
                "min_deposit": "אין",
                "avg_eurusd_spread": "0.1-0.4 pip + עמלה",
                "website": "https://www.interactivebrokers.com",
            },
            {
                "name": "OANDA",
                "type": "Market Maker / STP",
                "regulators": ["NFA", "CFTC"],
                "min_deposit": "$0",
                "avg_eurusd_spread": "1.1-1.4 pip",
                "website": "https://www.oanda.com",
            },
        ],
    },

    "בריטניה (UK)": {
        "regulators": [
            {
                "name": "FCA",
                "name_en": "Financial Conduct Authority",
                "what": "הרגולטור הפיננסי המרכזי בבריטניה. נחשב לאחד המחמירים בעולם. כל ברוקר חייב מספר רישוי (FRN) שמופיע ב-Register.",
                "lookup_url": "https://register.fca.org.uk/",
            },
        ],
        "compensation": "FSCS עד £85,000 לכל לקוח, בכפוף לתנאים. החזר מהמדינה במקרה של חדלות פירעון של ברוקר מפוקח FCA.",
        "tax": "Capital Gains Tax (CGT) ברווחי FX (אם נסחרים כהשקעה). Spread Bet – פטור ממס לתושבי בריטניה. CFD חייב במס.",
        "warnings": [
            "**מינוף מקסימלי**: 30:1 ב-Major, 20:1 ב-Minors (תקרת ESMA, נשמרה אחרי Brexit).",
            "**Negative Balance Protection**: חובה. הלקוח לא יכול לאבד יותר מההפקדה.",
            "**אזהרות סיכון**: ברוקר FCA חייב לציין % מהקמעונאים שמפסידים – ברוב המקרים 70%–85%."
        ],
        "brokers": [
            {
                "name": "CMC Markets",
                "type": "Market Maker",
                "regulators": ["FCA", "ASIC", "BaFin"],
                "min_deposit": "£0",
                "avg_eurusd_spread": "0.7 pip",
                "website": "https://www.cmcmarkets.com",
            },
            {
                "name": "IG Group",
                "type": "Market Maker",
                "regulators": ["FCA", "ASIC", "DFSA", "MAS"],
                "min_deposit": "£250",
                "avg_eurusd_spread": "0.6 pip",
                "website": "https://www.ig.com",
            },
            {
                "name": "Interactive Brokers UK",
                "type": "ECN / Multi-asset",
                "regulators": ["FCA"],
                "min_deposit": "אין",
                "avg_eurusd_spread": "0.1-0.4 pip + עמלה",
                "website": "https://www.interactivebrokers.co.uk",
            },
            {
                "name": "Pepperstone UK",
                "type": "ECN / STP",
                "regulators": ["FCA", "ASIC", "CySEC", "BaFin"],
                "min_deposit": "£0",
                "avg_eurusd_spread": "0.1 pip + עמלה (Razor)",
                "website": "https://pepperstone.com/en-gb",
            },
            {
                "name": "Tickmill UK",
                "type": "ECN",
                "regulators": ["FCA", "CySEC", "FSA Seychelles"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "0.1 pip + עמלה $4 round-turn",
                "website": "https://www.tickmill.com",
            },
        ],
    },

    "האיחוד האירופי (EU)": {
        "regulators": [
            {
                "name": "ESMA",
                "name_en": "European Securities and Markets Authority",
                "what": "מסגרת רגולציה אירופית מאוחדת. כל מדינה חברה אוכפת דרך הרגולטור המקומי שלה.",
                "lookup_url": "https://www.esma.europa.eu/",
            },
            {
                "name": "CySEC",
                "name_en": "Cyprus Securities and Exchange Commission",
                "what": "רגולטור קפריסאי, פופולרי בקרב ברוקרים שמשרתים את אירופה כולה (Passporting). פחות מחמיר מ-FCA אבל עדיין במסגרת ESMA.",
                "lookup_url": "https://www.cysec.gov.cy/en-GB/entities/",
            },
            {
                "name": "BaFin",
                "name_en": "Bundesanstalt für Finanzdienstleistungsaufsicht (גרמניה)",
                "what": "רגולטור גרמני מחמיר. ברוקרים שעובדים בגרמניה צריכים אישור.",
                "lookup_url": "https://www.bafin.de/",
            },
            {
                "name": "AMF",
                "name_en": "Autorité des marchés financiers (צרפת)",
                "what": "רגולטור צרפתי.",
                "lookup_url": "https://www.amf-france.org/",
            },
        ],
        "compensation": "ICF (Investor Compensation Fund) עד €20,000 בקפריסין, סכומים שונים במדינות אחרות באיחוד.",
        "tax": "משתנה לפי מדינה. ברוב המדינות – מס רווחי הון בשיעור 19%–30%.",
        "warnings": [
            "**מינוף מקסימלי (ESMA)**: 30:1 ב-Major, 20:1 ב-Minors, 5:1 במניות. חל על כל מדינות האיחוד.",
            "**Negative Balance Protection**: חובה.",
            "**אזהרות סיכון**: כל ברוקר ESMA חייב להציג את אחוז הקמעונאים שמפסידים.",
            "**Onboarding**: דרוש זיהוי KYC מלא (תעודה + הוכחת כתובת)."
        ],
        "brokers": [
            {
                "name": "Admiral Markets",
                "type": "Market Maker / STP",
                "regulators": ["CySEC", "FCA", "ASIC", "EFSA אסטוניה"],
                "min_deposit": "€100",
                "avg_eurusd_spread": "0.6-0.8 pip",
                "website": "https://admiralmarkets.com",
            },
            {
                "name": "FxPro",
                "type": "Market Maker / STP / ECN",
                "regulators": ["FCA", "CySEC", "FSCA", "SCB"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "0.4-0.6 pip",
                "website": "https://www.fxpro.com",
            },
            {
                "name": "IC Markets EU",
                "type": "ECN / STP",
                "regulators": ["CySEC", "ASIC", "FSA Seychelles"],
                "min_deposit": "$200",
                "avg_eurusd_spread": "0.1 pip + עמלה",
                "website": "https://www.icmarkets.com",
            },
            {
                "name": "Pepperstone EU",
                "type": "ECN / STP",
                "regulators": ["CySEC", "BaFin", "FCA", "ASIC"],
                "min_deposit": "$200",
                "avg_eurusd_spread": "0.1 pip + עמלה (Razor)",
                "website": "https://pepperstone.com/en",
            },
            {
                "name": "Saxo Bank",
                "type": "ECN / Multi-asset",
                "regulators": ["DFSA דנמרק", "FCA", "FINMA", "MAS"],
                "min_deposit": "$2,000 (Classic)",
                "avg_eurusd_spread": "0.4-0.6 pip",
                "website": "https://www.home.saxo",
            },
        ],
    },

    "אוסטרליה": {
        "regulators": [
            {
                "name": "ASIC",
                "name_en": "Australian Securities and Investments Commission",
                "what": "רגולטור אוסטרלי. נחשב לרציני ומחמיר. כל ברוקר חייב AFS Licence שניתן לאמת ב-Connect.",
                "lookup_url": "https://connectonline.asic.gov.au/",
            },
        ],
        "compensation": "אין תכנית פיצוי ממשלתית רשמית, אבל חובה על ברוקרים מורשים להחזיק כסף לקוחות בחשבון מופרד (Segregated). בעת חדלות פירעון – הכסף שייך ללקוח.",
        "tax": "Capital Gains Tax על רווחי FX, או הכנסה רגילה אם המסחר נחשב 'professional'. ATO מציעה הנחיות נפרדות.",
        "warnings": [
            "**מינוף מקסימלי**: ASIC מאז 2021 הגביל ל-30:1 ב-Major (זהה ל-ESMA).",
            "**רגולציה offshore**: חלק מהברוקרים האוסטרלים מציעים גם רישיון offshore (Seychelles, Vanuatu) לתושבי חוץ – לקוח שירשם דרך הישות הזרה מקבל מינוף גבוה יותר אבל גם הגנת רגולציה חלשה יותר.",
            "**Negative Balance Protection**: חובה ללקוחות קמעונאיים מאז 2021."
        ],
        "brokers": [
            {
                "name": "AxiTrader",
                "type": "STP",
                "regulators": ["ASIC", "FCA", "DFSA"],
                "min_deposit": "$0",
                "avg_eurusd_spread": "0.4-0.6 pip (Standard), 0.0 + עמלה (Pro)",
                "website": "https://www.axi.com",
            },
            {
                "name": "FP Markets",
                "type": "ECN / STP",
                "regulators": ["ASIC", "CySEC", "FSCA"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "0.1 pip + עמלה",
                "website": "https://www.fpmarkets.com",
            },
            {
                "name": "IC Markets",
                "type": "ECN / STP",
                "regulators": ["ASIC", "CySEC", "FSA Seychelles"],
                "min_deposit": "$200",
                "avg_eurusd_spread": "0.1 pip + עמלה $3.5 לכל leg",
                "website": "https://www.icmarkets.com",
            },
            {
                "name": "IG Australia",
                "type": "Market Maker",
                "regulators": ["ASIC", "FCA", "DFSA"],
                "min_deposit": "$0",
                "avg_eurusd_spread": "0.6 pip",
                "website": "https://www.ig.com/au",
            },
            {
                "name": "Pepperstone",
                "type": "ECN / STP",
                "regulators": ["ASIC", "FCA", "CySEC", "BaFin", "DFSA"],
                "min_deposit": "$200",
                "avg_eurusd_spread": "0.1 pip + עמלה",
                "website": "https://pepperstone.com",
            },
        ],
    },

    "קנדה": {
        "regulators": [
            {
                "name": "CIRO",
                "name_en": "Canadian Investment Regulatory Organization (לשעבר IIROC)",
                "what": "הרגולטור הקנדי המאוחד (איחוד של IIROC ו-MFDA ב-2023). כל ברוקר מורשה חייב להופיע ב-Find a Firm.",
                "lookup_url": "https://www.ciro.ca/office-investor/find-firm-or-individual",
            },
        ],
        "compensation": "CIPF (Canadian Investor Protection Fund) – עד $1,000,000 CAD לכל סוג חשבון. אחת התכניות הנדיבות בעולם.",
        "tax": "רווחי FX: אם נסחר בתדירות גבוהה – הכנסה רגילה. אם השקעה אקראית – Capital Gains (50% מהרווח חייב במס).",
        "warnings": [
            "**מינוף מקסימלי**: כ-50:1 ב-Major (תלוי בברוקר). בקנדה אין תקרת ESMA, אבל CIRO מצמצם.",
            "**מספר ברוקרים מצומצם**: רוב הברוקרים הזרים לא רשומים ב-CIRO ולא מקבלים קנדים.",
            "**Hedging מותר**, FIFO לא חובה (שונה מארה\"ב)."
        ],
        "brokers": [
            {
                "name": "CMC Markets Canada",
                "type": "Market Maker",
                "regulators": ["CIRO", "FCA"],
                "min_deposit": "$0",
                "avg_eurusd_spread": "0.7-0.9 pip",
                "website": "https://www.cmcmarkets.com/en-ca",
            },
            {
                "name": "Forex.com Canada",
                "type": "Market Maker / STP",
                "regulators": ["CIRO"],
                "min_deposit": "$100",
                "avg_eurusd_spread": "1.0-1.4 pip",
                "website": "https://www.forex.com/en-ca",
            },
            {
                "name": "Interactive Brokers Canada",
                "type": "ECN / Multi-asset",
                "regulators": ["CIRO"],
                "min_deposit": "אין",
                "avg_eurusd_spread": "0.1-0.4 pip + עמלה",
                "website": "https://www.interactivebrokers.ca",
            },
            {
                "name": "OANDA Canada",
                "type": "Market Maker / STP",
                "regulators": ["CIRO"],
                "min_deposit": "$0",
                "avg_eurusd_spread": "1.1-1.4 pip",
                "website": "https://www.oanda.com/ca-en/",
            },
            {
                "name": "Questrade FX",
                "type": "STP",
                "regulators": ["CIRO"],
                "min_deposit": "$250",
                "avg_eurusd_spread": "0.9-1.2 pip",
                "website": "https://www.questrade.com",
            },
        ],
    },

    "מדינה אחרת / Other": {
        "regulators": [
            {
                "name": "בדוק את הרגולטור הפיננסי של מדינתך",
                "name_en": "Find your local financial regulator",
                "what": "כל מדינה מפותחת מחזיקה רגולטור פיננסי. דוגמאות: סינגפור – MAS, יפן – JFSA, הונג קונג – SFC, דרום אפריקה – FSCA, שוויץ – FINMA, איחוד האמירויות – DFSA / SCA. חפשו את שם הרגולטור + 'forex broker register'.",
                "lookup_url": "https://www.google.com/search?q=financial+regulator+forex+broker+register",
            },
        ],
        "compensation": "משתנה. בודקים מה הכיסוי הביטוחי במדינה ספציפית.",
        "tax": "משתנה. בודקים עם רואה חשבון מקומי.",
        "warnings": [
            "**ללא רגולטור מקומי חזק** – נסחר עדיף דרך ברוקר עם רגולציה Tier-1 (FCA, ASIC, BaFin, SEC).",
            "**Offshore-only**: ברוקרים שהרגולציה היחידה שלהם היא ב-Vanuatu / Seychelles / Marshall Islands / Saint Vincent – סיכון גבוה.",
            "**אזהרת תרמית**: ברוקרים שמבקשים תשלום ב-Crypto בלבד, מבטיחים תשואות מובטחות, או מנסים להחזיר אותך אחרי שביקשת לסגור – חזק יותר מ-Red Flag."
        ],
        "brokers": [],
    },
}


country = st.selectbox(
    "🌍 בחרו את מדינת המגורים שלכם",
    list(COUNTRIES_DATA.keys()),
    index=0,
)

data = COUNTRIES_DATA[country]

st.divider()

st.markdown(f"### 🏛️ רגולטורים רלוונטיים – {country}")
for reg in data["regulators"]:
    with st.expander(f"**{reg['name']}** · {reg['name_en']}"):
        st.markdown(reg["what"])
        st.markdown(f"🔗 **בדיקת רישיון:** [{reg['lookup_url']}]({reg['lookup_url']})")

st.markdown("### 💰 כיסוי במקרה של חדלות פירעון")
st.info(data["compensation"])

st.markdown("### 📊 מיסוי")
st.info(data["tax"])

if data["warnings"]:
    st.markdown("### ⚠️ דברים שצריך לדעת")
    for w in data["warnings"]:
        st.warning(w)

if data["brokers"]:
    st.markdown(f"### 📋 ברוקרים מפוקחים שזמינים לתושבי {country}")
    st.caption(
        "רשימה אלפביתית של ברוקרים גדולים ומפוקחים שמקבלים תושבי מדינה זו לפי "
        "המידע הציבורי שלהם. **אין כאן המלצה**, ולא בדיקת איכות. נא לאמת באופן עצמאי "
        "את הרישיון, התנאים והמגבלות לפני כל החלטה."
    )

    for broker in data["brokers"]:
        with st.expander(f"**{broker['name']}** · {broker['type']}"):
            st.markdown(f"- **סוג ביצוע:** {broker['type']}")
            st.markdown(f"- **רגולטורים:** {', '.join(broker['regulators'])}")
            st.markdown(f"- **הפקדה מינימלית:** {broker['min_deposit']}")
            st.markdown(f"- **ספרד EUR/USD ממוצע:** {broker['avg_eurusd_spread']}")
            st.markdown(f"- **🔗 אתר:** [{broker['website']}]({broker['website']})")
            st.caption(
                "💡 בקרו באתר הרגולטור (למעלה) והקלידו את שם הברוקר כדי לוודא "
                "שהרישיון פעיל וכי הברוקר אכן רשום בישות הרגולטורית הצפויה."
            )
else:
    st.info(
        "לא הוספתי רשימת ברוקרים ספציפית לקטגוריה הזו, כי תנאי הקבלה משתנים מאוד "
        "ממדינה למדינה. השתמשו ברגולטור המקומי שלכם (למעלה) לחיפוש ברוקרים מורשים."
    )

st.divider()

st.markdown("### ✅ צ'קליסט אוניברסלי לבחירת ברוקר")
st.markdown(
    """
לפני שמפקידים שקל אחד, יש לוודא את כל הסעיפים הבאים:

1. **רישיון מאומת**. הקלידו את שם הברוקר ב-Register של הרגולטור (קישור למעלה).
   ודאו שיש מספר רישוי פעיל, ושהוא רשום למסחר ב-Forex/CFD ולא בקרנות בלבד.
2. **רגולציה Tier-1**. FCA, ASIC, BaFin, NFA/CFTC, FINMA, MAS – נחשבים שלב 1.
   CySEC, FSCA – שלב 2. רישיון יחיד מ-Vanuatu / SVG / Marshall Islands –
   דגל אדום משמעותי.
3. **כסף לקוחות מופרד (Segregated)**. הכסף שלכם חייב להיות מופרד מכספי
   הברוקר, בבנק מאושר. דרשו בכתב.
4. **תכנית פיצוי**. במקרה של חדלות פירעון, כמה תקבלו בחזרה?
   (FSCS £85k, ICF €20k, CIPF $1M CAD, SIPC $500k).
5. **תנאי הוצאת כסף**. עמלת משיכה, זמן ביצוע, הגבלות. בעיות במשיכה –
   הסימן הראשון לבעיות.
6. **תנאי מסחר ברורים**. ספרד טיפוסי, עמלות, swap, slippage. הכל בעמוד אחד
   נגיש – לא קבור באותיות קטנות.
7. **ניתוק אמיתי ב-Demo**. נסו את הפלטפורמה ב-Demo 2-3 שבועות. בדקו slippage,
   זמני תגובה, יציבות הקישור.
8. **תלונות פומביות**. בדקו ב-forexpeacearmy, trustpilot, רשתות חברתיות –
   האם יש דפוס של תלונות חוזרות (במיוחד על משיכות, requotes, slippage מוגזם).
9. **בעל הברוקר**. חברה ציבורית > חברה פרטית גדולה > חברה לא שקופה.
"""
)

st.markdown("### 🚩 דגלים אדומים שצריך לעצור עליהם")
st.error(
    "- **הבטחת תשואה / רווח מובטח** – אסור על פי כל רגולציה ראויה. הבטחה כזו = תרמית.\n"
    "- **בונוס הפקדה נדיב מדי** (50%-100%) – לרוב מותנה בנפח מסחר ענקי שמחייב את הלקוח להפסיד את ההפקדה.\n"
    "- **הפקדה רק ב-Crypto / מועברת ל-Wallet אישי של נציג** – תרמית.\n"
    "- **\"מומחה אישי\" שמתקשר לעזור לסחור** – ניסיון להגדיל את חשבונכם לטובת הברוקר.\n"
    "- **קושי במשיכה ראשונה** – אקסיומה: כל ברוקר אמיתי מוציא כסף בקלות. אם הראשונה תקועה – לא יהיו עוד.\n"
    "- **אתר חדש (פחות מ-6 חודשים), אין רגולציה ברורה, או רגולציה רק ב-Offshore**.\n"
    "- **משווק שטוען שהקורס לא צריך, רק תפקיד אצל מומחה** – המומחה משלם לברוקר על כל הפסד שלכם."
)

st.divider()

st.error(
    "⛔ **תזכורת:** הכלי הזה נועד אך ורק לחינוך. **אינני יועץ פיננסי ואינני "
    "ממליץ** על אף ברוקר ברשימה. כל החלטה לפתוח חשבון, להפקיד כסף או לסחור – "
    "באחריותכם הבלעדית. **אמתו כל פרט** עם הרגולטור הרשמי לפני שתפעלו, "
    "ומומלץ להתייעץ עם בעל רישיון מתאים."
)

page_end()
