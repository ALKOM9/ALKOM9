// Task Classifier — no LLM call, pure pattern matching (fast + free)
// Input: user message string
// Output: { taskType, complexity, requiresTools, isHebrew }

// Task type keyword patterns
const PATTERNS = {
    coding: [
        /\b(code|function|class|algorithm|debug|error|bug|script|program|implement|syntax|api|sql|query|regex|parse|compile)\b/i,
        /\b(javascript|python|java|c\+\+|typescript|nodejs|react|html|css|bash|shell|git)\b/i,
        /```|`[^`]+`/,
        /\b(כתוב קוד|תכתוב קוד|קוד|פונקציה|אלגוריתם|באג|שגיאה בקוד)\b/,
    ],
    reasoning: [
        /\b(why|how|explain|analyze|compare|evaluate|argue|prove|logic|step.by.step|because|therefore|conclude)\b/i,
        /\b(math|calculate|equation|formula|solve|derive|integral|derivative|probability|statistics)\b/i,
        /\b(למה|איך|הסבר|נתח|השווה|הוכח|לוגיקה|שלב אחר שלב|חשב|משוואה|סטטיסטיקה)\b/,
        /\d+[\s]*[+\-*/^%]\s*\d+|\b(percent|percentage)\b/i,
    ],
    creative: [
        /\b(write|compose|create|story|poem|song|fiction|narrative|creative|imagine|fantasy|draw|design)\b/i,
        /\b(כתוב סיפור|כתוב שיר|צור|דמיין|ספור|תאר|בדה|יצירתי)\b/,
    ],
    analysis: [
        /\b(summarize|summary|analyze|analysis|review|evaluate|assess|critique|feedback|opinion|think about)\b/i,
        /\b(סכם|ניתוח|נתח|סקור|הערכה|דעה|מה אתה חושב|מה דעתך)\b/,
    ],
    vision: [
        /\b(image|photo|picture|describe|what.*(see|show|image)|look at|attached)\b/i,
        /\b(תמונה|צילום|מה רואים|תאר את התמונה|מה יש בתמונה)\b/,
    ],
    simple: [
        /^.{0,60}[?]?$/, // Short messages (under 60 chars)
    ],
};

// Complexity signals
const HIGH_COMPLEXITY_SIGNALS = [
    /\b(step.by.step|detailed|comprehensive|thorough|in depth|elaborate|explain fully|cover all)\b/i,
    /\b(שלב אחר שלב|מפורט|מקיף|בעומק|הרחב|פרט|הסבר מלא)\b/,
    /\b(compare.*and|difference.*between|pros.*cons|advantages.*disadvantages)\b/i,
];

const LOW_COMPLEXITY_SIGNALS = [
    /^.{0,40}[?]?$/, // Very short
    /\b(what is|who is|when|where|how much|how many|מה זה|מי|מתי|איפה|כמה)\b/i,
    /\b(yes|no|true|false|כן|לא)\b/i,
];

// Hebrew detection
const HEBREW_RE = /[\u0590-\u05FF]/;

// Tool requirement signals (needs external data)
const TOOL_SIGNALS = [
    /\b(weather|news|stock|price|rate|current|today|latest|search|find|look up)\b/i,
    /\b(מזג אוויר|חדשות|מניה|מחיר|שער|עכשיו|היום|חפש|מצא)\b/,
    /\d{4}|bitcoin|ethereum|usd|eur|nis|ils|\$|€|₪/i,
];

function classify(message, isImage = false) {
    if (!message && !isImage) {
        return { taskType: 'simple', complexity: 'low', requiresTools: false, isHebrew: false };
    }

    const text = String(message || '');
    const isHebrew = HEBREW_RE.test(text);

    // Vision always wins if there's an image
    if (isImage) {
        return { taskType: 'vision', complexity: 'medium', requiresTools: false, isHebrew };
    }

    // Score each task type
    const scores = {};
    for (const [type, patternList] of Object.entries(PATTERNS)) {
        scores[type] = patternList.filter(re => re.test(text)).length;
    }

    // Pick highest scoring type (default: simple)
    let taskType = 'simple';
    let maxScore = 0;
    for (const [type, score] of Object.entries(scores)) {
        if (type !== 'simple' && score > maxScore) {
            maxScore = score;
            taskType = type;
        }
    }

    // Determine complexity
    let complexity = 'medium';
    const highSignals = HIGH_COMPLEXITY_SIGNALS.filter(re => re.test(text)).length;
    const lowSignals = LOW_COMPLEXITY_SIGNALS.filter(re => re.test(text)).length;
    const len = text.trim().length;

    if (highSignals > 0 || len > 300) complexity = 'high';
    else if (lowSignals > 0 || len < 60) complexity = 'low';

    // Tool requirement
    const requiresTools = TOOL_SIGNALS.some(re => re.test(text));

    return { taskType, complexity, requiresTools, isHebrew };
}

module.exports = { classify };
