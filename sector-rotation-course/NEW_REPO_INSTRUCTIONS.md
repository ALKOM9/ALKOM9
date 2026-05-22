# 🆕 איך ליצור ריפו נפרד "sector-rotation-course"

הקוד כרגע יושב בריפו `alkom9/alkom9` בתוך תיקייה `sector-rotation-course/`.  
אם אתה רוצה ריפו ייעודי **`sector-rotation-course`** כקורס נפרד לחלוטין מהארביטראז׳ – הנה צעד-צעד מהטלפון. ~5 דקות.

> **לא חייב.** Streamlit Cloud עובד מעולה גם מהריפו הנוכחי (`alkom9/alkom9`, main file path: `sector-rotation-course/app.py`). אם אתה רוצה לחסוך זמן, דלג ופעל לפי `MOBILE_FINAL_STEPS.md` כפי שהוא.

---

## 1️⃣ צור את הריפו ב-GitHub (טלפון)

1. פתח **https://github.com/new** בדפדפן הטלפון.
2. **Repository name:** `sector-rotation-course`
3. **Description:** `Sector Rotation course – Hebrew, Streamlit, mobile-first`
4. סמן **Private** ✅ (חשוב!)
5. **אל תסמן** "Add a README" ו-"Add .gitignore" ו-license. נשאיר ריק.
6. לחץ **Create repository**.

תקבל מסך עם הוראות. **אל תעקוב אחריהן** – יש לנו דרך פשוטה יותר למובייל בצעד הבא.

---

## 2️⃣ העבר את הקוד דרך GitHub Web Editor

GitHub מאפשר להעלות קבצים ישירות מהדפדפן בטלפון. אנחנו ננצל את זה.

### א. הורד את הקוד שלך מהריפו הנוכחי

1. פתח **https://github.com/alkom9/alkom9/tree/claude/sector-rotation-course-ZUjlo/sector-rotation-course**
2. לחץ על הכפתור הירוק **Code** → **Download ZIP**.
3. הקובץ יישמר בהורדות של הטלפון. שמו יהיה משהו כמו `alkom9-claude-sector-rotation-course-ZUjlo.zip`.

### ב. חלץ את ה-ZIP

- **iPhone:** Files app → לחץ ארוך על ה-ZIP → "Uncompress".
- **Android:** מנהל הקבצים → לחץ על ה-ZIP → "Extract".

תקבל תיקייה. לתוכה תיכנס לתת-תיקייה `sector-rotation-course/` – שם נמצאים: `app.py`, `pages/`, `utils/`, `requirements.txt`, וכו׳.

### ג. העלה לריפו החדש

1. חזור ל-https://github.com/<USERNAME>/sector-rotation-course (החליפן ב-username שלך).
2. לחץ על הקישור **"uploading an existing file"** במסך ה-Quick Setup.
3. גרור או בחר את **כל הקבצים והתיקיות** מתת-התיקייה `sector-rotation-course/`.  
   ⚠️ אל תעלה את התיקייה `sector-rotation-course/` עצמה – אלא את **התוכן שלה** ברמה הראשונה של הריפו החדש.

   קבצים שצריך להעלות:
   ```
   app.py
   requirements.txt
   README.md
   FRED_API_QUICK.md
   MOBILE_FINAL_STEPS.md
   pages/   (תיקייה - כל הקבצים בתוכה)
   utils/   (תיקייה - כל הקבצים בתוכה)
   .streamlit/   (תיקייה - אם רואים אותה; היא מוסתרת בחלק מהמנהלי קבצים)
   ```

   **טיפ למובייל:** אם המנהל קבצים שלך לא מציג את `.streamlit` (תיקייה שמתחילה בנקודה היא מוסתרת), אל תדאג – יש לנו דרך פשוטה ליצור אותה. ראה צעד 3 למטה.

4. **Commit message:** `Initial commit – Sector Rotation course`
5. בחר **Commit directly to the `main` branch**.
6. לחץ **Commit changes**.

---

## 3️⃣ הוסף את הקובץ `.streamlit/config.toml` ידנית (אם לא הועלה)

זה הקובץ שקובע את ה-theme השחור והעיצוב למובייל. אם המנהל קבצים שלך לא העלה את התיקייה הנסתרת `.streamlit/`:

1. בריפו ב-GitHub, לחץ **Add file** → **Create new file**.
2. בשורת השם: **`.streamlit/config.toml`** (חשוב – `.streamlit/` עם הסלאש יוצר תת-תיקייה).
3. הדבק את התוכן הזה:

   ```toml
   [theme]
   base = "dark"
   primaryColor = "#1f77b4"
   backgroundColor = "#0e1117"
   secondaryBackgroundColor = "#1c1f26"
   textColor = "#fafafa"
   font = "sans serif"

   [server]
   headless = true
   runOnSave = false

   [browser]
   gatherUsageStats = false

   [client]
   showErrorDetails = true
   toolbarMode = "minimal"
   ```

4. **Commit message:** `Add Streamlit config`.
5. **Commit directly to main**.

---

## 4️⃣ פרוס ב-Streamlit Cloud

זהה ל-`MOBILE_FINAL_STEPS.md` רק עם הבדלים קטנים:

- **Repository:** `<USERNAME>/sector-rotation-course`
- **Branch:** `main`
- **Main file path:** `app.py` *(ללא תת-תיקייה – הקבצים יושבים ברמה ראשונה)*

---

## 5️⃣ Secrets

זה זהה ל-`MOBILE_FINAL_STEPS.md` – Settings → Secrets → הדבק:

```toml
password = "Choose-A-Strong-Password-123!"
fred_api_key = "your_fred_key_from_step_1"
```

Save. Reboot אוטומטי. בדוק שעובד.

---

## אזהרה לגבי הריפו הישן

אחרי שווידאת שהריפו החדש עובד מצוין, אתה יכול **למחוק את הסניף הזה** מהריפו הישן (`alkom9/alkom9`):

```
Settings → Branches → claude/sector-rotation-course-ZUjlo → Delete
```

או פשוט להשאיר – הוא לא מפריע, רק שב חזק.

---

## בעיות נפוצות

**"לא רואה את התיקייה `.streamlit` ב-ZIP אחרי החילוץ"**  
→ תיקיות שמתחילות בנקודה מוסתרות באייפון ובאנדרואיד. השתמש בצעד 3 (יצירה ידנית מ-GitHub Web).

**"Streamlit אומר ModuleNotFoundError: utils"**  
→ Main file path צריך להיות `app.py` בדיוק (לא `sector-rotation-course/app.py`) כי בריפו החדש הקבצים בשורש.

**"Streamlit אומר 'app file not found'"**  
→ ודא שה-`app.py` נמצא ברמת השורש של הריפו, ושבחרת את ה-branch הנכון (`main`).

**"לא רואים נתונים במודול 4"**  
→ Secrets → ודא ש-`fred_api_key` קיים ולא חתוך. ראה `FRED_API_QUICK.md`.
