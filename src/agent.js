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

        const history = this.memory.getHistory(chatId);
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
            ? 'llama-3.2-11b-vision-preview'   // מודל ויז'ן לתמונות
            : 'llama-3.3-70b-versatile';        // מודל רגיל לטקסט

        // שלח לגרוק ועבד קריאות לכלים
        let response = await this.groq.chat.completions.create({
            model,
            messages,
            tools: imageData ? undefined : TOOLS, // כלים רק במצב טקסט
            tool_choice: imageData ? undefined : 'auto',
            max_tokens: 2048,
            temperature: 0.7
        });

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
            response = await this.groq.chat.completions.create({
                model: 'llama-3.3-70b-versatile',
                messages,
                tools: TOOLS,
                tool_choice: 'auto',
                max_tokens: 2048,
                temperature: 0.7
            });
        }

        const responseText = response.choices[0]?.message?.content?.trim()
            || 'מצטער, לא הצלחתי ליצור תגובה. נסה שוב.';

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
        const botName = process.env.BOT_NAME || 'AI Assistant';
        const now = new Date().toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem' });
        return `אתה ${botName}, עוזר AI חכם ומועיל שמשולב בוואצאפ.
תאריך ושעה: ${now}

יכולות: מענה על שאלות, חיפוש ברשת, מזג אוויר, חישובים, תרגום, ניתוח תמונות, כתיבה ועריכה.

כללים:
1. ענה בשפה של המשתמש (עברית/אנגלית/אחרת)
2. היה קצר וברור
3. אל תשתמש בסימני Markdown כמו ** או # (וואצאפ לא תומך בהם)
4. אם לא בטוח - חפש ברשת
5. היה ידידותי ומועיל, אפשר להשתמש באמוג'י`;
    }
}

module.exports = { AIAgent };
