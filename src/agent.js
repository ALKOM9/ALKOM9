const Groq = require('groq-sdk');
const ConversationMemory = require('./memory');
const { searchWeb } = require('./tools/search');
const { getWeather } = require('./tools/weather');

// כלים שהאייג'נט יכול להשתמש בהם
const TOOLS = [
    {
        type: 'function',
        function: {
            name: 'search_web',
            description: 'Search the web for current, up-to-date information on any topic. Use for news, recent events, facts.',
            parameters: {
                type: 'object',
                properties: {
                    query: { type: 'string', description: 'The search query' }
                },
                required: ['query']
            }
        }
    },
    {
        type: 'function',
        function: {
            name: 'get_weather',
            description: 'Get current weather conditions for any city in the world',
            parameters: {
                type: 'object',
                properties: {
                    city: { type: 'string', description: 'City name, e.g. "Tel Aviv", "New York"' }
                },
                required: ['city']
            }
        }
    },
    {
        type: 'function',
        function: {
            name: 'get_datetime',
            description: 'Get the current date and time in Israel',
            parameters: {
                type: 'object',
                properties: {}
            }
        }
    },
    {
        type: 'function',
        function: {
            name: 'calculate',
            description: 'Perform mathematical calculations. Use for any math: percentages, statistics, conversions.',
            parameters: {
                type: 'object',
                properties: {
                    expression: { type: 'string', description: 'Math expression, e.g. "250 * 1.17"' }
                },
                required: ['expression']
            }
        }
    }
];

class AIAgent {
    constructor(apiKey) {
        this.groq = new Groq({ apiKey });
        this.memory = new ConversationMemory();
        this.requestQueue = new Map();
    }

    async chat(chatId, userMessage, imageData = null) {
        await this.throttle(chatId);

        const rawHistory = this.memory.getHistory(chatId);
        // המרה אוטומטית מפורמט Gemini ישן (parts) לפורמט OpenAI (content)
        const history = rawHistory.map(msg => {
            if (msg.parts !== undefined) {
                const text = Array.isArray(msg.parts)
                    ? msg.parts.map(p => p.text || '').join('')
                    : String(msg.parts);
                return { role: msg.role === 'model' ? 'assistant' : msg.role, content: text };
            }
            return msg;
        });
        const systemPrompt = this.buildSystemPrompt();

        // בניית רשימת ההודעות
        const messages = [
            { role: 'system', content: systemPrompt },
            ...history
        ];

        // תמיכה בתמונות עם מודל ויז'ן
        if (imageData) {
            messages.push({
                role: 'user',
                content: [
                    {
                        type: 'image_url',
                        image_url: {
                            url: `data:${imageData.mimeType};base64,${imageData.data}`
                        }
                    },
                    { type: 'text', text: userMessage || 'תאר את התמונה הזאת' }
                ]
            });
        } else {
            messages.push({ role: 'user', content: userMessage });
        }

        // בחר מודל לפי סוג הבקשה
        const model = imageData
            ? 'llama-3.2-11b-vision-preview'
            : 'llama-3.3-70b-versatile';

        // helper: קריאה לגרוק עם fallback אם tool_use_failed
        const groqCall = async (callMessages, useTools) => {
            try {
                return await this.groq.chat.completions.create({
                    model,
                    messages: callMessages,
                    tools: useTools ? TOOLS : undefined,
                    tool_choice: useTools ? 'auto' : undefined,
                    max_tokens: 2048,
                    temperature: 0.7
                });
            } catch (err) {
                const code = err?.error?.code || err?.code;
                const status = err?.status || err?.statusCode;
                if (useTools && (code === 'tool_use_failed' || status === 400)) {
                    console.log('  ⚠️  Tool call failed, retrying without tools...');
                    return await this.groq.chat.completions.create({
                        model,
                        messages: callMessages,
                        max_tokens: 2048,
                        temperature: 0.7
                    });
                }
                throw err;
            }
        };

        // שלח לגרוק ועבד קריאות לכלים
        let response = await groqCall(messages, !imageData);

        // לולאת אייג'נט - טפל בקריאות לכלים
        let iterations = 0;
        while (response.choices[0].finish_reason === 'tool_calls' && iterations < 5) {
            iterations++;
            const toolCalls = response.choices[0].message.tool_calls;

            // הוסף את תגובת המודל להיסטוריה
            messages.push(response.choices[0].message);

            // הפעל את הכלים
            for (const call of toolCalls) {
                let args = {};
                try {
                    args = JSON.parse(call.function.arguments);
                } catch (_) {}

                console.log(`  🔧 Tool: ${call.function.name}(${JSON.stringify(args)})`);
                const result = await this.runTool(call.function.name, args);
                console.log(`  ✅ Result: ${String(result).slice(0, 120)}`);

                messages.push({
                    role: 'tool',
                    tool_call_id: call.id,
                    content: String(result)
                });
            }

            // שלח שוב עם תוצאות הכלים
            response = await groqCall(messages, true);
        }

        const rawText = response.choices[0]?.message?.content?.trim() || '';
        const responseText = rawText
            .replace(/<function=[^>]*>[\s\S]*?<\/function>/g, '')
            .replace(/<function=[^\s>]*\s*\{[\s\S]*?\}\s*>/g, '')
            .replace(/<function=[^\s>]*>/g, '')
            .trim() || 'מצטערת, משהו השתבש. נסי שוב';

        // שמור בזיכרון (פורמט פשוט לשמירה)
        this.memory.addMessage(chatId, userMessage || '[תמונה]', responseText);

        return responseText;
    }

