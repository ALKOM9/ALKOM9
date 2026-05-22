# 📱 שלושת הצעדים האחרונים שלך – מהטלפון

הקוד מוכן ודחוף ל-GitHub. נשארו לך 3 פעולות, סך הכל ~10 דקות מהטלפון:

| # | מה | איפה | זמן |
|---|----|------|-----|
| 1 | קבלת מפתח FRED | fredaccount.stlouisfed.org | 2 דק׳ |
| 2 | פריסה ב-Streamlit Cloud | streamlit.io/cloud | 3 דק׳ |
| 3 | הגדרת Secrets | App → Settings → Secrets | 1 דק׳ |

---

## 1️⃣ מפתח FRED (חינמי, 2 דקות)

ראה הוראות מפורטות ב-[`FRED_API_QUICK.md`](./FRED_API_QUICK.md). תקציר:
- היכנס ל-https://fredaccount.stlouisfed.org/apikeys
- הירשם, אשר אימייל
- העתק את המפתח (32 תווים)

שמור את המפתח בהערות בטלפון – נשתמש בו בצעד 3.

---

## 2️⃣ פריסה ב-Streamlit Community Cloud

### א. הרשמה (אם עדיין לא)

פתח **https://streamlit.io/cloud** והתחבר עם חשבון ה-GitHub שלך. זה חינמי.

### ב. אפליקציה חדשה

לחץ **"New app"** או **"Create app"**.

מלא:
- **Repository:** `alkom9/alkom9` (או `sector-rotation-course` אם הקמת ריפו חדש)
- **Branch:** `claude/sector-rotation-course-ZUjlo`
- **Main file path:** `sector-rotation-course/app.py` *(שים לב לתיקייה!)*
- **App URL:** בחר משהו כמו `my-sector-course` (זה יהפוך לכתובת `my-sector-course.streamlit.app`)

לחץ **Deploy**. Streamlit יבנה את הסביבה תוך 1–2 דקות. *בכניסה הראשונה תראה מסך נעילה – זה תקין. נמשיך לצעד 3 שיפעיל אותו.*

---

## 3️⃣ Secrets (סיסמה + FRED key)

באפליקציה החדשה: **⚙ Settings → Secrets**.

הדבק בדיוק את זה, החלף את הערכים בשלך:

```toml
password = "Choose-A-Strong-Password-123!"
fred_api_key = "abcd1234567890..."
```

הערות:
- `password` – זו הסיסמה שתקליד כל פעם שאתה נכנס לקורס. בחר משהו חזק.
- `fred_api_key` – מהצעד 1.
- שמור את שתי השורות. גרשיים כפולים מסביב לערכים.

לחץ **Save**. Streamlit יעשה reboot אוטומטי תוך כמה שניות.

---

## ✅ סיום

פתח את כתובת האפליקציה (`https://your-name.streamlit.app`):
1. תראה מסך נעילה → הקלד את הסיסמה.
2. תראה מסך הסכמה דו-לשוני → סמן את התיבה → I Agree.
3. תראה את עמוד הבית עם 8 המודולים. ☰ למעלה משמאל פותח את התפריט.

### בדיקה מהירה
- מודול 4 (Macro Dashboard) – אמורים להופיע מספרים עם תאריך עדכני (תוך כמה שניות).
- אם רואים "⚠️ לא נמצא fred_api_key" – Settings → Secrets → ודא ששורת `fred_api_key` קיימת ולא חתוכה.

---

## 🛠️ תחזוקה

### עדכון סיסמה
Settings → Secrets → ערוך → Save → האפליקציה תעשה reboot. הסיסמה הישנה לא תעבוד יותר.

### "האפליקציה ישנה"
אחרי כמה ימי חוסר שימוש Streamlit Cloud משבית את האפליקציה. בכניסה תראה "Yes, get this app back up" – לחץ וחכה 30 שניות.

### עדכוני קוד
אם דוחפים קוד חדש לסניף → Streamlit מזהה תוך דקה ומעדכן אוטומטית.

### תקלה?
- צילום מסך של המסך השחור / השגיאה.
- Settings → "Manage app" → לוגים בתחתית.
- שלח לי (Claude) את הצילום + הלוג → אתקן.

---

## 🔒 פרטיות

- הריפו ב-GitHub שלך פרטי. אף אחד אחר לא יראה את הקוד.
- הסיסמה ב-Secrets, לא בקוד. אם תחליף סיסמה – הקוד לא משתנה.
- ה-FRED API key רק בקריאות מהשרת של Streamlit אל FRED. לא נשלח לדפדפן שלך.
- האפליקציה לא שומרת מי נכנס מתי. אין analytics. אין cookies חיצוניים.
