from utils.page import bootstrap, page_end
from utils.quiz import render_quiz
import streamlit as st

bootstrap("מודול 9 – מציאת עסקאות במהירות")

st.markdown("## 🚀 מודול 9 – מציאת עסקאות ארביטראז' במהירות מקסימלית")
st.caption("שתי גישות: ידנית (מה שאדם יכול לעשות בעיניים ובאצבעות) ואוטומטית (מה שמכונה יכולה לעשות).")
st.divider()

st.error(
    "⛔ **חשוב לפני שמתחילים:** המודול מסביר *כיצד* פועלים תהליכים אלו, "
    "**לא** כיצד לעשות מהם רווח. אינני יועץ פיננסי, ואין כאן המלצה לבנות מערכת "
    "ולהפעיל אותה בכסף אמיתי. **קמעונאי לא יכול לנצח HFT** – וזו תוצאה של חשבון, "
    "לא של דעה. הקוד והשיטות שתראו כאן מלמדים את המנגנון; השימוש בפועל באחריותכם הבלעדית."
)

st.divider()

# ============================================================
# PART 1: MANUAL
# ============================================================

st.markdown("## 🖱️ חלק א' – מציאה ידנית במהירות מקסימלית")
st.caption("הגדרה אופטימלית של עמדת עבודה אנושית, ה-workflow, והקירות המתמטיים של מה שאדם יכול לעשות.")

st.markdown("### 🎛️ העמדה האידיאלית")

st.markdown(
    """
כדי שתהיה לכם סיכוי כלשהו לזהות ולבצע פערית באופן ידני, נדרשת **הגדרה רצינית**:

**חומרה:**

- **שני מסכים לפחות**, רצוי 3. אחד לציטוטים בזמן אמת, אחד למחשבון, אחד להזמנות.
- **חיבור Ethernet קווי**, לא WiFi. מוריד 5-15 ms לטנסי.
- **ISP עם נתב מצויין** וללא packet loss. בדקו עם speedtest.net.
- **מקלדת מכנית** עם זמן תגובה מהיר (לא bluetooth).
- **מחשב חזק** (CPU מהיר, RAM 16GB+, SSD).

**תוכנה:**

- **פלטפורמת ברוקר אחת מהירה** (cTrader / MetaTrader / TWS) עם API להחלפת ציטוטים.
- **גיליון Excel או Python notebook** מוכן עם הנוסחה: `implied = pair1 × pair2`,
  שמתעדכן מיד עם הקלדה.
- **Hot Keys** מוגדרים בברוקר: F1 = Buy zoog 1, F2 = Sell zoog 1, F3 = Buy zoog 2 וכו'.
- **התראות ויזואליות**: צביעת תאי Excel באדום/ירוק כשהפערית עוברת סף.
"""
)

st.divider()

st.markdown("### 🔄 ה-Workflow הידני המהיר ביותר")

st.markdown(
    """
**שלב 0: הגדרה מראש (פעם אחת ביום)**

1. בחרו **משולש קבוע** – למשל EUR/USD × USD/JPY × EUR/JPY.
2. פתחו את 3 הזוגות ב-3 חלונות, צמודים זה לזה במסך.
3. ב-Excel: עמודה A = bid של כל זוג, עמודה B = ask, עמודה C = mid, עמודה D = implied,
   עמודה E = פערית ב-bp, עמודה F = צבע (אדום/ירוק).
4. כיוונו hot keys: 6 קליקים (3 legs × 2 כיוונים).

**שלב 1: צפייה רציפה (1-30 שניות)**

- העיניים נעות בין 3 הציטוטים. ה-Excel מחשב implied אוטומטית.
- מחפשים: פערית > 3 bp (אחרת לא שווה אחרי עלויות).

**שלב 2: זיהוי + החלטה (~500 ms)**

- ראיתם פערית של 4 bp. החלטה: באיזה כיוון? מסתכלים בעמודה ה-G של ה-Excel
  שאומרת "לחץ F1+F3+F5" (כיוון A) או "F2+F4+F6" (כיוון B).

**שלב 3: ביצוע (~600 ms)**

- 3 קליקי הקלידה, כל אחד שולח order.
- בנוסף: זמן תגובה של הברוקר + LP last-look = עוד 100-300 ms.

**סה"כ ידני: 1-2 שניות** מרגע זיהוי הפערית עד שכל 3 ה-legs בוצעו.
"""
)

