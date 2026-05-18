# 🔺 Triangular Arbitrage Course

קורס אינטראקטיבי בעברית על Triangular Arbitrage, שרץ ב-Streamlit Cloud, מוגן בסיסמה, אופטימלי למובייל.

> **התחל כאן:** [`MOBILE_SETUP_GUIDE.md`](./MOBILE_SETUP_GUIDE.md) – הקמה מלאה מהטלפון ב-15-25 דקות.

## מבנה

```
app.py                  # נקודת כניסה: auth + consent + welcome
.streamlit/config.toml  # תצורת Streamlit (theme, mobile)
requirements.txt        # תלויות פייתון
pages/                  # 8 מודולים, multipage Streamlit
utils/                  # auth, consent, style (RTL+mobile), quiz
```

## פריסה ב-Streamlit Cloud

1. Repo: `triangular-arbitrage-course` (פרטי).
2. Branch: `claude/triangular-arbitrage-course-8EZO7` (או `main` אם מיזגת).
3. Main file path: `app.py`.
4. Secrets:
   ```toml
   password = "YOUR_STRONG_PASSWORD"
   ```

ראה [`MOBILE_SETUP_GUIDE.md`](./MOBILE_SETUP_GUIDE.md) להוראות צעד-צעד.

## אזהרה

הקורס למטרות חינוכיות בלבד. **אינו** ייעוץ פיננסי. מסחר ארביטראז' כרוך בסיכון אובדן הון משמעותי.
