/**
 * אשף הגדרה - עוזר להגדיר את הבוט לראשונה
 */
const readline = require('readline');
const fs = require('fs');
const path = require('path');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(question) {
    return new Promise(resolve => rl.question(question, resolve));
}

function printLine(char = '=', len = 55) {
    console.log(char.repeat(len));
}

async function main() {
    console.clear();
    printLine();
    console.log('🤖 הגדרת אייג\'נט AI לוואצאפ');
    printLine();
    console.log('');

    // בדוק גרסת Node.js
    const nodeVersion = parseInt(process.version.slice(1));
    if (nodeVersion < 18) {
        console.error('❌ נדרשת Node.js גרסה 18 ומעלה!');
        console.error(`   גרסה נוכחית: ${process.version}`);
        console.error('   הורד מ: https://nodejs.org\n');
        rl.close();
        process.exit(1);
    }

    console.log('ברוך הבא! בוא נגדיר את הבוט שלך.\n');
    console.log('הבוט משתמש ב-Google Gemini - שירות AI חינמי לגמרי!');
    console.log('');

    // הסבר כיצד לקבל API key
    printLine('-');
    console.log('📋 שלב 1: קבלת מפתח API חינמי מ-Google');
    printLine('-');
    console.log('');
    console.log('1. פתח בדפדפן: https://aistudio.google.com/app/apikey');
    console.log('2. התחבר עם חשבון Google שלך');
    console.log('3. לחץ על "Create API Key"');
    console.log('4. העתק את המפתח (נראה כמו: AIzaSy...)');
    console.log('');

    const apiKey = await ask('📋 הדבק כאן את מפתח ה-API: ');

    if (!apiKey?.trim() || apiKey.trim() === 'your_api_key_here') {
        console.log('\n❌ לא הוזן מפתח. הגדרה בוטלה.');
        rl.close();
        return;
    }

    const trimmedKey = apiKey.trim();

    // בדיקה בסיסית שהמפתח נראה תקין
    if (!trimmedKey.startsWith('AIza') || trimmedKey.length < 30) {
        console.log('\n⚠️  המפתח לא נראה תקין. ודא שהעתקת אותו נכון.');
        const cont = await ask('להמשיך בכל זאת? (כן/לא): ');
        if (!cont.toLowerCase().includes('כ') && !cont.toLowerCase().includes('y')) {
            rl.close();
            return;
        }
    }

    // שם הבוט
    console.log('');
    const botNameInput = await ask('🤖 שם הבוט (אופציונלי, Enter לברירת מחדל "עוזר AI"): ');
    const botName = botNameInput?.trim() || 'עוזר AI';

    // קבוצות
    console.log('');
    console.log('👥 האם לענות בקבוצות?');
    console.log('   לא (ברירת מחדל) - הבוט יענה רק בהודעות פרטיות');
    console.log('   כן - הבוט יענה גם בקבוצות (רק כשמתייגים אותו)');
    const groupsInput = await ask('הגב בקבוצות? (כן/לא, Enter = לא): ');
    const respondInGroups = groupsInput?.trim().toLowerCase().startsWith('כ') ||
                           groupsInput?.trim().toLowerCase().startsWith('y');

    // כתוב קובץ .env
    const envContent = `# ========================================
# הגדרות אייג'נט AI לוואצאפ
# ========================================

# מפתח API של Google Gemini (חינמי!)
GEMINI_API_KEY=${trimmedKey}

# שם הבוט
BOT_NAME=${botName}

# האם לענות בקבוצות? (true/false)
RESPOND_IN_GROUPS=${respondInGroups}
`;

    const envPath = path.join(process.cwd(), '.env');
    fs.writeFileSync(envPath, envContent, 'utf8');

    console.log('');
    printLine();
    console.log('✅ הגדרה הושלמה בהצלחה!');
    printLine();
    console.log('');
    console.log(`📝 שם הבוט: ${botName}`);
    console.log(`👥 מגיב בקבוצות: ${respondInGroups ? 'כן' : 'לא (רק הודעות פרטיות)'}`);
    console.log('');
    console.log('🚀 להפעלת הבוט, הרץ:');
    console.log('   npm start');
    console.log('');
    console.log('📱 לאחר ההפעלה:');
    console.log('   1. יופיע קוד QR במסך');
    console.log('   2. פתח וואצאפ → מכשירים מחוברים → קשר מכשיר');
    console.log('   3. סרוק את הקוד');
    console.log('   4. שלח הודעה לבוט!\n');

    rl.close();
}

main().catch(error => {
    console.error('שגיאה:', error.message);
    rl.close();
    process.exit(1);
});