st.divider()

st.markdown("### ⛔ הקיר המתמטי – למה הידני (כמעט) תמיד מפסיד")

st.markdown(
    """
שיטה ידנית הטובה ביותר: כ-1,500 ms מזיהוי לביצוע מלא.

| משתתף | זמן זיהוי+ביצוע | יחס |
|---|---|---|
| **אתם, ידני, מקסימום אופטימיזציה** | ~1,500 ms | 1× |
| HFT צמרת | ~5 μs | פי 300,000 מהיר |

**מה זה אומר בעולם האמיתי?**

כשפערית נפתחת ב-bid/ask, היא חיה בממוצע **10-100 μs** בזוגות Major.
לפני שאתם בכלל מסיימים *לזהות* אותה ב-Excel, ה-HFT כבר סגר אותה
**100,000 פעמים** ופתח שכבת הגנה למקרה שתחזור.

**אז למה לעשות את זה ידני בכלל?** רק מסיבה אחת: **לימוד**. כדי להבין באמת
איך נראית פערית, איך מרגישה החלטה, ולמה בלי אוטומציה זה לא משחק.
"""
)

st.warning(
    "⚠️ **אזהרה:** אם מצאתם פערית עקבית של מעל 5 bp שחיה לאורך זמן בזוג Major – "
    "כמעט בוודאות זו שגיאת ציטוט של הברוקר שלכם או feed מושהה. "
    "**אל תפעלו עליה**, כי כשתשלחו order הברוקר יבטל / יסליפ. בדקו מול feed שני (Google, "
    "frankfurter.app, ברוקר אחר) – אם רק אצלכם זה ככה, הברוקר זמני לא מסונכרן."
)

st.divider()

# ============================================================
# PART 2: AUTOMATIC
# ============================================================

st.markdown("## 🤖 חלק ב' – מציאה אוטומטית במהירות מקסימלית")
st.caption("ארכיטקטורה, latency budget, השוואת שפות, וקוד-דוגמה ב-Python.")

st.markdown("### 🏗️ הארכיטקטורה הנכונה")

st.markdown(
    """
מערכת אוטומטית מקצועית בנויה משלוש שכבות, **מופרדות בקפדנות**:

```
┌─────────────────────────────────────────────────┐
│  Market Data Layer                              │
│  WebSocket → Parser → In-memory book per pair   │
└─────────────────────────────────────────────────┘
                       ↓ event
┌─────────────────────────────────────────────────┐
│  Decision Layer                                 │
│  Compute implied → compare → decide direction   │
└─────────────────────────────────────────────────┘
                       ↓ trigger
┌─────────────────────────────────────────────────┐
│  Order Layer                                    │
│  Fire 3 orders in parallel (atomic ideally)     │
└─────────────────────────────────────────────────┘
```

**עקרונות:**

1. **Event-driven**, לא polling. WebSocket מודיע לכם כשמחיר מתעדכן.
2. **Single-threaded לכל leg** עם lock-free queues – לא race conditions.
3. **Pre-computed**: כל מה שאפשר לחשב מראש (Lookup tables), מחשבים מראש.
4. **No allocations on hot path**: לא מקצים זיכרון בזמן שמחירים זורמים.
5. **Atomic order firing**: שלוש ההזמנות יוצאות יחד, לא ברצף.
"""
)

st.divider()

st.markdown("### ⏱️ Latency Budget – כל מילישנייה נספרת")

st.markdown("הזמן המינימלי לאיטרציה אחת:")

