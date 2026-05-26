# מסלול מורפולוגיית הפועל (Verb Morphology Track)

## מערכת החריצים (Slot System)

הפועל הטורקי בנוי משרשרת סיומות בסדר קבוע. חשבו על זה כטופס עם שדות:

```
חריץ 1: גזע הפועל (STEM)
חריץ 2: שלילה (NEG) — -mE / -mA
חריץ 3: יכולת (ABIL) — -(y)Ebil
חריץ 4: זמן/היבט (TENSE/ASPECT)
חריץ 5: תנאי/אופן (COND/MOOD) — -sE
חריץ 6: גוף ומספר (PERSON/NUMBER)
חריץ 7: חלקיקית שאלה (Q) — mI
```

### דוגמה מלאה
```
gel-e-me-yebil-ecek-ti-m       mi?
STEM-ABIL-NEG-ABIL-FUT-PAST-1SG  Q

"האם לא הייתי יכול לבוא?"
```

---

## חריץ 1: גזע הפועל (STEM)

כל פועל טורקי מסתיים ב-mak/-mek באינפיניטיב. הגזע = האינפיניטיב בלי mak/mek:

| אינפיניטיב | גזע | משמעות |
|-----------|-----|--------|
| gel-mek | gel- | לבוא |
| git-mek | git- | ללכת |
| yap-mak | yap- | לעשות |
| oku-mak | oku- | לקרוא |
| gör-mek | gör- | לראות |

### השוואה לעברית
בעברית, שורש הפועל (ש-מ-ר) + בניין (נפעל, הפעיל...) = גזע.
בטורקית, הגזע הוא יחידה אחת פשוטה — אין "בניינים".

---

## חריץ 2: שלילה (NEG) — -mE/-mA

| חיוב | שלילה |
|------|-------|
| geliyorum (אני בא) | gel**me**yorum (אני לא בא) |
| geldim (באתי) | gel**me**dim (לא באתי) |
| gideceğim (אלך) | git**me**yeceğim (לא אלך) |

**כלל**: -me (אחרי תנועה קדמית) / -ma (אחרי תנועה אחורית).
מקום: מיד אחרי הגזע, לפני כל סיומת אחרת.

**השוואה לעברית**: בעברית, שלילה = מילה נפרדת ("לא באתי"). בטורקית, היא חלק מהפועל עצמו.

---

## חריץ 3: יכולת (ABIL) — -(y)Ebil

| רגיל | יכולת | שלילה + יכולת |
|------|-------|-------------|
| geliyorum | gel**ebil**iyorum (אני יכול לבוא) | gel**eme**yorum (אני לא יכול לבוא) |
| yapıyorum | yap**abil**iyorum (אני יכול לעשות) | yap**ama**yorum (אני לא יכול לעשות) |

**שימו לב**: בשלילה, -Ebil הופך ל-EmE (gel-eme-yorum), לא *gel-ebil-me-yorum.

---

## חריץ 4: זמן/היבט (TENSE/ASPECT)

### הצגה הדרגתית בקורס

#### A1.1 — שלושה זמנים בסיסיים

**1. Present Continuous — -(I)yor** (שיעור 2)
פעולה שמתרחשת עכשיו / הרגל נוכחי.
```
gel-iyor-um    אני בא (עכשיו)
yap-ıyor-sun   אתה עושה
oku-yor         הוא/היא קורא/ת
```
**חריגה**: הסיומת -yor קשיחה (לא משתתפת בהרמוניית תנועות).
גוף: -um, -sun, -∅, -uz, -sunuz, -lar

**2. Past Definite — -DI** (שיעור 6)
עבר שהדובר חווה/ראה ישירות.
```
gel-di-m       באתי
yap-tı-n       עשית
gör-dü-k       ראינו
```
הרמוניה: I-type (-di/-dı/-dü/-du) + עיצור (t אחרי ç,f,h,k,p,s,ş,t).
גוף: -m, -n, -∅, -k, -nız, -lar

**3. Imperative** (שיעור 4)
```
gel!           בוא!
gel-in!        בואו!
gel-iniz!      בואו! (פורמלי)
```

#### A1.2 — עוד שלושה

**4. Future — -(y)AcAk** (שיעור 1)
```
gel-eceğ-im     אבוא
yap-acağ-ız     נעשה
```
הרמוניה: E-type (-ecek/-acak). ğ מופיע לפני סיומת תנועה.

**5. Aorist — -(A/I)r** (שיעור 4)
הרגל, כלליות, "עתיד רגיל", הבטחה.
```
gel-ir-im       אני בא (בדרך כלל)
yap-ar-sın      אתה עושה (בדרך כלל)
```
כללי צורה:
- חד-הברתיים: -(A)r: gel-ir, yap-ar, gör-ür, bul-ur
- רב-הברתיים: -(I)r: başla-r, konuş-ur

**שלילה Aorist — מיוחדת!**
```
gel-me-m        אני לא בא (בד"כ)    ← לא *gel-me-r-im
yap-ma-z-sın    אתה לא עושה (בד"כ)  ← -z במקום -r
```

**6. Present Continuous vs. Aorist — הבחנה קריטית**
```
Çay içiyorum.     אני שותה תה (עכשיו, ברגע זה).
Çay içerim.       אני שותה תה (בדרך כלל, אני אוהב תה).
```

#### A2 — שני זמנים נוספים + copula

**7. Evidential Past — -mIş** (שיעור 3)
עבר שהדובר לא חווה ישירות — שמע, הסיק, גילה.
```
Ali gel-miş.      עלי בא (כנראה; שמעתי; גיליתי שהוא פה).
Ali gel-di.       עלי בא (ראיתי אותו מגיע).
```
**אין מקבילה בעברית!** זו קטגוריה דקדוקית חדשה: **ראייתיות** (evidentiality).