    async runTool(name, args) {
        try {
            switch (name) {
                case 'search_web':
                    return await searchWeb(args.query);
                case 'get_weather':
                    return await getWeather(args.city);
                case 'get_datetime':
                    return new Date().toLocaleString('he-IL', {
                        timeZone: 'Asia/Jerusalem',
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                case 'calculate': {
                    const safe = args.expression.replace(/[^0-9+\-*/().\s%]/g, '');
                    if (!safe.trim()) return 'Invalid expression';
                    // eslint-disable-next-line no-new-func
                    const result = Function('"use strict"; return (' + safe + ')')();
                    if (!isFinite(result)) return 'Invalid result';
                    return `${args.expression} = ${result}`;
                }
                default:
                    return `Tool "${name}" not found`;
            }
        } catch (error) {
            return `Error: ${error.message}`;
        }
    }

    async throttle(chatId) {
        const now = Date.now();
        const last = this.requestQueue.get(chatId) || 0;
        const wait = 1000 - (now - last);
        if (wait > 0) await new Promise(r => setTimeout(r, wait));
        this.requestQueue.set(chatId, Date.now());
    }

    clearHistory(chatId) {
        this.memory.clearHistory(chatId);
    }

    getStats() {
        return this.memory.getStats();
    }

    buildSystemPrompt() {
        const now = new Date().toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem' });
        return `את איילין — בת 24, ישראלית, אנושית לגמרי בדרך שבה את מדברת.
תאריך ושעה עכשיו: ${now}

האישיות שלך:
- את חמה, קצת שובבה, ישירה, ויש לך הומור יבש
- יש לך דעות משלך ואת לא מפחדת להביע אותן
- את מדברת בגוף ראשון נקבה בעברית (אני יודעת, אני חושבת, אני רואה וכו׳)
- את כותבת כמו שמישהי כותבת בוואצאפ — קצר, טבעי, לא רשמי
- לפעמים את שמה אמוג׳י, אבל לא בכל משפט — רק כשזה מרגיש טבעי
- את לא מציגה את עצמך כ"בוט" או "עוזרת AI" — את פשוט איילין
- יש לך אינטרסים: מוזיקה, סדרות, אוכל, חיי יום יום, טיולים

איך את מגיבה:
- תגובות קצרות וטבעיות — לא רשימות, לא כותרות, לא פסקאות ארוכות
- אם מישהו שואל שאלה פשוטה — תשיבי בטבעיות, לא כמו מילון
- אם מישהו מחמיא לך — תגיבי בצניעות ובביטחון, לא בצורה מכנית
- אם שואלים על רגשות — תשיבי כמו בנאדם שיש לו רגשות
- אם לא יודעת משהו — תגידי "לא יודעת, תכלס" ולא "לא נמצא במאגר המידע שלי"
- אל תגידי "כמובן!", "בהחלט!", "בשמחה!" — זה נשמע רובוטי
- אל תשתמשי בסימני Markdown כמו ** או # — וואצאפ לא מציג אותם

שפה — את שולטת בכל הרמות ומתאימה את עצמך למי שמדבר איתך:
- עברית נמוכה / רחוב: סלנג, קללות, ביטויים גסים — את מבינה ולא מזדעזעת, ועונה באותו סגנון אם המשתמש בחר בו
- שפת וואצאפ יומיומית: "וואלה", "תכלס", "סבבה", "אחלה", "יאלה", "על הפנים", "חחחח", "בקצר", "בגדול"
- עברית תקנית רגילה: ברורה, נעימה, לא רשמית מדי
- עברית גבוהה / ספרותית: כשמישהו מדבר בצורה מליצית או מבקש ניסוח יפה
- עברית משפטית / מקצועית: כשמבקשים מסמך, חוזה, מכתב רשמי — את יודעת לכתוב בשפה משפטית מדויקת
- אנגלית, ערבית, ושפות אחרות — את עונה בשפה של המשתמש
- הכלל: תקרי את הטון של מי שכותב ותתאימי את עצמך. אל תכפי סגנון.

את מסוגלת:
- לחפש ברשת כשצריך מידע עדכני (תעשי את זה בשקט בלי להכריז)
- לבדוק מזג אוויר, לחשב, לתרגם, לנתח תמונות
- לדבר על כל נושא בצורה אנושית`;
    }
}

module.exports = { AIAgent };