st.table(
    [
        {"שלב": "קבלת ציטוט (WebSocket)",          "Python קמעונאי": "20-80 ms",  "C++ + Colocation": "1-5 μs"},
        {"שלב": "Parse JSON / FIX",                "Python קמעונאי": "1-5 ms",    "C++ + Colocation": "<1 μs"},
        {"שלב": "חישוב implied + השוואה",          "Python קמעונאי": "0.1-1 ms",  "C++ + Colocation": "<0.1 μs"},
        {"שלב": "החלטה",                            "Python קמעונאי": "<1 ms",     "C++ + Colocation": "<0.1 μs"},
        {"שלב": "שליחת 3 orders במקביל",            "Python קמעונאי": "30-150 ms", "C++ + Colocation": "5-20 μs"},
        {"שלב": "אישור LP (last-look)",             "Python קמעונאי": "10-100 ms", "C++ + Colocation": "10-50 μs"},
        {"שלב": "**סך הכל לאיטרציה**",              "Python קמעונאי": "**60-340 ms**", "C++ + Colocation": "**~20-80 μs**"},
    ]
)

st.markdown(
    """
**משמעות:** המערכת הקמעונאית הטובה ביותר ב-Python היא **פי 1,000–10,000 איטית** מ-HFT.
זה לא בעיה של "לכתוב טוב יותר". זה בעיה של פיזיקה, רשתות, ולא להיות באותו datacenter.
"""
)

st.divider()

st.markdown("### 🛠️ השוואת שפות תכנות")

st.table(
    [
        {"שפה / סטאק":             "Python + asyncio + websockets", "מהירות יחסית": "1×",        "קלות פיתוח": "★★★★★", "מתאים ל":   "לימוד, prototype"},
        {"שפה / סטאק":             "Node.js + uWebSockets",          "מהירות יחסית": "2×",        "קלות פיתוח": "★★★★☆", "מתאים ל":   "Prototype מהיר יותר"},
        {"שפה / סטאק":             "Go + Gorilla WebSocket",         "מהירות יחסית": "5×",        "קלות פיתוח": "★★★★☆", "מתאים ל":   "Production רציני"},
        {"שפה / סטאק":             "Java + Netty / vert.x",          "מהירות יחסית": "8×",        "קלות פיתוח": "★★★☆☆", "מתאים ל":   "ברוקרים גדולים"},
        {"שפה / סטאק":             "C++ + custom networking",        "מהירות יחסית": "50×",       "קלות פיתוח": "★★☆☆☆", "מתאים ל":   "HFT מקצועי"},
        {"שפה / סטאק":             "Rust + tokio",                   "מהירות יחסית": "45×",       "קלות פיתוח": "★★☆☆☆", "מתאים ל":   "HFT מודרני"},
        {"שפה / סטאק":             "FPGA + Verilog",                 "מהירות יחסית": "500×",      "קלות פיתוח": "★☆☆☆☆", "מתאים ל":   "HFT צמרת"},
    ]
)

st.divider()

st.markdown("### 🔌 APIs של ברוקרים – מה ניתן באמת לחבר")

st.markdown(
    """
**APIs מקצועיים (מהירים):**

- **FIX Protocol 4.2 / 4.4** – הסטנדרט המוסדי. דורש מנוי, גישה לרשת הברוקר.
  ברוקרים שתומכים: LMAX, Saxo, Pepperstone Razor, FXCM. עלות: $500-$5,000/חודש.
- **cTrader Open API** – Protobuf-based, מצוין למסחר אלגוריתמי. חינמי.
  ברוקרים: IC Markets, Pepperstone, FxPro.

**APIs קמעונאיים (איטיים יותר):**

- **OANDA v20 REST + Streaming** – יש Python SDK רשמי. ספרדים סבירים.
- **Interactive Brokers TWS / IB Gateway** – `ib_insync` ב-Python. דורש להריץ TWS פעיל.
- **MetaTrader 5 Python API** – חיבור ל-MT5 כקליינט. לטנסי גבוה (~50-200 ms).
- **AvaTrade API, FOREX.com API** – פחות פופולריים, תיעוד דליל.

**APIs ציבוריים (לא למסחר, רק לנתונים):**

- **frankfurter.app** – ECB Reference Rates (יומי, מה שמשמש את מודול 7).
- **OANDA Public API** – יש מצב חינמי לנתונים היסטוריים.
- **Alpha Vantage** – חינמי עם הגבלת קצב.
"""
)

st.divider()

st.markdown("### 💻 קוד-דוגמה: סקנר אסינכרוני ב-Python")

st.caption("דוגמה ללימוד בלבד. **אל תפעילו את זה בכסף אמיתי.** הקוד מדגים את המבנה, לא מערכת מוכנה.")

