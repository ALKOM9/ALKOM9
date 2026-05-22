"""Glossary page - searchable bilingual reference for the course.

Students hit this whenever they bump into a term they don't know. Hebrew
explanations, but English headers are kept because that's what they'll see
in Bloomberg / TradingView / academic papers.
"""
from __future__ import annotations

import streamlit as st

from utils.page import bootstrap
from utils.style import page_header


bootstrap("מילון מונחים")
page_header("📖 מילון מונחים", "חיפוש מהיר וסיווג לפי קטגוריות – הסבר בעברית, מונח באנגלית")


TERMS: list[dict] = [
    # ===== מאקרו =====
    {
        "en": "Business Cycle",
        "he": "מחזור עסקים",
        "category": "מאקרו",
        "def_he": (
            "התנודה החוזרת של פעילות כלכלית בין שלבים של צמיחה והאטה. מחזור טיפוסי בארה\"ב נמשך "
            "כ-5–10 שנים וכולל ארבעה שלבים: התאוששות, אמצע, סוף, ומיתון. הבנת השלב הנוכחי היא הבסיס "
            "להחלטות סקטוריאליות."
        ),
        "see_also": ["Recovery / Early Expansion", "Mid Cycle", "Late Cycle", "Recession"],
    },
    {
        "en": "Recovery / Early Expansion",
        "he": "התאוששות",
        "category": "מאקרו",
        "def_he": (
            "השלב שאחרי מיתון – הצמיחה חוזרת, האבטלה מתחילה לרדת, והפד עדיין בריבית נמוכה או "
            "מתחיל להעלות לאט. היסטורית זה השלב הטוב ביותר לסקטורים מחזוריים כמו פיננסים, "
            "תעשייה, חומרי גלם ונדל\"ן."
        ),
        "see_also": ["Business Cycle", "Cyclical Sector"],
    },
    {
        "en": "Mid Cycle",
        "he": "אמצע מחזור",
        "category": "מאקרו",
        "def_he": (
            "השלב הארוך ביותר – צמיחה יציבה, אינפלציה מתונה, הפד בריבית ניטרלית. בדרך כלל סקטור "
            "הטכנולוגיה ושירותי תקשורת מובילים, ושוק המניות הרחב נוטה להניב תשואות חיוביות אך "
            "לא דרמטיות."
        ),
        "see_also": ["Business Cycle"],
    },
    {
        "en": "Late Cycle",
        "he": "סוף מחזור",
        "category": "מאקרו",
        "def_he": (
            "האינפלציה גואה, הפד מהדק, עקום התשואות משתטח או מתהפך, והצמיחה מאטה. סקטורי האנרגיה, "
            "חומרי גלם וסקטורים הגנתיים (Staples, Health Care) נוטים להוביל. שלב מועד לסיכון – "
            "המיתון לרוב 12–18 חודשים אחריו."
        ),
        "see_also": ["Yield Curve Inversion", "Defensive Sector"],
    },
    {
        "en": "Recession",
        "he": "מיתון",
        "category": "מאקרו",
        "def_he": (
            "ירידה רחבה ומתמשכת בפעילות הכלכלית – ירידה בתוצר, עלייה באבטלה, נפילה בייצור התעשייתי "
            "ובמכירות. ה-NBER הוא הגוף שמכריז רשמית על מיתון בארה\"ב, בדרך כלל בדיעבד. סקטורי הגנה "
            "(צריכה בסיסית, בריאות, שירותים) נוטים להחזיק יחסית טוב."
        ),
        "see_also": ["NBER", "Sahm Rule", "Defensive Sector"],
    },
    {
        "en": "NBER",
        "he": "NBER",
        "category": "מאקרו",
        "def_he": (
            "ה-National Bureau of Economic Research – מכון מחקר עצמאי שהוועדה שלו (Business Cycle "
            "Dating Committee) קובעת רשמית מתי התחיל ונגמר מיתון בארה\"ב. ההכרזה תמיד מאוחרת "
            "(לרוב 6–18 חודשים אחרי) ולכן לא משמשת לאיתות בזמן אמת."
        ),
        "see_also": ["Recession"],
    },
    {
        "en": "GDP",
        "he": "תוצר מקומי גולמי",
        "category": "מאקרו",
        "def_he": (
            "הערך הכולל של כל הסחורות והשירותים שיוצרו במשק בתקופה נתונה (לרוב רבעון). מתפרסם "
            "בארה\"ב על ידי ה-BEA, מתעדכן שלוש פעמים לכל רבעון. השינוי השנתי הריאלי (Real GDP YoY) "
            "הוא מדד הצמיחה המרכזי."
        ),
        "see_also": ["Inflation, CPI"],
    },
    {
        "en": "Inflation, CPI",
        "he": "אינפלציה",
        "category": "מאקרו",
        "def_he": (
            "קצב עליית המחירים במשק. ה-CPI (Consumer Price Index) מודד את שינוי המחירים של סל "
            "מוצרים ושירותים אופייני למשק בית. הפד מסתכל בעיקר על ה-PCE, אבל ה-CPI הוא המספר "
            "שמזיז את השוק כי הוא יוצא ראשון."
        ),
        "see_also": ["Core CPI / PCE", "Federal Funds Rate"],
    },
    {
        "en": "Core CPI / PCE",
        "he": "אינפלציית ליבה",
        "category": "מאקרו",
        "def_he": (
            "אינפלציה ללא מזון ואנרגיה – שני הסעיפים התנודתיים ביותר. הפד מתמקד ב-Core PCE כי הוא "
            "משקף לחצי מחירים בסיסיים ומתמשכים, ולא רעש זמני. יעד הפד הוא 2% שנתי."
        ),
        "see_also": ["Inflation, CPI", "FOMC"],
    },
    {
        "en": "Federal Funds Rate",
        "he": "ריבית הפד",
        "category": "מאקרו",
        "def_he": (
            "הריבית שבה בנקים מלווים אחד לשני יתרות בן-לילה. ה-FOMC קובע יעד (Target Range) שמשפיע "
            "על כל הריביות במשק. כשהריבית עולה – אשראי מתייקר, פעילות כלכלית מתמתנת, ושוק המניות "
            "נוטה להגיב שלילית בטווח הקצר."
        ),
        "see_also": ["FOMC", "Yield Curve"],
    },
    {
        "en": "FOMC",
        "he": "FOMC",
        "category": "מאקרו",
        "def_he": (
            "Federal Open Market Committee – הוועדה המוניטרית של הפדרל ריזרב. מתכנסת 8 פעמים בשנה "
            "ומקבלת החלטות ריבית ו-QE/QT. ההחלטה מתפרסמת ב-14:00 EST, אחריה מסיבת עיתונאים של "
            "היו\"ר ב-14:30 – שתיהן אירועי תנודתיות גבוהה."
        ),
        "see_also": ["Federal Funds Rate", "Quantitative Easing", "Quantitative Tightening"],
    },
    {
        "en": "Quantitative Easing",
        "he": "הרחבה כמותית (QE)",
        "category": "מאקרו",
        "def_he": (
            "כלי מוניטרי בלתי קונבנציונלי שבו הפד רוכש אג\"ח ממשלתי ו-MBS בכמויות גדולות כדי להזרים "
            "נזילות ולהוריד ריביות ארוכות. שימש 2008–2014 ושוב ב-2020. בדרך כלל תומך באפיקי סיכון "
            "(מניות, אג\"ח HY)."
        ),
        "see_also": ["Quantitative Tightening", "FOMC"],
    },
    {
        "en": "Quantitative Tightening",
        "he": "הידוק כמותי (QT)",
        "category": "מאקרו",
        "def_he": (
            "ההפך מ-QE – הפד מקטין את המאזן שלו על ידי אי-החלפת אג\"ח שמגיע לפדיון. מצמצם נזילות "
            "במערכת ולוחץ ריביות ארוכות מעלה. החל ב-2022 בקצב של עד 95 מיליארד דולר לחודש."
        ),
        "see_also": ["Quantitative Easing"],
    },
    {
        "en": "Yield Curve",
        "he": "עקום התשואות",
        "category": "מאקרו",
        "def_he": (
            "הגרף שמתאר תשואות אג\"ח ממשלתי לפי טווח לפדיון (3M, 2Y, 10Y, 30Y וכו'). במצב נורמלי "
            "התשואות הארוכות גבוהות מהקצרות. הצורה והשיפוע משקפים ציפיות לצמיחה, אינפלציה ומדיניות "
            "הפד."
        ),
        "see_also": ["Yield Curve Inversion", "Federal Funds Rate"],
    },
    {
        "en": "Yield Curve Inversion",
        "he": "היפוך עקום התשואות",
        "category": "מאקרו",
        "def_he": (
            "מצב שבו תשואת אג\"ח לטווח קצר (2Y או 3M) גבוהה מתשואת ה-10Y. מאז 1955 כל מיתון בארה\"ב "
            "הגיע אחרי היפוך, עם פיגור של 6–24 חודשים. אחד הסיגנלים המוקדמים והאמינים ביותר "
            "לסוף מחזור."
        ),
        "see_also": ["Yield Curve", "Late Cycle", "Recession"],
    },
    {
        "en": "High Yield Option-Adjusted Spread",
        "he": "מרווח HY OAS",
        "category": "מאקרו",
        "def_he": (
            "ההפרש בין תשואת אג\"ח קונצרני בדירוג ספקולטיבי (BB ומטה) לתשואת אג\"ח ממשלתי באותו "
            "טווח, מותאם לאופציות הגלומות. מרווח רחב (>6%) מסמן סטרס בשוק האשראי – ולרוב מתואם "
            "עם נפילות במניות. סדרה BAMLH0A0HYM2 ב-FRED."
        ),
        "see_also": ["Recession"],
    },

    # ===== אינדיקטורים =====
    {
        "en": "PMI / ISM",
        "he": "מדד מנהלי הרכש",
        "category": "אינדיקטורים",
        "def_he": (
            "מדד דיפוזיה חודשי שנע בין 0 ל-100, מבוסס על סקר מנהלי רכש. מעל 50 = התרחבות, מתחת = "
            "התכווצות. ה-ISM Manufacturing הוא הוותיק והפופולרי, ה-Services PMI חשוב לא פחות "
            "כיוון ש-70% מהמשק האמריקאי הוא שירותים."
        ),
        "see_also": ["LEI", "Industrial Production, INDPRO"],
    },
    {
        "en": "LEI",
        "he": "מדד מקדים (LEI)",
        "category": "אינדיקטורים",
        "def_he": (
            "Leading Economic Index של ה-Conference Board – מדד מורכב מ-10 רכיבים מקדימים (אישורי "
            "בנייה, תביעות אבטלה, מדד S&P 500, עקום תשואות ועוד). ירידה של 6 חודשים רצופים נחשבת "
            "היסטורית כסימן מובהק למיתון מתקרב."
        ),
        "see_also": ["PMI / ISM", "Recession"],
    },
    {
        "en": "Non-Farm Payrolls",
        "he": "דוח התעסוקה",
        "category": "אינדיקטורים",
        "def_he": (
            "NFP – השינוי החודשי במספר העובדים בארה\"ב (ללא חקלאות וצבא). מתפרסם ביום שישי הראשון "
            "של החודש ב-08:30 EST על ידי ה-BLS. אחד מהאירועים החשובים ביותר בלוח הכלכלי – משפיע "
            "על ריבית הפד, דולר ומניות."
        ),
        "see_also": ["Unemployment Rate", "Sahm Rule"],
    },
    {
        "en": "Initial Claims for Unemployment",
        "he": "תביעות אבטלה ראשוניות",
        "category": "אינדיקטורים",
        "def_he": (
            "ICSA – מספר האנשים שהגישו בקשה ראשונה לדמי אבטלה בשבוע החולף. מתפרסם בכל יום חמישי "
            "ב-08:30 EST. אינדיקטור תכוף ומקדים – עלייה מהירה (מעבר ל-300K-350K) מסמנת התכווצות "
            "בשוק העבודה."
        ),
        "see_also": ["Non-Farm Payrolls", "Unemployment Rate"],
    },
    {
        "en": "Unemployment Rate",
        "he": "שיעור אבטלה",
        "category": "אינדיקטורים",
        "def_he": (
            "אחוז המובטלים מתוך כוח העבודה האזרחי. מתפרסם יחד עם ה-NFP. למרות חשיבותו, זהו "
            "אינדיקטור מפגר (Lagging) – הוא מגיע לשפל בדיוק לפני שמתחיל מיתון, ולכן יש להשתמש "
            "בו לצד כללים דינמיים כמו Sahm Rule."
        ),
        "see_also": ["Sahm Rule", "Non-Farm Payrolls"],
    },
    {
        "en": "Sahm Rule",
        "he": "כלל Sahm",
        "category": "אינדיקטורים",
        "def_he": (
            "כלל פשוט שגיבשה הכלכלנית Claudia Sahm: אם הממוצע הנע ל-3 חודשים של שיעור האבטלה "
            "עלה ב-0.5 נקודות אחוז מעל השפל ב-12 חודשים האחרונים – המשק במיתון. צדק בכל מיתון "
            "מ-1960. הופעל ב-2024."
        ),
        "see_also": ["Unemployment Rate", "Recession"],
    },
    {
        "en": "Michigan Consumer Sentiment",
        "he": "מדד סנטימנט הצרכן מישיגן",
        "category": "אינדיקטורים",
        "def_he": (
            "סקר חודשי של אוניברסיטת מישיגן שבודק כיצד הצרכן האמריקאי תופס את מצבו הכלכלי ואת "
            "צפיותיו לעתיד. שפלים היסטוריים (<70) נקשרו למיתונים. צרכן חלש = פגיעה בסקטורי "
            "Consumer Discretionary."
        ),
        "see_also": ["Retail Sales, RSAFS"],
    },
    {
        "en": "Industrial Production, INDPRO",
        "he": "ייצור תעשייתי",
        "category": "אינדיקטורים",
        "def_he": (
            "מדד הפד שמודד את התפוקה הריאלית של תעשייה, כרייה ושירותי חשמל וגז. מתפרסם חודשי. "
            "צפיפות גבוהה עם המחזור העסקי – ירידה רצופה של מספר חודשים מסמנת חולשה תעשייתית "
            "ולעיתים קרובות מיתון."
        ),
        "see_also": ["PMI / ISM"],
    },
    {
        "en": "Building Permits",
        "he": "אישורי בנייה",
        "category": "אינדיקטורים",
        "def_he": (
            "מספר אישורי הבנייה למגורים שניתנו על ידי רשויות מקומיות בארה\"ב. אינדיקטור מקדים "
            "קלאסי – הוא חלק מה-LEI – כי החלטות בנייה מגיבות מהר לשינויי ריבית וצופות פעילות "
            "עתידית בענפי בנייה, ריהוט וצריכת מוצרי בני קיימא."
        ),
        "see_also": ["LEI"],
    },
    {
        "en": "Retail Sales, RSAFS",
        "he": "מכירות קמעונאיות",
        "category": "אינדיקטורים",
        "def_he": (
            "ערך המכירות החודשיות בעסקים קמעונאיים בארה\"ב. מדד מרכזי לבריאות הצרכן, שהוא כ-70% "
            "מהתוצר. נתון ה-Control Group (ללא מכוניות, דלק, חומרי בניין ומזון) משמש לחישוב ה-GDP."
        ),
        "see_also": ["Michigan Consumer Sentiment", "GDP"],
    },

    # ===== סקטורים =====
    {
        "en": "SPDR Select Sectors",
        "he": "SPDR Select Sectors",
        "category": "סקטורים",
        "def_he": (
            "סדרה של 11 ETFs של State Street שמחלקים את ה-S&P 500 לפי סקטורי GICS: XLK (טכנולוגיה), "
            "XLF (פיננסים), XLE (אנרגיה), XLV (בריאות), XLI (תעשייה), XLY, XLP, XLU, XLB, XLRE, XLC. "
            "סטנדרט בתעשייה לבדיקות סקטוריאליות וביישומי Sector Rotation."
        ),
        "see_also": ["GICS", "ETF"],
    },
    {
        "en": "GICS",
        "he": "סיווג GICS",
        "category": "סקטורים",
        "def_he": (
            "Global Industry Classification Standard – שיטת סיווג שפיתחו MSCI ו-S&P לחלוקת חברות "
            "ל-11 סקטורים, 24 קבוצות תעשייה, ומאות תת-תעשיות. זהו הסטנדרט שעליו בנויים רוב ה-ETFs "
            "הסקטוריאליים בעולם."
        ),
        "see_also": ["SPDR Select Sectors"],
    },
    {
        "en": "Defensive Sector",
        "he": "סקטור הגנתי",
        "category": "סקטורים",
        "def_he": (
            "סקטור שביקוש למוצריו לא תלוי במחזור העסקי – אנשים ממשיכים לקנות מזון, תרופות וחשמל "
            "גם במיתון. הסקטורים הקלאסיים: Consumer Staples (XLP), Health Care (XLV), Utilities "
            "(XLU). לרוב בעלי Beta < 1."
        ),
        "see_also": ["Cyclical Sector", "Beta"],
    },
    {
        "en": "Cyclical Sector",
        "he": "סקטור מחזורי",
        "category": "סקטורים",
        "def_he": (
            "סקטור שביצועיו מתואמים חזק עם מצב המשק – פיננסים (XLF), תעשייה (XLI), חומרי גלם (XLB), "
            "צריכה לא חיונית (XLY) ולעיתים אנרגיה (XLE). מובילים בהתאוששות ובאמצע מחזור, נחבטים "
            "במיתון. לרוב Beta > 1."
        ),
        "see_also": ["Defensive Sector", "Beta", "Business Cycle"],
    },
    {
        "en": "Growth vs Value",
        "he": "צמיחה מול ערך",
        "category": "סקטורים",
        "def_he": (
            "Growth = חברות עם צמיחת רווחים גבוהה וכפולות (P/E) גבוהות (טכנולוגיה, צריכה לא חיונית). "
            "Value = חברות במחיר נמוך יחסית לרווחים/הון (פיננסים, אנרגיה, תעשייה). הסיבוב ביניהם "
            "מושפע מאוד מריביות – ריבית עולה לרוב פוגעת ב-Growth ומועילה ל-Value."
        ),
        "see_also": ["Cyclical Sector"],
    },
    {
        "en": "Mega-cap, Large-cap, Small-cap",
        "he": "שווי שוק (Mega/Large/Small-cap)",
        "category": "סקטורים",
        "def_he": (
            "חלוקת חברות לפי שווי שוק: Mega-cap מעל 200 מיליארד דולר (Apple, Microsoft), Large-cap "
            "10–200 מיליארד, Mid-cap 2–10 מיליארד, Small-cap 300 מיליון–2 מיליארד. ביצועי "
            "Small-caps (Russell 2000) חזקים יותר במחזורי התאוששות."
        ),
        "see_also": ["Business Cycle"],
    },

    # ===== מסחר =====
    {
        "en": "ETF",
        "he": "תעודת סל (ETF)",
        "category": "מסחר",
        "def_he": (
            "Exchange-Traded Fund – קרן שנסחרת בבורסה כמו מניה ועוקבת אחרי מדד, סקטור או נכס. "
            "מאפשרת חשיפה מבוזרת בעלות נמוכה (Expense Ratio של 0.03%–0.5% לרוב). הכלי הבסיסי "
            "ליישום אסטרטגיית Sector Rotation."
        ),
        "see_also": ["SPDR Select Sectors", "Turnover"],
    },
    {
        "en": "Total Return",
        "he": "תשואה כוללת",
        "category": "מסחר",
        "def_he": (
            "תשואה שמשלבת עליית מחיר ודיבידנדים מושקעים חזרה (Reinvested). זה המספר הרלוונטי "
            "להשוואת ביצועים – מדד Price Return בלבד מתעלם מתזרים שיכול להגיע ל-2%–4% בשנה "
            "בסקטורים כמו Utilities ו-REITs."
        ),
        "see_also": ["ETF"],
    },
    {
        "en": "Drawdown",
        "he": "Drawdown",
        "category": "מסחר",
        "def_he": (
            "הירידה מהשיא האחרון של תיק או נכס, באחוזים. נמדד בכל נקודת זמן ביחס לשיא הקודם. "
            "מדד הסיכון האינטואיטיבי ביותר – מה הפסדתי בנקודה הגרועה ביותר?"
        ),
        "see_also": ["Maximum Drawdown", "Volatility"],
    },
    {
        "en": "Maximum Drawdown",
        "he": "Drawdown מקסימלי",
        "category": "מסחר",
        "def_he": (
            "ה-Drawdown העמוק ביותר בתקופת הבדיקה. נחשב למדד סיכון מרכזי באסטרטגיות סיסטמטיות. "
            "S&P 500 לדוגמה ירד 56% ב-2007–2009 ו-34% במרץ 2020. תיק עם MDD של 60% דורש +150% "
            "כדי לחזור לשיא."
        ),
        "see_also": ["Drawdown"],
    },
    {
        "en": "Volatility",
        "he": "תנודתיות",
        "category": "מסחר",
        "def_he": (
            "סטיית התקן של תשואות, לרוב ב-annualized terms (כפול שורש 252 לתשואות יומיות). מודד "
            "כמה התשואה מתפזרת סביב הממוצע. שוק המניות האמריקאי בעל Volatility היסטורי של "
            "15%–20% שנתי."
        ),
        "see_also": ["Beta", "Sharpe Ratio"],
    },
    {
        "en": "Beta",
        "he": "Beta",
        "category": "מסחר",
        "def_he": (
            "מקדם רגישות של נכס לתנודות השוק (לרוב S&P 500). Beta = 1.2 אומר שהנכס נע 20% יותר "
            "מהשוק בממוצע. סקטורי טכנולוגיה ופיננסים בעלי Beta > 1, סקטורי הגנה בעלי Beta < 1."
        ),
        "see_also": ["Volatility", "Cyclical Sector"],
    },
    {
        "en": "Sharpe Ratio",
        "he": "יחס Sharpe",
        "category": "מסחר",
        "def_he": (
            "תשואה עודפת (מעל ריבית חסרת סיכון) חלקי סטיית תקן. מודד תשואה ליחידת סיכון. Sharpe "
            "של 1 נחשב טוב, 2 מעולה, מעל 3 חשוד. החיסרון: מעניש תנודתיות גם בכיוון החיובי."
        ),
        "see_also": ["Sortino Ratio", "Volatility"],
    },
    {
        "en": "Sortino Ratio",
        "he": "יחס Sortino",
        "category": "מסחר",
        "def_he": (
            "כמו Sharpe אבל מחלק רק בסטיית תקן של תשואות שליליות (Downside Deviation). הגיוני יותר "
            "כי משקיעים לא חוששים מתנודתיות חיובית. בדרך כלל גבוה מ-Sharpe באותו תיק."
        ),
        "see_also": ["Sharpe Ratio"],
    },
    {
        "en": "Tracking Error",
        "he": "Tracking Error",
        "category": "מסחר",
        "def_he": (
            "סטיית תקן של ההפרש בין תשואות התיק לבין תשואות הבנצ'מארק. נמוך אצל ETFs פסיביים "
            "(<0.1%) וגבוה אצל אסטרטגיות אקטיביות (3%–8%). ככל שגבוה יותר – הפעילות יותר "
            "אקטיבית."
        ),
        "see_also": ["ETF"],
    },
    {
        "en": "Turnover",
        "he": "תחלופה (Turnover)",
        "category": "מסחר",
        "def_he": (
            "אחוז התיק שמתחלף בשנה. תיק עם Turnover של 200% מחליף את עצמו פעמיים בשנה בממוצע. "
            "Turnover גבוה משמעו עמלות גבוהות יותר, Slippage גבוה יותר, ולרוב חבות מס גבוהה "
            "יותר."
        ),
        "see_also": ["Slippage", "Rebalancing"],
    },
    {
        "en": "Slippage",
        "he": "החלקה (Slippage)",
        "category": "מסחר",
        "def_he": (
            "ההפרש בין המחיר שתכננת לבצע בו עסקה לבין המחיר שבו היא בוצעה בפועל. נובע מתנועת "
            "השוק, מ-Bid-Ask Spread ומ-Market Impact בעסקאות גדולות. שווה לבדוק אותו בכל בדיקת "
            "Backtest."
        ),
        "see_also": ["Turnover", "Backtest"],
    },
    {
        "en": "Rebalancing",
        "he": "איזון מחדש",
        "category": "מסחר",
        "def_he": (
            "הפעולה של החזרת תיק להקצאה היעד שלו אחרי שמחירי השוק שינו אותו. תדירויות נפוצות: "
            "חודשי, רבעוני, או לפי סטייה (לדוגמה כשמשקל סקטור חורג ביותר מ-3% מהיעד). תדירות "
            "גבוהה = עמלות וטעויות יותר."
        ),
        "see_also": ["Turnover"],
    },
    {
        "en": "Long-Short",
        "he": "לונג-שורט",
        "category": "מסחר",
        "def_he": (
            "אסטרטגיה שקונה (Long) נכסים שצפויים לעלות ומוכרת בחסר (Short) נכסים שצפויים לרדת. "
            "בסקטור רוטיישן זה מתבטא ב-Long על סקטור מוביל ו-Short על סקטור מפגר. נטרלי לשוק "
            "ברמה התיאורטית – ה-Beta הכולל קרוב לאפס."
        ),
        "see_also": ["Beta", "Relative Strength"],
    },
    {
        "en": "Momentum",
        "he": "מומנטום",
        "category": "מסחר",
        "def_he": (
            "התופעה (והאסטרטגיה) שבה נכסים שעלו לאחרונה נוטים להמשיך לעלות בטווח של 1–12 חודשים. "
            "מהאנומליות החזקות והעקביות ביותר בשווקים פיננסיים מאז המחקר של Jegadeesh & Titman "
            "ב-1993. בסיס לרוב מודלי Sector Rotation."
        ),
        "see_also": ["Relative Strength", "Mean Reversion"],
    },
    {
        "en": "Mean Reversion",
        "he": "חזרה לממוצע",
        "category": "מסחר",
        "def_he": (
            "ההפך ממומנטום – ההנחה שמחירים שחרגו רחוק מהממוצע יחזרו אליו. עובד טוב יותר בטווחים "
            "קצרים מאוד (ימים-שבועות) ובמדדים רחבים. בטווחי Sector Rotation (חודשים) Momentum "
            "לרוב חזק יותר."
        ),
        "see_also": ["Momentum", "Z-score"],
    },
    {
        "en": "Relative Strength",
        "he": "כוח יחסי",
        "category": "מסחר",
        "def_he": (
            "ביצוע של נכס יחסית לבנצ'מארק (לדוגמה XLK/SPY). אם היחס עולה – הנכס חזק יחסית, אם "
            "יורד – חלש יחסית. הבסיס לטכניקת RRG ולכל ניתוח Rotation. שונה מאוד מ-RSI "
            "(Relative Strength Index)."
        ),
        "see_also": ["RRG", "JdK RS-Ratio / RS-Momentum"],
    },
    {
        "en": "RRG",
        "he": "RRG",
        "category": "מסחר",
        "def_he": (
            "Relative Rotation Graph – כלי ויזואלי שפיתח Julius de Kempenaer, מציג כוח יחסי "
            "ומומנטום של נכסים בו זמנית. כל נכס מתואר כנקודה שנעה ברבעים: מוביל (Leading), "
            "מחליש (Weakening), מפגר (Lagging), משתפר (Improving)."
        ),
        "see_also": ["Relative Strength", "JdK RS-Ratio / RS-Momentum"],
    },
    {
        "en": "JdK RS-Ratio / RS-Momentum",
        "he": "JdK RS-Ratio / RS-Momentum",
        "category": "מסחר",
        "def_he": (
            "שני המדדים שמרכיבים RRG. RS-Ratio הוא כוח יחסי מנורמל (סביב 100) – ציר X. RS-Momentum "
            "הוא קצב השינוי של ה-RS-Ratio – ציר Y. נכס ברבע ימני-עליון = מוביל, שמאלי-עליון = "
            "משתפר, וכו'."
        ),
        "see_also": ["RRG", "Relative Strength"],
    },

    # ===== סטטיסטיקה =====
    {
        "en": "Z-score",
        "he": "Z-score",
        "category": "סטטיסטיקה",
        "def_he": (
            "כמה סטיות תקן ערך מסוים רחוק מהממוצע: Z = (x - μ) / σ. שימושי לנרמול אינדיקטורים "
            "בסדרי גודל שונים ולזיהוי ערכי קיצון. Z > 2 או Z < -2 נחשבים חריגים."
        ),
        "see_also": ["Rolling Window", "Mean Reversion"],
    },
    {
        "en": "Rolling Window",
        "he": "חלון נע",
        "category": "סטטיסטיקה",
        "def_he": (
            "חישוב סטטיסטיקה (ממוצע, סטיית תקן, מתאם וכו') על קבוצה של תצפיות עוקבות שנעה לאורך "
            "ציר הזמן. לדוגמה ממוצע נע ל-50 ימים מחשב את הממוצע של 50 ימי המסחר האחרונים בכל "
            "נקודה."
        ),
        "see_also": ["EMA", "Z-score"],
    },
    {
        "en": "EMA",
        "he": "ממוצע נע מעריכי (EMA)",
        "category": "סטטיסטיקה",
        "def_he": (
            "Exponential Moving Average – ממוצע נע שנותן משקל גבוה יותר לתצפיות עדכניות. מגיב "
            "מהר יותר משינויים מ-SMA פשוט. נפוץ ב-MACD, ב-trend filters וב-cross-overs של "
            "EMA(50) ו-EMA(200)."
        ),
        "see_also": ["Rolling Window"],
    },
    {
        "en": "Year-over-Year",
        "he": "שינוי שנתי (YoY)",
        "category": "סטטיסטיקה",
        "def_he": (
            "ההפרש באחוזים בין הערך הנוכחי לערך באותה תקופה לפני 12 חודשים. שימושי לנטרול "
            "עונתיות – CPI YoY הוא הציטוט הסטנדרטי לאינפלציה כי הוא משווה אוקטובר השנה לאוקטובר "
            "שעבר."
        ),
        "see_also": ["Month-over-Month", "Rate of Change"],
    },
    {
        "en": "Month-over-Month",
        "he": "שינוי חודשי (MoM)",
        "category": "סטטיסטיקה",
        "def_he": (
            "ההפרש באחוזים בין החודש הנוכחי לחודש הקודם. מגיב מהר יותר מ-YoY אבל רגיש לעונתיות, "
            "ולכן נתוני MoM של אינפלציה ומכירות מפורסמים תמיד גם בגרסה Seasonally Adjusted (SA)."
        ),
        "see_also": ["Year-over-Year", "Rate of Change"],
    },
    {
        "en": "Rate of Change",
        "he": "קצב שינוי (ROC)",
        "category": "סטטיסטיקה",
        "def_he": (
            "השינוי באחוזים על פני N תקופות: ROC = (P_t / P_{t-N}) - 1. שימושי כמדידת מומנטום "
            "(לדוגמה ROC של 12 חודשים) ולזיהוי ערכי קיצון. נפוץ בבחירת סקטורים על בסיס "
            "Momentum."
        ),
        "see_also": ["Momentum", "Year-over-Year"],
    },

    # ===== כללי =====
    {
        "en": "FRED",
        "he": "FRED",
        "category": "כללי",
        "def_he": (
            "Federal Reserve Economic Data – מאגר מידע פתוח של הפד של St. Louis שמרכז יותר "
            "מ-800,000 סדרות נתונים מאקרו-כלכליות. API חינמי עם רישום מהיר, וזהו המקור העיקרי "
            "של כל הנתונים הכלכליים בקורס."
        ),
        "see_also": ["API Key", "Bloomberg / Refinitiv / TradingView"],
    },
    {
        "en": "Bloomberg / Refinitiv / TradingView",
        "he": "פלטפורמות נתונים",
        "category": "כללי",
        "def_he": (
            "Bloomberg ו-Refinitiv (לשעבר Reuters) הם הטרמינלים הוותיקים והיקרים (כ-$24K לשנה) של "
            "תעשיית הפיננסים. TradingView היא הפלטפורמה המודרנית, נגישה (חינם עד $60 לחודש), "
            "מתאימה למשקיע פרטי. כולם מציגים מונחים באנגלית – לכן המילון דו-לשוני."
        ),
        "see_also": ["FRED"],
    },
    {
        "en": "API Key",
        "he": "מפתח API",
        "category": "כללי",
        "def_he": (
            "מחרוזת מזהה שמאפשרת גישה תכנותית לשירות (FRED, AlphaVantage, Polygon וכו'). יש "
            "לשמור אותה בסוד – אסור להעלות ל-GitHub. ב-Streamlit Cloud מנוהלת דרך Secrets ולא "
            "מופיעה בקוד עצמו."
        ),
        "see_also": ["FRED"],
    },
    {
        "en": "Backtest",
        "he": "Backtest",
        "category": "כללי",
        "def_he": (
            "סימולציה של אסטרטגיה על נתונים היסטוריים כדי להעריך את ביצועיה ההיפותטיים. כלי "
            "חיוני אך מסוכן – קל מאוד לרמות את עצמך עם Look-ahead bias, Overfitting ו-Survivorship "
            "bias. תמיד יש לבדוק על תקופה Out-of-sample."
        ),
        "see_also": ["Look-ahead bias", "Survivorship bias", "Out-of-sample / In-sample", "Walk-forward"],
    },
    {
        "en": "Look-ahead bias",
        "he": "הטיית מבט קדימה",
        "category": "כללי",
        "def_he": (
            "טעות נפוצה בבדיקה היסטורית שבה האסטרטגיה משתמשת בנתון שלא היה זמין בזמן אמת. "
            "לדוגמה: שימוש בנתון GDP לרבעון הראשון בתחילת אפריל, למרות שהפרסום הראשון היה רק "
            "בסוף אפריל. גורם לתוצאות מנופחות באופן לא ריאלי."
        ),
        "see_also": ["Backtest", "Survivorship bias"],
    },
    {
        "en": "Survivorship bias",
        "he": "הטיית הישרדות",
        "category": "כללי",
        "def_he": (
            "טעות בבדיקה היסטורית שבה משתמשים רק בחברות/קרנות ששרדו עד היום, ומתעלמים מאלה שפשטו "
            "רגל או נמחקו. מנפח את התשואות ההיסטוריות, כי הכישלונות נמחקו. במאגר טוב יש Point-in-"
            "time data."
        ),
        "see_also": ["Backtest", "Look-ahead bias"],
    },
    {
        "en": "Out-of-sample / In-sample",
        "he": "In-sample / Out-of-sample",
        "category": "כללי",
        "def_he": (
            "In-sample = התקופה שבה כיוונת את האסטרטגיה. Out-of-sample = תקופה נפרדת שעליה בודקים "
            "את הביצועים מבלי שהשפיעה על הכיוונון. רק תוצאות Out-of-sample הן אינדיקציה מהימנה "
            "ליכולות אמיתיות."
        ),
        "see_also": ["Backtest", "Walk-forward"],
    },
    {
        "en": "Walk-forward",
        "he": "Walk-forward",
        "category": "כללי",
        "def_he": (
            "טכניקת בדיקה שבה מכיילים מודל על חלון היסטורי (לדוגמה 5 שנים), בודקים על השנה הבאה, "
            "מזיזים את החלון קדימה, ושוב. מדמה תהליך אמיתי של בנייה מחדש של מודל לאורך זמן ומקטין "
            "Overfitting."
        ),
        "see_also": ["Backtest", "Out-of-sample / In-sample"],
    },
    {
        "en": "Regime Change",
        "he": "שינוי משטר",
        "category": "כללי",
        "def_he": (
            "מעבר של השוק או המשק ממצב סטטיסטי אחד למצב אחר – לדוגמה משוק שורי לדובי, מסביבה "
            "אינפלציונית לדפלציונית, או ממדיניות מוניטרית מרחיבה למצמצמת. מודלים שעבדו במשטר אחד "
            "עלולים להיכשל לחלוטין במשטר אחר."
        ),
        "see_also": ["Business Cycle"],
    },
    {
        "en": "Core-Satellite",
        "he": "ליבה + לוויינים",
        "category": "כללי",
        "def_he": (
            "מבנה תיק שבו רוב הכסף (70%–90%) יושב באחזקת ליבה פסיבית רחבה (לדוגמה SPY או VT), "
            "והיתרה מוקצית לאסטרטגיות אקטיביות (Satellites) כמו Sector Rotation. גישה זהירה "
            "ליישום אסטרטגיות אקטיביות בלי לסכן את כל התיק."
        ),
        "see_also": ["ETF"],
    },
    {
        "en": "Wash sale",
        "he": "מכירה תאומה",
        "category": "כללי",
        "def_he": (
            "כלל מס אמריקאי שמבטל את ההכרה בהפסד אם רכשת מחדש את אותו נכס (או נכס דומה מהותית) "
            "תוך 30 יום לפני או אחרי המכירה בהפסד. רלוונטי במיוחד באסטרטגיות עם Turnover גבוה "
            "כמו Sector Rotation."
        ),
        "see_also": ["Turnover"],
    },
]


