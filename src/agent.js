const { GoogleGenerativeAI } = require('@google/generative-ai');
const ConversationMemory = require('./memory');
const { searchWeb } = require('./tools/search');
const { getWeather } = require('./tools/weather');

// כלים שהאייג'נט יכול להשתמש בהם
const TOOLS = [{
    functionDeclarations: [
        {
            name: 'search_web',
            description: 'Search the web for current, up-to-date information on any topic. Use this for news, recent events, facts, or anything that might have changed.',
            parameters: {
                type: 'OBJECT',
                properties: {
                    query: {
                        type: 'STRING',
                        description: 'The search query'
                    }
                },
                required: ['query']
            }
        },
        {
            name: 'get_weather',
            description: 'Get current weather conditions for any city in the world',
            parameters: {
                type: 'OBJECT',
                properties: {
                    city: {
                        type: 'STRING',
                        description: 'City name (e.g. "Tel Aviv", "Jerusalem", "New York")'
                    }
                },
                required: ['city']
            }
        },
        {
            name: 'get_datetime',
            description: 'Get the current date and time in Israel',
            parameters: {
                type: 'OBJECT',
                properties: {}
            }
        },
        {
            name: 'calculate',
            description: 'Perform mathematical calculations. Use for any math: percentages, statistics, conversions, etc.',
            parameters: {
                type: 'OBJECT',
                properties: {
                    expression: {
                        type: 'STRING',
                        description: 'Mathematical expression to calculate, e.g. "250 * 1.17" or "(100 + 50) / 3"'
                    }
                },
                required: ['expression']
            }
        }
    ]
}];

class AIAgent {
    constructor(apiKey) {
        this.genAI = new GoogleGenerativeAI(apiKey);
        this.memory = new ConversationMemory();
        this.requestQueue = new Map(); // Rate limiting per chat
    }

    async chat(chatId, userMessage, imageData = null) {
        // Rate limiting: מינימום 1.5 שניות בין בקשות
        await this.throttle(chatId);

        const model = this.genAI.getGenerativeModel({
            model: 'gemini-2.0-flash',
            tools: TOOLS,
            systemInstruction: this.buildSystemPrompt()
        });

        const history = this.memory.getHistory(chatId);

        const chat = model.startChat({ history });

        // בניית חלקי ההודעה
        let messageParts;

        if (imageData) {
            messageParts = [
                {
                    inlineData: {
                        mimeType: imageData.mimeType,
                        data: imageData.data
                    }
                },
                { text: userMessage || 'תאר את התמונה' }
            ];
        } else {
            messageParts = userMessage;
        }

        // שלח הודעה וטפל בקריאות לפונקציות
        let result = await chat.sendMessage(messageParts);
        let response = result.response;

        // לולאת אייג'נט - טפל בקריאות לכלים
        let iterations = 0;
        const MAX_ITERATIONS = 5;

        while (iterations < MAX_ITERATIONS) {
            const calls = response.functionCalls();
            if (!calls || calls.length === 0) break;

            iterations++;
            const functionResponses = [];

            for (const call of calls) {
                console.log(`  🔧 כלי: ${call.name}(${JSON.stringify(call.args)})`);
                const toolResult = await this.runTool(call.name, call.args);
                console.log(`  ✅ תוצאה: ${String(toolResult).slice(0, 120)}`);

                functionResponses.push({
                    functionResponse: {
                        name: call.name,
                        response: { result: toolResult }
                    }
                });
            }

            result = await chat.sendMessage(functionResponses);
            response = result.response;
        }

        // קבל את הטקסט הסופי
        let responseText;
        try {
            responseText = response.text();
        } catch {
            responseText = 'מצטער, לא הצלחתי ליצור תגובה. נסה שוב.';
        }

        if (!responseText?.trim()) {
            responseText = 'מצטער, לא הצלחתי להבין את הבקשה. נסה שוב בניסוח אחר.';
        }

        // שמור בזיכרון
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
                    const expr = args.expression;
                    // מאפשר רק תווים מתמטיים בטוחים
                    const safe = expr.replace(/[^0-9+\-*/().\s%]/g, '');
                    if (!safe.trim()) return 'ביטוי לא תקין';
                    try {
                        // eslint-disable-next-line no-new-func
                        const result = Function('"use strict"; return (' + safe + ')')();
                        if (typeof result !== 'number' || !isFinite(result)) return 'תוצאה לא תקינה';
                        return `${expr} = ${result}`;
                    } catch (e) {
                        return `לא ניתן לחשב: ${e.message}`;
                    }
                }

                default:
                    return `כלי "${name}" לא קיים`;
            }
        } catch (error) {
            console.error(`שגיאה בכלי ${name}:`, error.message);
            return `שגיאה: ${error.message}`;
        }
    }

    async throttle(chatId) {
        const now = Date.now();
        const last = this.requestQueue.get(chatId) || 0;
        const wait = 1500 - (now - last);
        if (wait > 0) {
            await new Promise(r => setTimeout(r, wait));
        }
        this.requestQueue.set(chatId, Date.now());
    }

    clearHistory(chatId) {
        this.memory.clearHistory(chatId);
    }

    getStats() {
        return this.memory.getStats();
    }

    buildSystemPrompt() {
        const botName = process.env.BOT_NAME || 'עוזר AI';
        const now = new Date().toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem' });

        return `אתה ${botName}, עוזר AI חכם ומועיל שמשולב בוואצאפ.
תאריך ושעה עכשוויים: ${now}

היכולות שלך:
- מענה על כל שאלה מתחום הידע הכללי
- חיפוש מידע עדכני ברשת
- בדיקת מזג אוויר בכל עיר בעולם
- ביצוע חישובים מתמטיים
- תרגום בין שפות
- ניתוח ותיאור תמונות
- כתיבה, עריכה, סיכום ויצירה
- עזרה עם בעיות ורעיונות

כללי תגובה:
1. ענה בשפה של המשתמש (עברית/אנגלית/אחרת)
2. היה קצר וברור - ענה ישירות לשאלה
3. אל תשתמש בסימני * # ** לפורמט (וואצאפ לא תומך בMarkdown רגיל)
4. אם לא בטוח במידע עובדתי, השתמש בחיפוש ברשת
5. היה ידידותי, חם ומועיל
6. אפשר להשתמש באמוג'י במידה`;
    }
}

module.exports = { AIAgent };