st.code(
    '''import asyncio
import json
import time
import websockets


# הזוגות במשולש שלנו
TRIANGLE = ("EUR/USD", "USD/JPY", "EUR/JPY")

# מחירים אחרונים, משתפים בין כל ה-coroutines
prices = {"EUR/USD": None, "USD/JPY": None, "EUR/JPY": None}

# סף פערית, ב-basis points, מעבר אליו נשקול ביצוע
THRESHOLD_BP = 3.0


async def listen_pair(pair: str, ws_url: str):
    """נחבר ל-WebSocket של הברוקר ונאזין לעדכוני bid/ask."""
    async with websockets.connect(ws_url) as ws:
        # subscribe לפי הפרוטוקול של הברוקר (מדומה כאן)
        await ws.send(json.dumps({"action": "subscribe", "symbol": pair}))
        async for raw in ws:
            msg = json.loads(raw)
            # נניח שה-message מגיע עם {bid, ask, ts}
            prices[pair] = {"bid": msg["bid"], "ask": msg["ask"], "ts": time.monotonic()}
            check_arbitrage()


def check_arbitrage():
    """כל פעם שמחיר מתעדכן, נבדוק האם נפתחה פערית."""
    if not all(prices.values()):
        return  # עדיין לא קיבלנו את כל 3 הזוגות

    eu = prices["EUR/USD"]; uj = prices["USD/JPY"]; ej = prices["EUR/JPY"]

    # implied EUR/JPY מ-2 הזוגות הראשונים
    implied = eu["ask"] * uj["ask"]   # ראשוני: ביצוע buy בשני ה-legs
    market_bid = ej["bid"]

    if market_bid > implied:
        edge_bp = (market_bid - implied) / implied * 10_000
        if edge_bp > THRESHOLD_BP:
            asyncio.create_task(fire_orders(edge_bp, direction="A"))

    # ובכיוון השני
    implied_b = eu["bid"] * uj["bid"]
    market_ask = ej["ask"]
    if implied_b > market_ask:
        edge_bp = (implied_b - market_ask) / implied_b * 10_000
        if edge_bp > THRESHOLD_BP:
            asyncio.create_task(fire_orders(edge_bp, direction="B"))


async def fire_orders(edge_bp: float, direction: str):
    """שלוש ההזמנות במקביל. במציאות צריך לטפל בכשלים."""
    print(f"[EDGE] {edge_bp:.2f} bp, direction={direction}")
    # async def send_order(...): ...
    # await asyncio.gather(send_order(leg1), send_order(leg2), send_order(leg3))


async def main():
    await asyncio.gather(
        listen_pair("EUR/USD", "wss://broker.example/eu"),
        listen_pair("USD/JPY", "wss://broker.example/uj"),
        listen_pair("EUR/JPY", "wss://broker.example/ej"),
    )


if __name__ == "__main__":
    asyncio.run(main())
''',
    language="python",
)

st.divider()

st.markdown("### 🔬 איפה הקוד הזה ישבר במציאות")

st.markdown(
    """
הקוד למעלה הוא **דמו לימודי**. בייצור הוא ישבר בכל אחד מהמקומות הבאים:

1. **חיבור יחיד שנופל** – Reconnect logic חסרה. במציאות צריך retry exponential backoff.
2. **חוסר סנכרון** – שלוש ה-WebSockets מקבלות מחירים בזמנים שונים. לפעמים PD/USD מ-09:00:00.123
   ו-EUR/JPY מ-09:00:00.156 – זה 33 ms של דעיכה.
3. **Order rejection** – הברוקר ידחה את ה-order השני אחרי שהראשון נכשל, ותישארו עם
   פוזיציה לא מאוזנת. צריך rollback logic.
4. **Last Look** – ה-LP יקבל את 3 ה-orders, יראה שאתם רוצים פערית, ידחה את אחד מהם.
5. **Throttling** – הברוקר יחסום אתכם אחרי 50 ניסיונות.
6. **Network latency variance** – לפעמים 30 ms, לפעמים 200 ms. ההחלטה שלכם נסמכת על הראשון.
7. **Python GIL** – ה-asyncio לא מקביל באמת. אם החישוב לוקח 10 ms יש איחור.

**מערכת ייצור צריכה לטפל בכל אחד מהאלה.** וגם אז – אתם פי 1,000+ איטיים מ-HFT.
"""
)

