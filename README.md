# 🔺 Triangular Arbitrage Course

> ## ⚠️ NOT FINANCIAL ADVICE / לא ייעוץ פיננסי
>
> **English.** The owner of this course is **not** a licensed financial,
> investment, or tax advisor. **Nothing in this repository is advice,
> a recommendation, or a solicitation to take any action with your money.**
> All content, calculators, scripts, and examples are **for educational
> and illustrative purposes only**. Trading FX, crypto, or arbitrage carries
> substantial risk of loss — possibly all of it. Past performance does not
> guarantee future results. Any reliance on this content is at your sole
> risk. Consult a licensed professional before taking any action.
>
> **עברית.** בעל הקורס **אינו** יועץ פיננסי, יועץ השקעות, או יועץ מס מורשה.
> **אין בקוד או בתוכן הזה ייעוץ, אין המלצה, ואין הצעה לבצע פעולה כלשהי בכספך.**
> כל התוכן, המחשבונים, הסקריפטים והדוגמאות הם **למטרות לימוד והמחשה בלבד**.
> מסחר בפורקס, קריפטו, או ארביטראז' כרוך בסיכון משמעותי לאובדן הון – אולי כולו.
> ביצועי עבר אינם מבטיחים ביצועי עתיד. כל הסתמכות על התוכן באחריותך הבלעדית.
> התייעץ עם בעל רישיון מתאים לפני כל פעולה.

קורס אינטראקטיבי בעברית על Triangular Arbitrage, שרץ ב-Streamlit Cloud, מוגן בסיסמה, אופטימלי למובייל.

## Structure / מבנה

```
app.py                  # נקודת כניסה: auth + consent + welcome
.streamlit/config.toml  # תצורת Streamlit (theme, mobile)
requirements.txt        # תלויות פייתון
pages/                  # 8 מודולים, multipage Streamlit
utils/                  # auth, consent, disclaimer, style, quiz
```

## Deploy / פריסה

1. Streamlit Cloud → New app.
2. Repository: `alkom9/alkom9`
3. Branch: `claude/triangular-arbitrage-course-8EZO7`
4. Main file path: `app.py`
5. Add to **Secrets**:
   ```toml
   password = "YOUR_STRONG_PASSWORD"
   ```

## License & Liability / רישיון ואחריות

The author of this repository disclaims all liability for losses, damages,
or other adverse outcomes resulting from use of this material. By using,
cloning, forking, or otherwise interacting with this repository, you accept
sole responsibility for any decision you make.

מחבר המאגר אינו אחראי לכל הפסד, נזק או תוצאה שלילית אחרת הנובעים משימוש
בחומר. שימוש, שכפול, פיצול (fork), או כל אינטראקציה אחרת עם המאגר מהווים
קבלת אחריות מלאה ובלעדית על כל החלטה שתתקבל על ידך.