**8. Necessitative — -mElI** (שיעור 5)
חובה, צורך.
```
gel-meli-yim      אני צריך/חייב לבוא
yap-malı-sın      אתה צריך לעשות
```

**9. Copula suffixes** (שיעור 1)
```
öğrenci-yim       אני תלמיד
güzel-sin          את/ה יפה
hasta-∅            הוא/היא חולה
iyiyiz             אנחנו בסדר
```

#### B1 — זמנים מורכבים ואופנים

**10. Conditional — -sE** (שיעור 2)
```
gel-se-m          אם אבוא / הלוואי שאבוא
yap-sa-n          אם תעשה
```

**11. Optative — -(y)E** (שיעור 4)
```
gel-eyim           שאבוא / בוא אבוא
gid-elim           בואו נלך
```

**12. Compound tenses** (שיעורים 5–8)
```
gel-miş-ti-m       (כנראה) באתי (לפני זמן מה) — evidential pluperfect
gel-iyor-du-m      הייתי בא / באתי (ממושך בעבר) — past continuous
gel-ecek-ti-m      הייתי אמור לבוא — future in the past
gel-ir-di-m        הייתי בא (רגיל בעבר) — habitual past
```

#### B2 — שמות פועל וביניים

**13. Verbal Nouns (שמות פועל)**
```
gel-mek            לבוא (infinitive)
gel-me             ביאה / עניין הביאה (gerund)
gel-iş             ביאה (manner/style)
gel-dik            (העובדה ש)באנו
gel-ecek           (מה ש)יבוא
```

**14. Participles (ביניים)**
```
gel-en adam         האיש שבא (subject participle)
gör-düğ-üm film    הסרט שראיתי (object participle)
yap-ılacak iş      העבודה שתיעשה (future passive participle)
```

#### C1 — צורות ספרותיות ומתקדמות

**15. Literary/archaic forms**
- -mAktA (continuous formal): gelmektedir
- -(I)yor olacak (future continuous)
- -mIş olacak (future perfect)

---

## חריץ 6: גוף ומספר (PERSON/NUMBER)

### שתי קבוצות סיומות גוף

**קבוצה 1 (Type I) — עם רוב הזמנים**
| גוף | סיומת | דוגמה (past -DI) |
|------|-------|-------------------|
| 1SG | -m | gel-di-m |
| 2SG | -n | gel-di-n |
| 3SG | ∅ | gel-di |
| 1PL | -k | gel-di-k |
| 2PL | -nIz | gel-di-niz |
| 3PL | -lEr | gel-di-ler |

**קבוצה 2 (Type II) — עם present continuous ו-copula**
| גוף | סיומת | דוגמה (-yor) |
|------|-------|-------------|
| 1SG | -(y)Im | gel-iyor-um |
| 2SG | -sIn | gel-iyor-sun |
| 3SG | ∅ | gel-iyor |
| 1PL | -(y)Iz | gel-iyor-uz |
| 2PL | -sInIz | gel-iyor-sunuz |
| 3PL | -lEr | gel-iyor-lar |

---

## טבלת סיכום — סדר הצגה בקורס

| שיעור | צורה חדשה | חריצים מעורבים |
|-------|----------|---------------|
| L01-02 | Present continuous (-yor) | STEM + T/A + PERS |
| L01-04 | Imperative | STEM (+ PERS) |
| L01-06 | Past definite (-DI) | STEM + T/A + PERS |
| L01-06 | Negative (-mE) | STEM + NEG + T/A + PERS |
| L01-10 | Copula suffixes | — |
| L02-01 | Future (-AcAk) | STEM + T/A + PERS |
| L02-04 | Aorist (-(A/I)r) | STEM + T/A + PERS |
| L02-04 | Negative aorist (-mEz) | STEM + NEG + T/A + PERS |
| L03-03 | Evidential (-mIş) | STEM + T/A + PERS |
| L03-05 | Necessitative (-mElI) | STEM + T/A + PERS |
| L03-01 | Copula past (-DI on nominals) | — |
| L04-02 | Conditional (-sE) | STEM + T/A + COND + PERS |
| L04-04 | Optative (-(y)E) | STEM + MOOD + PERS |
| L04-05 | Compound: past continuous (-yordu) | STEM + T/A1 + T/A2 + PERS |
| L04-08 | Compound: evidential pluperfect (-mIştI) | STEM + T/A1 + T/A2 + PERS |
| L05-02 | Verbal nouns | STEM + VN suffix |
| L05-04 | Participles | STEM + PART suffix |
| L05-08 | Ability (-Ebil) | STEM + ABIL + T/A + PERS |
| L06-02 | Passive (-Il) | STEM + PASS + T/A + PERS |
| L06-04 | Causative (-DIr) | STEM + CAUS + T/A + PERS |
| L06-06 | Reflexive (-In) / Reciprocal (-Iş) | STEM + VOICE + T/A + PERS |

---

## השוואה מסכמת: פועל עברי vs. פועל טורקי

| תכונה | עברית | טורקית |
|-------|-------|--------|
| מבנה | שורש + בניין (תבניתי) | גזע + שרשרת סיומות (ליניארי) |
| מין | כן (הלך/הלכה) | לא |
| גוף/מספר | כן | כן |
| זמן | 3 (עבר, הווה, עתיד) | 5+ (+ evidential, aorist, necessitative) |
| שלילה | מילה נפרדת (לא) | סיומת (-mE) |
| יכולת | מילה נפרדת (יכול) | סיומת (-Ebil) |
| ראייתיות | אין | כן (-mIş) |
| סביל | בניין נפעל/פועל | סיומת (-Il) |
| גורם | בניין הפעיל | סיומת (-DIr) |