st.divider()

st.markdown("### 🎯 מה כן הגיוני לעשות עם מערכת אוטומטית")

st.markdown(
    """
אם בכל זאת בניתם אחת, היא יכולה להיות שימושית למטרות **אחרות**:

1. **לימוד שפת תכנות + שווקים** – הפרויקט מצוין לימודית.
2. **גילוי באגים אצל Market Maker** – לפעמים MM נותן ספרד גרוע יותר ממה שאמר. הסקנר
   יראה את זה.
3. **Backtest של אסטרטגיות אחרות** – ה-infrastructure של quotes streaming שימושי
   להרבה אלגוריתמים, לא רק לארביטראז'.
4. **Monitor ל-spreads** – לדעת מתי הברוקר שלכם מרחיב ספרדים מעבר לטיפוסי.
5. **Demo Trading** – אם מריצים בחשבון Demo, אתם לומדים בלי לאבד כסף.
"""
)

st.error(
    "⛔ **תזכורת אחרונה ועיקרית:** המטרה של המודול הזה הייתה ללמד **כיצד** "
    "מערכות כאלה עובדות, **לא** לעודד אתכם לבנות ולהפעיל. רוב מי שמנסה לסחור "
    "ארביטראז' פורקס אוטומטי עם הון קמעונאי – מפסיד את כל ההון. "
    "אינני יועץ פיננסי, ואין כאן המלצה."
)

st.divider()

render_quiz(
    "module9",
    [
        {
            "q": "מהו הזמן הסביר ביותר שיידרש לאדם מאומן לזהות ולבצע ארביטראז' ידני, גם בעמדה אופטימלית?",
            "options": [
                "10 ms",
                "100 ms",
                "1,500 ms",
                "10 שניות",
            ],
            "answer": 2,
            "explain": "סדר גודל של 1-2 שניות (1,500 ms). HFT מתחרה ב-5 μs – פי 300,000 מהיר. לא הוגן.",
        },
        {
            "q": "מהי הארכיטקטורה הנכונה למערכת ארביטראז' אוטומטית?",
            "options": [
                "REST polling כל שנייה",
                "WebSocket → Decision → Order, מופרדים",
                "סקריפט bash אחד שעושה הכל",
                "אקסל עם רענון אוטומטי",
            ],
            "answer": 1,
            "explain": "Event-driven עם שלוש שכבות מופרדות (Data, Decision, Order). REST polling איטי בסדרי גודל.",
        },
        {
            "q": "כמה פעמים HFT מהיר יותר ממערכת Python קמעונאית טיפוסית?",
            "options": [
                "פי 10",
                "פי 100",
                "פי 1,000-10,000",
                "באותה מהירות",
            ],
            "answer": 2,
            "explain": "Python קמעונאי: 60-340 ms לאיטרציה. HFT צמרת: ~20-80 μs. ההפרש בסדר גודל פי 1,000-10,000.",
        },
        {
            "q": "מהו ה-API המוסדי הסטנדרטי לחיבור ברוקר במהירות גבוהה?",
            "options": [
                "REST API ב-JSON",
                "FIX Protocol",
                "WebSocket עם JSON",
                "MetaTrader 4 API",
            ],
            "answer": 1,
            "explain": "FIX 4.2/4.4 הוא הפרוטוקול המוסדי הסטנדרטי. דורש מנוי וגישה לרשת הברוקר.",
        },
        {
            "q": "אם זיהיתם פערית עקבית של 5 bp שחיה דקות שלמות אצל ברוקר אחד אבל לא במקור עצמאי – מה זה כנראה?",
            "options": [
                "הזדמנות אמיתית לרווח גדול",
                "Feed מושהה או שגיאת ציטוט של הברוקר",
                "תקלה ב-WebSocket שלכם",
                "באג ב-Python",
            ],
            "answer": 1,
            "explain": "פערית עקבית גדולה שלא קיימת במקורות אחרים = הברוקר לא מסונכרן, או שזה quote מקולקל. כשתשלחו order – ידחה / יסליפ.",
        },
    ],
)

page_end()
