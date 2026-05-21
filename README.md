# 🔄 Sector Rotation Course

קורס אינטראקטיבי בעברית על Sector Rotation – אסטרטגיית רוטציית סקטורים לפי המחזור הכלכלי.
רץ ב-Streamlit Cloud, מוגן בסיסמה, אופטימלי למובייל, עם Macro Dashboard חי מ-FRED ו-backtest של 20 שנה.

> **התחל כאן:** [`MOBILE_FINAL_STEPS.md`](./MOBILE_FINAL_STEPS.md) – 3 פעולות, ~10 דקות, הכל מהטלפון.
> **מפתח FRED:** [`FRED_API_QUICK.md`](./FRED_API_QUICK.md) – הרשמה חינמית, 2 דקות.

## מבנה

```
app.py                  # נקודת כניסה: auth + consent + welcome
.streamlit/config.toml  # תצורת Streamlit (theme, mobile)
requirements.txt        # תלויות פייתון (streamlit, plotly, pandas, yfinance, requests)
pages/                  # 8 מודולים + מילון, multipage Streamlit
utils/
  auth.py        # password gate (st.secrets)
  consent.py     # bilingual disclaimer
  page.py        # bootstrap (page config + style + auth + consent)
  style.py       # RTL + mobile CSS
  quiz.py        # 5-question quiz component
  fred.py        # FRED API wrapper (cached)
  market.py      # yfinance + SPDR sector ETFs (cached)
  cycle.py       # business cycle phase detection
  rrg.py         # Relative Rotation Graph computation + Plotly figure
  backtest.py    # top-N momentum backtester + figures
```

## המודולים

1. **Business Cycle** – ארבעת השלבים, yield curve, PMI, LEI.
2. **מיפוי סקטורים** – 11 SPDR ETFs.
3. **הסיבוב הקלאסי** – איזה סקטור בכל שלב, חוקי Sam Stovall.
4. **Macro Dashboard חי** – 8 אינדיקטורים מ-FRED, סיווג אוטומטי.
5. **Relative Strength + RRG** – JdK RS-Ratio/Momentum, גרף אינטראקטיבי.
6. **יישום** – overweight, long-short, momentum.
7. **Backtest** – top-3 sectors momentum, 20 שנה.
8. **שילוב בתיק** – core/satellite, גודל הימור, רי-בלאנס.

## פריסה ב-Streamlit Cloud

1. Repo: `alkom9/alkom9` (או `sector-rotation-course` אם הקמת ריפו ייעודי).
2. Branch: `claude/sector-rotation-course-ZUjlo`.
3. Main file path: `app.py`.
4. Secrets:
   ```toml
   password = "YOUR_STRONG_PASSWORD"
   fred_api_key = "YOUR_FRED_KEY"
   ```

ראה [`MOBILE_FINAL_STEPS.md`](./MOBILE_FINAL_STEPS.md) להוראות צעד-צעד.

## אזהרה

הקורס למטרות חינוכיות בלבד. **אינו** ייעוץ פיננסי. Sector Rotation היא אסטרטגיה אקטיבית עם
תקופות drawdown משמעותיות; ביצועי עבר אינם מבטיחים ביצועי עתיד. ראה מסך ההסכמה המלא באפליקציה.