ALL_CATEGORIES = ["מאקרו", "אינדיקטורים", "סקטורים", "מסחר", "סטטיסטיקה", "כללי"]


# --- חיפוש וסינון ---
col_a, col_b = st.columns([2, 3])
with col_a:
    q = st.text_input("חפש מונח", "", placeholder="למשל: עקום, Beta, NFP")
with col_b:
    cats = st.multiselect("קטגוריות", ALL_CATEGORIES, default=ALL_CATEGORIES)

q_norm = q.strip().lower()


def _matches(term: dict) -> bool:
    if term["category"] not in cats:
        return False
    if not q_norm:
        return True
    return q_norm in term["en"].lower() or q_norm in term["he"].lower()


filtered = [t for t in TERMS if _matches(t)]
filtered.sort(key=lambda t: t["he"])

st.caption(f"מציג {len(filtered)} מתוך {len(TERMS)} מונחים")
st.divider()

if not filtered:
    st.info("לא נמצאו תוצאות. נסה לנקות את החיפוש או להרחיב את הקטגוריות.")
else:
    for term in filtered:
        with st.container(border=True):
            st.markdown(f"**{term['he']}** ({term['en']})")
            st.caption(f"קטגוריה: {term['category']}")
            st.write(term["def_he"])
            see_also = term.get("see_also") or []
            if see_also:
                bolded = " · ".join(f"**{s}**" for s in see_also)
                st.markdown(f"ראה גם: {bolded}")

st.divider()
st.caption(
    "המילון נועד ללמידה בלבד ולא מהווה ייעוץ השקעות. כל המונחים הם תרגום עברי-עברי "
    "של מונחי תעשייה באנגלית, ובסיס לקריאה עצמאית במקורות מקצועיים."
)
