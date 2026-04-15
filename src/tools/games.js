// Games: trivia, fortune, song guessing, interactive story, jokes

async function getTrivia(category) {
    try {
        const catMap = { general: 9, science: 17, history: 23, sports: 21, music: 12, movies: 11, geography: 22 };
        const catId = catMap[String(category).toLowerCase()] || 9;
        const res = await fetch(`https://opentdb.com/api.php?amount=1&category=${catId}&type=multiple`, {
            signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return _localTrivia();
        const d = await res.json();
        if (d.response_code !== 0 || !d.results?.length) return _localTrivia();
        const q = d.results[0];
        const answers = [...q.incorrect_answers, q.correct_answer].sort(() => Math.random() - 0.5);
        const L = ['א', 'ב', 'ג', 'ד'];
        const correctIdx = answers.indexOf(q.correct_answer);
        return {
            question: `❓ ${_decodeHtml(q.question)}\n\n${answers.map((a, i) => `${L[i]}. ${_decodeHtml(a)}`).join('\n')}`,
            answer: `✅ ${L[correctIdx]}. ${_decodeHtml(q.correct_answer)}`,
            correctLetter: L[correctIdx]
        };
    } catch { return _localTrivia(); }
}

function _decodeHtml(s) {
    return String(s).replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#039;/g, "'");
}

function _localTrivia() {
    const list = [
        { q: 'מה הבירה של ישראל?', a: 'ירושלים', opts: ['תל אביב', 'ירושלים', 'חיפה', 'באר שבע'] },
        { q: 'כמה ימים יש בשנה לועזית רגילה?', a: '365', opts: ['360', '365', '366', '364'] },
        { q: 'מהי השפה הנפוצה ביותר לפי דוברים?', a: 'מנדרינית סינית', opts: ['אנגלית', 'ספרדית', 'מנדרינית סינית', 'ערבית'] },
        { q: 'מי חיבר את הסימפוניה התשיעית?', a: 'בטהובן', opts: ['מוצרט', 'בטהובן', 'באך', 'שופן'] },
        { q: 'מהו כוכב הלכת הגדול ביותר במערכת השמש?', a: 'צדק', opts: ['שבתאי', 'צדק', 'אורנוס', 'נפטון'] },
        { q: 'כמה רגליים לעכביש?', a: '8', opts: ['6', '8', '10', '12'] },
        { q: 'באיזו שנה הוקמה מדינת ישראל?', a: '1948', opts: ['1945', '1947', '1948', '1950'] },
        { q: 'מהי הנהר הארוך בעולם?', a: 'הנילוס', opts: ['האמזונס', 'הנילוס', 'הוולגה', 'הינגצה'] },
    ];
    const q = list[Math.floor(Math.random() * list.length)];
    const shuffled = [...q.opts].sort(() => Math.random() - 0.5);
    const L = ['א', 'ב', 'ג', 'ד'];
    const idx = shuffled.indexOf(q.a);
    return {
        question: `❓ ${q.q}\n\n${shuffled.map((o, i) => `${L[i]}. ${o}`).join('\n')}`,
        answer: `✅ ${L[idx]}. ${q.a}`,
        correctLetter: L[idx]
    };
}

function getFortune() {
    const day = new Date().getDate() + new Date().getMonth() * 31;
    const fortunes = [
        'הכוכבים מספרים שמשהו מפתיע עומד להגיע מכיוון שלא ציפית. תהיי פתוחה ✨',
        'אנרגיות חזקות סובבות אותך — זה הזמן המושלם לפתוח דף חדש 🌙',
        'מישהו חושב עליך בדיוק עכשיו. לא אגיד מי... אבל זה ברור 👁',
        'שבוע קשה אבל גשם עז מביא צמחייה ירוקה. הסערה תשאיר אחריה משהו יפה 🌿',
        'הגלגל מסתובב — מה שנתת חוזר אליך עכשיו פי כמה 🌀',
        'קמץ אחד של עוז יביא לך מה שחצי שנה של חכייה לא הצליחה 🔥',
        'הקלפים מראים מספר שלוש. שלוש בחירות — אבל רק אחת נכונה ❤️',
        'המזל שלך בסימן מים השבוע. היה גמיש כמו הנהר 💧',
        'כוכב בהיר מאיר בשמיים שלך. כוכב של שקט פנימי 🌟',
        'משהו שאיבדת מזמן — פיזי או רגשי — עומד להגיע בחזרה 🗝️',
        'אל תתנגד לשינוי שמגיע. הוא בדיוק מה שצריך 🍃',
        'שני אנשים בחייך — אחד ייתן לך כוח, אחד ייקח. תדעי להבחין 🔮',
    ];
    const prefixes = ['🔮 ראיתי בכדור הבדולח...', '🌙 הכוכבים ספרו לי...', '🃏 הקלפים חשפו...', '👁 הגורל לחש לי...'];
    return `${prefixes[day % prefixes.length]}\n\n${fortunes[day % fortunes.length]}`;
}

const SONGS = [
    { artist: 'עידן רייכל', song: 'Im Ninalu', lyric: 'אם יינעלו דלתות שמיים, תפילתי תבקע עננים' },
    { artist: 'שלמה ארצי', song: 'יונה', lyric: 'יונה, יונה, תגידי לי מה שלומך' },
    { artist: 'מאיר אריאל', song: 'ירושלים של ברזל', lyric: 'ירושלים של ברזל, ושל עופרת, ושל שחור' },
    { artist: 'אריק איינשטיין', song: 'שיר נגד', lyric: 'אני לא רוצה לדעת מה יהיה מחר' },
    { artist: 'Queen', song: 'Bohemian Rhapsody', lyric: 'Is this the real life? Is this just fantasy? Caught in a landslide' },
    { artist: 'The Beatles', song: 'Hey Jude', lyric: 'Hey Jude, don\'t make it bad, take a sad song and make it better' },
    { artist: 'Adele', song: 'Rolling in the Deep', lyric: 'We could have had it all, rolling in the deep' },
    { artist: 'אייל גולן', song: 'מלכה', lyric: 'מלכה, את נשמת נשמתי, את מבטחי' },
    { artist: 'הדג נחש', song: 'לילות לבנים', lyric: 'לילות לבנים, שחרים שחורים, ואני ביניהם' },
    { artist: 'מגי מזרחי', song: 'עצמות', lyric: 'ולי אין עצמות, ולי אין גוף, אבל יש לי נשמה' },
    { artist: 'Coldplay', song: 'The Scientist', lyric: 'Nobody said it was easy, no one ever said it would be this hard' },
    { artist: 'Amy Winehouse', song: 'Rehab', lyric: 'They tried to make me go to rehab, I said no, no, no' },
];

function getSongGuess() {
    const song = SONGS[Math.floor(Math.random() * SONGS.length)];
    return {
        lyric: `🎵 נחשו איזה שיר:\n\n"${song.lyric}"`,
        answer: `🎤 ${song.song} — ${song.artist}`,
        song: song.song,
        artist: song.artist
    };
}

const STORY = {
    start: { text: '🌙 את מוצאת את עצמך בפני שלושה שבילים ביער עתיק.\nלאן תלכי?\n\nא. לתוך היער\nב. לנהר מנצנץ\nג. לכיוון ההר', options: { א: 'forest', ב: 'river', ג: 'mountain' } },
    forest: { text: '🌲 עמקת ביער. קול מוזר מאחורי עץ ענק.\n\nא. לבדוק מה זה\nב. לברוח\nג. לחכות ולהקשיב', options: { א: 'investigate', ב: 'run', ג: 'listen' } },
    river: { text: '🏞️ נהר זוהר בכסף. על הגדה דייג זקן מחייך.\nהוא מציע לך מקום בסירה.\n\nא. לעלות לסירה\nב. לשחות לצד השני\nג. לשבת ולנוח על הגדה', options: { א: 'boat', ב: 'swim', ג: 'rest' } },
    mountain: { text: '⛰️ פסגת ההר. כל העולם נפרש מולך. לפתע נשר ענקי מתקרב.\n\nא. לפרוס זרועות ולנסות לעוף\nב. להישאר שקטה ולצפות\nג. לרדת בחזרה', options: { א: 'fly', ב: 'watch', ג: 'descend' } },
    investigate: { text: '🦊 שועל קסום מאחורי העץ. הוא מציע לך מתנה אחת.\n✨ *סוף: מסע הפלאות* — בחרת להתמודד עם הלא-נודע. נועזת!', options: {} },
    run: { text: '🏃‍♀️ רצת מהר ויצאת מהיער לשדה פתוח.\n🌅 *סוף: הבריחה הגדולה* — לפעמים לברוח זה החוכמה.', options: {} },
    listen: { text: '🎵 הקשבת וזיהית: מוזיקה עתיקה, לא חיה. הבנת משהו על השתיקה.\n💫 *סוף: קול הדממה* — לא כל תשובה צריכה מילים.', options: {} },
    boat: { text: '⛵ הדייג הוביל אותך לאי נסתר. שם מצאת משהו שחיפשת זמן רב.\n💎 *סוף: גילוי האוצר* — הרפתקה שתזכרי לנצח!', options: {} },
    swim: { text: '🌊 שחית לצד השני. שם קסבה עתיקה מלאה סודות.\n🏛️ *סוף: העיר האבודה* — גילית מה אחרים פחדו לגלות.', options: {} },
    rest: { text: '🌿 ישבת על הגדה. תוך כמה דקות הבנת שכאן הייתה כל התשובה.\n☮️ *סוף: הנהר שלימד* — שקט הוא לפעמים הדרך הארוכה ביותר.', options: {} },
    fly: { text: '🦅 קפצת. לרגע ממש קצר — הייתה תחושה של מעוף.\n👑 *סוף: הממלכה הנסתרת* — מי שמעזת — מגיעה לשמיים.', options: {} },
    watch: { text: '🌄 צפית בנשר עד שנעלם. הבנת שאין צורך להגיע לכל מקום.\n🌟 *סוף: ההכרה הפנימית* — הנסיעה הכי חשובה היא פנימה.', options: {} },
    descend: { text: '🏘️ ירדת ומצאת כפר שמח שחיכה לך בדיוק.\n🎉 *סוף: הבית שמצאת* — לפעמים הדרך חזרה היא הדרך קדימה.', options: {} },
};

function getStoryNode(nodeId) {
    return STORY[nodeId] || STORY.start;
}

function getDailyJoke() {
    const jokes = [
        'שאל ילד את אביו: "אבא, למה השמיים כחולים?"\nהאבא: "כי גם הם לא מבינים את הממשלה"',
        'מה ההבדל בין פסיכולוג לקוסם?\nקוסם מוציא ארנב מכובע. פסיכולוג מוציא אחד מהמוח.',
        'בדיחה על קצרי זיכרון:\n.\n.\n.\nשכחתי אותה',
        'אשה צלצלה לבעלה: "נגנב לי הארנק עם כל הכסף!"\nהבעל: "תתקשרי למשטרה"\nהאשה: "איך? הטלפון גם היה בארנק"',
        'למה הצב עובר את הכביש?\nכדי להגיע לשל קיוסק.',
        'שאל תלמיד את המורה: "האם אפשר להעניש מישהו על משהו שלא עשה?"\nהמורה: "ודאי שלא"\nהתלמיד: "טוב, כי לא עשיתי את שיעורי הבית"',
    ];
    return jokes[new Date().getDate() % jokes.length];
}

module.exports = { getTrivia, getFortune, getSongGuess, getStoryNode, getDailyJoke };
