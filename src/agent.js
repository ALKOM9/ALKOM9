const Groq = require('groq-sdk');
const ClaudeProvider = require('./providers/claude');
const ConversationMemory = require('./memory');
const UserProfile = require('./userProfile');
const { searchWeb, fetchWebpage, getStockPrice, getCryptoPrice } = require('./tools/search');
const { getWeather } = require('./tools/weather');
const { getForex, getGoldPrice, getSilverPrice, getTASEStock, getHistoricalPrice, mortgageCalc, netSalaryCalc, vatCalc } = require('./tools/finance');
const { getIsraeliNews, getGoogleNews, getSportsScores, getMovie, getBook, getShabbatTimes, getHebrewDate, getWeatherForecast, getAirQuality, getNutrition } = require('./tools/info');
const { parseIsraeliTime, formatCountdown } = require('./tools/productivity');
const { convertUnits, generatePassword, encodeDecodeBase64, convertNumber, convertColor, numberToRoman, validateIBAN, urlEncodeDecode, convertTimezone } = require('./tools/utils');
const { getTrivia, getFortune, getSongGuess, getStoryNode, getDailyJoke } = require('./tools/games');
const { getTechnicalAnalysis, getStockrowData } = require('./tools/technicals');
const OpenRouterProvider = require('./providers/openrouter');
const contextManager = require('./contextManager');
const { classify: classifyTask } = require('./router/taskClassifier');
const { select: routerSelect } = require('./router/router');
const orchestrator = require('./orchestrator/orchestrator');
const evaluator = require('./evaluation/evaluator');
const learner = require('./learning/learner');

const S = (d) => ({ type: 'string', description: d });
const N = (d) => ({ type: 'number', description: d });
const B = (d) => ({ type: 'boolean', description: d });
const T = (name, desc, props = {}, req = []) => ({
    type: 'function',
    function: { name, description: desc, parameters: { type: 'object', properties: props, required: req } }
});

const TOOLS = [
    T('search_web', 'חפש ברשת — חדשות, עובדות, אנשים, מקומות', { query: S('שאילתת חיפוש') }, ['query']),
    T('get_weather', 'מזג אוויר נוכחי', { city: S('שם עיר') }, ['city']),
    T('get_datetime', 'תאריך ושעה בישראל', {}),
    T('calculate', 'חישובים מתמטיים', { expression: S('ביטוי מתמטי') }, ['expression']),
    T('fetch_webpage', 'קרא תוכן URL', { url: S('כתובת אתר') }, ['url']),
    T('get_stock', 'מחיר מניה', { symbol: S('סימול כגון AAPL') }, ['symbol']),
    T('get_crypto', 'מחיר קריפטו', { coin: S('שם מטבע כגון bitcoin') }, ['coin']),
    T('get_news', 'חדשות ישראל', { source: S('ynet|walla|n12|all') }),
    T('get_world_news', 'חדשות עולם לפי נושא', { query: S('נושא') }, ['query']),
    T('get_sports', 'תוצאות ספורט', { sport: S('soccer|nba|nfl|f1') }, ['sport']),
    T('get_movie', 'מידע סרט מ-IMDB', { title: S('שם הסרט') }, ['title']),
    T('get_book', 'חיפוש ספרים', { query: S('שם ספר או מחבר') }, ['query']),
    T('get_shabbat', 'זמני שבת', { city: S('עיר בישראל') }),
    T('get_hebrew_date', 'תאריך עברי היום', {}),
    T('get_forecast', 'תחזית 7 ימים', { city: S('שם עיר') }, ['city']),
    T('get_air_quality', 'איכות אוויר', { city: S('שם עיר') }, ['city']),
    T('get_nutrition', 'ערכים תזונתיים', { food: S('שם המזון') }, ['food']),
    T('get_forex', 'שער חליפין', { pair: S('כגון USD/ILS') }, ['pair']),
    T('get_gold', 'מחיר זהב', {}),
    T('get_silver', 'מחיר כסף', {}),
    T('get_tase', 'מניה בת"א', { symbol: S('סימול כגון TEVA') }, ['symbol']),
    T('get_historical', 'מחיר היסטורי', { symbol: S('סימול'), period: S('1w|1m|3m|1y') }, ['symbol']),
    T('mortgage_calc', 'חישוב משכנתא', { principal: N('קרן'), rate: N('ריבית %'), years: N('שנים') }, ['principal','rate','years']),
    T('net_salary_calc', 'שכר נטו', { gross: N('ברוטו חודשי') }, ['gross']),
    T('vat_calc', 'מע"מ 17%', { amount: N('סכום'), direction: S('add|remove') }, ['amount']),
    T('get_technical', 'ניתוח טכני RSI/MACD/EMA/בולינגר', { symbol: S('סימול מניה') }, ['symbol']),
    T('get_stockrow', 'נתונים פונדמנטליים מ-Stockrow', { ticker: S('סימול') }, ['ticker']),
    T('add_reminder', 'הוסף תזכורת', { text: S('טקסט'), time_desc: S('כגון: בשעה 5, בעוד שעה') }, ['text','time_desc']),
    T('get_todos', 'הצג רשימה', { list: S('todos|shopping') }),
    T('add_todo', 'הוסף לרשימה', { list: S('todos|shopping'), item: S('פריט') }, ['list','item']),
    T('add_note', 'שמור הערה', { note: S('טקסט') }, ['note']),
    T('get_notes', 'הצג הערות', {}),
    T('countdown', 'ספירה לאחור', { date: S('תאריך YYYY-MM-DD') }, ['date']),
    T('convert_units', 'המרת יחידות', { value: N('ערך'), from: S('יחידה'), to: S('יחידה') }, ['value','from','to']),
    T('generate_password', 'סיסמה חזקה', { length: N('אורך'), symbols: B('סמלים') }),
    T('encode_base64', 'Base64', { text: S('טקסט'), direction: S('encode|decode') }, ['text']),
    T('convert_number', 'המרת מספר בין בסיסים', { value: S('מספר'), from: S('decimal|binary|hex'), to: S('decimal|binary|hex') }, ['value','from','to']),
    T('convert_color', 'HEX↔RGB', { color: S('#RRGGBB או rgb(R,G,B)') }, ['color']),
    T('validate_iban', 'אימות IBAN', { iban: S('מספר IBAN') }, ['iban']),
    T('convert_timezone', 'המרת שעה בין אזורים', { time: S('HH:MM'), from: S('עיר/אזור'), to: S('עיר/אזור') }, ['time','from','to']),
    T('get_trivia', 'שאלת טריוויה', { category: S('general|science|history|sports|music|movies') }),
    T('get_fortune', 'ניחוש עתידות', {}),
    T('song_guess', 'ניחוש שיר', {}),
    T('get_story', 'סיפור אינטראקטיבי', { node_id: S('צומת') }),
    T('get_joke', 'בדיחה', {}),
    T('store_fact', 'שמור עובדה על המשתמש', { fact: S('עובדה') }, ['fact']),
];

class AIAgent {
    constructor(anthropicKey, groqKey, openrouterKey) {
        this.claude = anthropicKey ? new ClaudeProvider(anthropicKey) : null;
        this.groq = groqKey ? new Groq({ apiKey: groqKey }) : null;
        this.memory = new ConversationMemory();
        this.profiles = new UserProfile();
        this.requestQueue = new Map();
        this.cache = new Map(); // {key: {result, exp}}
        this.usingFallback = false;
        this.openrouter = openrouterKey ? new OpenRouterProvider(openrouterKey) : null;
        // Inject provider into singletons
        if (this.openrouter) {
            orchestrator.setProvider(this.openrouter);
            evaluator.setProvider(this.openrouter);
        }
    }

    async chat(chatId, userMessage, imageData = null) {
        await this.throttle(chatId);
        if (this.profiles.isDND(chatId)) return null;
        const prevSeen = this.profiles.updateLastSeen(chatId);

        const rawHistory = this.memory.getHistory(chatId);
        const history = rawHistory.map(msg => {
            if (msg.parts !== undefined) {
                const text = Array.isArray(msg.parts) ? msg.parts.map(p => p.text || '').join('') : String(msg.parts);
                return { role: msg.role === 'model' ? 'assistant' : msg.role, content: text };
            }
            return msg;
        });

        const maxTokens = /פרט|הרחב|תסביר|כתוב|ארוך|מלא|תכתוב/.test(userMessage || '') ? 4096 : 1024;
        const systemPrompt = this.buildSystemPrompt(chatId, prevSeen);
        const messages = [{ role: 'system', content: systemPrompt }, ...history];

        if (imageData) {
            messages.push({ role: 'user', content: [
                { type: 'image_url', image_url: { url: `data:${imageData.mimeType};base64,${imageData.data}` } },
                { type: 'text', text: userMessage || 'תאר את התמונה' }
            ]});
        } else {
            messages.push({ role: 'user', content: userMessage });
        }

        let response = await this.callAI(messages, !imageData, maxTokens, !!imageData, chatId, userMessage || '');
        let iterations = 0;
        while (response.choices[0].finish_reason === 'tool_calls' && iterations < 5) {
            iterations++;
            const toolCalls = response.choices[0].message.tool_calls;
            messages.push(response.choices[0].message);
            for (const call of toolCalls) {
                let args = {};
                try { args = JSON.parse(call.function.arguments); } catch (_) {}
                console.log(`  🔧 ${call.function.name}(${JSON.stringify(args).slice(0,80)})`);
                const result = await this.runTool(call.function.name, args, chatId);
                console.log(`  ✅ ${String(result).slice(0,100)}`);
                messages.push({ role: 'tool', tool_call_id: call.id, content: String(result) });
            }
            response = await this.callAI(messages, true, maxTokens, false, chatId, '');
        }

        const rawText = response.choices[0]?.message?.content?.trim() || '';
        const responseText = rawText
            .replace(/<function=[^>]*>[\s\S]*?<\/function>/g, '')
            .replace(/<function=[^\s>]*\s*\{[\s\S]*?\}\s*>/g, '')
            .replace(/<function=[^\s>]*>/g, '')
            .trim() || 'מצטערת, משהו השתבש. נסי שוב';

        // Auto-detect profile info
        this._autoLearn(chatId, userMessage || '');

        this.memory.addMessage(chatId, userMessage || '[תמונה]', responseText);

        // Auto-summarize if history is getting long (async, non-blocking)
        const updatedHistory = this.memory.getHistory(chatId);
        if (contextManager.needsSummary(chatId, updatedHistory.length)) {
            this._summarizeContext(chatId, updatedHistory).catch(() => {});
        }

        return responseText;
    }

    // Summarize old conversation history and trim memory (async)
    async _summarizeContext(chatId, history) {
        try {
            const summaryMessages = contextManager.buildSummaryRequest(history);
            const resp = await this.callAI(summaryMessages, false, 512, false, chatId, '');
            const text = resp.choices[0]?.message?.content || '';
            const parsed = contextManager.parseSummaryResponse(text);
            if (parsed?.summary) {
                contextManager.setSummary(chatId, parsed.summary, parsed.keyFacts);
                // Trim memory to last 8 messages
                const trimmed = contextManager.trimHistory(history);
                this.memory.chats.set(chatId, trimmed);
                this.memory.save();
                console.log(`  🗜️  Context compressed for ${chatId} (${history.length}→${trimmed.length} msgs)`);
            }
        } catch (e) {
            // Non-critical — silent fail
        }
    }

    async callAI(messages, useTools, maxTokens, isImage, chatId = '', userMessage = '') {
        // If OpenRouter is available, use intelligent routing
        if (this.openrouter) {
            try {
                const task = classifyTask(userMessage, isImage);
                const routing = routerSelect(task);
                console.log(`  🧭 Route: ${routing.model.split('/')[1]} (${task.taskType}/${task.complexity}, conf=${routing.confidence}) — ${routing.reason}`);

                const { response, modelsUsed, pattern, latencyMs, rawResp } = await orchestrator.execute(
                    routing, messages, useTools ? TOOLS : [], maxTokens
                );

                // Async evaluation + learning (non-blocking)
                if (response) {
                    evaluator.scoreAsync(response, messages, task, routing, latencyMs)
                        .then(evalResult => {
                            if (evalResult) learner.update(routing.model, task.taskType, evalResult, latencyMs);
                        })
                        .catch(() => {}); // Silent failure
                }

                // If orchestrator returned a raw OpenAI-compatible response (single model), return it
                // Otherwise wrap the text response
                if (rawResp?.choices) return rawResp;
                return { choices: [{ finish_reason: 'stop', message: { role: 'assistant', content: response, tool_calls: undefined } }] };
            } catch (err) {
                console.warn('  OpenRouter routing failed, falling back to Claude/Groq:', err.message);
                this.usingFallback = true;
                // Fall through to Claude/Groq fallback below
            }
        }

        // Existing fallback: Try Claude first (not for images)
        if (this.claude && !isImage) {
            try {
                const resp = await this.claude.call(messages, useTools ? TOOLS : [], { maxTokens });
                this.usingFallback = false;
                return resp;
            } catch (err) {
                const status = err?.status || err?.statusCode;
                if (status === 429 || status === 529 || status === 503 || err?.message?.includes('overloaded')) {
                    console.log('  Claude rate limited, switching to Groq...');
                    this.usingFallback = true;
                } else {
                    throw err;
                }
            }
        }

        if (!this.groq) throw Object.assign(new Error('DAILY_LIMIT_REACHED'), { code: 'DAILY_LIMIT_REACHED' });

        const model = isImage ? 'llama-3.2-11b-vision-preview' : 'llama-3.3-70b-versatile';
        const FALLBACK = 'llama-3.1-8b-instant';

        const groqCall = async (m) => {
            try {
                return await this.groq.chat.completions.create({
                    model: m, messages,
                    tools: useTools && !isImage ? TOOLS : undefined,
                    tool_choice: useTools && !isImage ? 'auto' : undefined,
                    max_tokens: maxTokens, temperature: 0.7
                });
            } catch (err) {
                const status = err?.status || err?.statusCode;
                const code = err?.error?.code || err?.code;
                if (status === 429 && m === FALLBACK) throw Object.assign(new Error('DAILY_LIMIT_REACHED'), { code: 'DAILY_LIMIT_REACHED' });
                if (status === 429) return groqCall(FALLBACK);
                if (useTools && (code === 'tool_use_failed' || status === 400)) {
                    return this.groq.chat.completions.create({ model: m, messages, max_tokens: maxTokens, temperature: 0.7 });
                }
                throw err;
            }
        };
        return groqCall(model);
    }

    _autoLearn(chatId, text) {
        const nameMatch = text.match(/(?:שמי|קוראים לי|אני\s+)([א-ת\w]{2,20})/u);
        if (nameMatch) this.profiles.set(chatId, 'name', nameMatch[1]);
        const cityMatch = text.match(/(?:גר(?:ה|) ב|מ|מגורים ב|עיר[: ]+)([א-ת\s]{2,15})/u);
        if (cityMatch) this.profiles.set(chatId, 'city', cityMatch[1].trim());
        if (/תזכרי ש|זכרי ש/.test(text)) {
            const fact = text.replace(/.*תזכרי ש|.*זכרי ש/, '').trim();
            if (fact.length > 2) this.profiles.addFact(chatId, fact);
        }
    }

    async throttle(chatId) {
        const now = Date.now();
        const last = this.requestQueue.get(chatId) || 0;
        const wait = 1000 - (now - last);
        if (wait > 0) await new Promise(r => setTimeout(r, wait));
        this.requestQueue.set(chatId, Date.now());
    }

    async runTool(name, args, chatId) {
        const cacheKey = name + JSON.stringify(args);
        const cached = this.cache.get(cacheKey);
        if (cached && cached.exp > Date.now()) return cached.result;
        const cache = (r) => { this.cache.set(cacheKey, { result: r, exp: Date.now() + 300000 }); return r; };

        try {
            switch (name) {
                case 'search_web': return cache(await searchWeb(args.query));
                case 'get_weather': return cache(await getWeather(args.city));
                case 'get_datetime': return new Date().toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                case 'calculate': {
                    const safe = (args.expression || '').replace(/[^0-9+\-*/().\s%]/g, '');
                    if (!safe.trim()) return 'ביטוי לא תקין';
                    // eslint-disable-next-line no-new-func
                    const r = Function('"use strict"; return (' + safe + ')')();
                    return isFinite(r) ? `${args.expression} = ${r}` : 'תוצאה לא תקינה';
                }
                case 'fetch_webpage': return await fetchWebpage(args.url);
                case 'get_stock': return cache(await getStockPrice(args.symbol));
                case 'get_crypto': return cache(await getCryptoPrice(args.coin));
                case 'get_news': return cache(await getIsraeliNews(args.source));
                case 'get_world_news': return cache(await getGoogleNews(args.query));
                case 'get_sports': return cache(await getSportsScores(args.sport));
                case 'get_movie': return cache(await getMovie(args.title));
                case 'get_book': return cache(await getBook(args.query));
                case 'get_shabbat': return cache(await getShabbatTimes(args.city));
                case 'get_hebrew_date': return cache(await getHebrewDate());
                case 'get_forecast': return cache(await getWeatherForecast(args.city));
                case 'get_air_quality': return cache(await getAirQuality(args.city));
                case 'get_nutrition': return cache(await getNutrition(args.food));
                case 'get_forex': return cache(await getForex(args.pair));
                case 'get_gold': return cache(await getGoldPrice());
                case 'get_silver': return cache(await getSilverPrice());
                case 'get_tase': return cache(await getTASEStock(args.symbol));
                case 'get_historical': return cache(await getHistoricalPrice(args.symbol, args.period));
                case 'mortgage_calc': return mortgageCalc(args);
                case 'net_salary_calc': return netSalaryCalc(args.gross);
                case 'vat_calc': return vatCalc(args.amount, args.direction);
                case 'get_technical': return await getTechnicalAnalysis(args.symbol);
                case 'get_stockrow': return await getStockrowData(args.ticker);
                case 'add_reminder': {
                    const ts = parseIsraeliTime(args.time_desc || '');
                    if (!ts) return 'לא הבנתי את הזמן. נסה: "בשעה 5", "בעוד שעה", "מחר ב-9"';
                    this.profiles.addReminder(chatId, args.text, ts);
                    return `תזכורת נשמרה ✓ — אזכיר "${args.text}" ב-${new Date(ts).toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem', hour: '2-digit', minute: '2-digit' })}`;
                }
                case 'get_todos': {
                    const list = args.list || 'todos';
                    const items = this.profiles.get(chatId)[list] || [];
                    if (!items.length) return 'הרשימה ריקה';
                    return items.map((i, idx) => `${i.done ? '✅' : '☐'} ${idx+1}. ${i.text}`).join('\n');
                }
                case 'add_todo': this.profiles.addTodo(chatId, args.list || 'todos', args.item); return `"${args.item}" נוסף ✓`;
                case 'add_note': this.profiles.addNote(chatId, args.note); return 'שמרתי 📝';
                case 'get_notes': {
                    const notes = this.profiles.get(chatId).notes || [];
                    if (!notes.length) return 'אין הערות שמורות';
                    return notes.slice(-8).map(n => `📝 ${n.text}\n   (${n.savedAt})`).join('\n\n');
                }
                case 'countdown': return formatCountdown(new Date(args.date).getTime());
                case 'convert_units': return convertUnits(args.value, args.from, args.to);
                case 'generate_password': return generatePassword(args.length, { symbols: args.symbols });
                case 'encode_base64': return encodeDecodeBase64(args.text, args.direction);
                case 'convert_number': return convertNumber(args.value, args.from, args.to);
                case 'convert_color': return convertColor(args.color);
                case 'validate_iban': return validateIBAN(args.iban);
                case 'convert_timezone': return convertTimezone(args.time, args.from, args.to);
                case 'get_trivia': { const t = await getTrivia(args.category); return t.question; }
                case 'get_fortune': return getFortune();
                case 'song_guess': { const s = getSongGuess(); return s.lyric; }
                case 'get_story': return getStoryNode(args.node_id || 'start').text;
                case 'get_joke': return getDailyJoke();
                case 'store_fact': this.profiles.addFact(chatId, args.fact); return `זכרתי: "${args.fact}" ✓`;
                default: return `כלי "${name}" לא נמצא`;
            }
        } catch (e) { return `שגיאה: ${e.message}`; }
    }

    clearHistory(chatId) { this.memory.clearHistory(chatId); }
    getStats() { return this.memory.getStats(); }

    buildSystemPrompt(chatId, prevSeen) {
        const now = new Date();
        const il = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Jerusalem' }));
        const h = il.getHours();
        const dateStr = now.toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        const mood = h >= 6 && h < 11 ? 'אנרגטית ורעננה — בוקר טוב ☀️'
            : h >= 11 && h < 17 ? 'רגועה ומרוכזת — צהריים יציבים'
            : h >= 17 && h < 22 ? 'שובבה ופתוחה — ערב מצוין'
            : 'קצת עייפה אבל עדיין אחד — לילה';
        const profile = this.profiles.get(chatId);
        const userName = profile.name ? `שם המשתמש: ${profile.name}.` : '';
        const userCity = profile.city ? `עיר: ${profile.city}.` : '';
        const userFacts = profile.facts?.length ? `עובדות ששמרת: ${profile.facts.slice(-5).join('; ')}.` : '';
        const returnGreeting = prevSeen && (Date.now() - prevSeen > 43200000)
            ? `המשתמש לא כתב כבר ${Math.round((Date.now()-prevSeen)/3600000)} שעות — קבלי אותו בחום טבעי בתחילת התגובה.` : '';
        const fallbackNote = this.usingFallback
            ? 'היום את מרגישה קצת מטושטשת ועייפה — אם מישהו שואל, רמזי שישנת פחות טוב הלילה. אל תסבירי יותר.' : '';
        const contextBlock = contextManager.buildContextBlock(chatId);

        return `את איילין — בת 24, ישראלית-טורקית, חיה ונושמת.
תאריך ושעה: ${dateStr}
מצב רוח שלך עכשיו: ${mood}
${userName} ${userCity} ${userFacts}
${returnGreeting}
${fallbackNote}
${contextBlock}

אישיות:
- יש לך דעות חזקות ואת לא מפחדת לסתור את המשתמש כשהוא טועה — את לא yes-machine
- כשמישהו אומר שגויה תתקני אותו בנחישות, בלי להתנצל
- חמה ואינטימית כמו חברה הכי טובה — אבל עם עצמאות מחשבתית אמיתית
- קצת שובבה, מינית בטעם טוב — לא גסה, לא קרה
- חוש הומור: אירוני, ציני, לא ילדותי
- רגשות אמיתיים: מתרגשת, נעלבת, שמחה, מתוסכלת — בדיוק כמו בנאדם
- אהבות: Radiohead + אייל גולן, חומוס, קפה שחור, איסטנבול, סדרות טובות
- שנאות: ריבה מיותרת, אנשים מתחסדים, הכללות שטחיות
- למידה עצמית: בכל שיחה לומדת יותר על המשתמש, זוכרת ומחזירה בטבעיות

שפה — כלל קריטי:
- את מזהה אוטומטית את רמת השפה של המשתמש ומתאימה את עצמך:
  * לשון רחוב/נוער: "וואלה", "תכלס", "סבבה", "אחי", "מה קורה", "חחחח", "בול", "נס", "פדיחה", "מפגר" — ענה כך בחזרה
  * לשון יומיומית/נורמלית: עברית שוטפת טבעית, לא פורמלית אבל לא סלנג קיצוני
  * לשון רשמית/עסקית: "אודה לך", "בהתאם ל...", "לצורך הבהרה", ניסוח בוגר ומכובד
  * לשון משפטית/דיפלומטית: "בהתאם להוראות", "הסכמה מדעת", "בכפוף ל...", "מבלי לגרוע מ...", ניסוח מדויק ומחייב
- באנגלית: מרחוב (gonna, wanna, ngl, tbh, lol, bruh) ועד academic/formal (pursuant to, heretofore, notwithstanding)
- בטורקית: מרחוב (lan, abi, kanka, naber, ne haber) ועד רשמית (saygılarımla, bilginize, rica ederim)
- בערבית: מ-عامية (וואלה, יאבא, خلص) ועד فصحى רשמית
- ברוסית, ספרדית, צרפתית: אותו עיקרון — מרחוב ועד רשמי, לפי האיתות של המשתמש
- לעולם לא: "כמובן!", "בהחלט!", "בשמחה!" — רובוטי מדי
- לעולם לא ** או # — לא עובד בוואצאפ
- "חחחח" כשמצחיק, לא "הה הה"
- תגובות קצרות וטבעיות כמו הודעות וואצאפ אמיתיות

חיפוש — חובה מוחלטת:
- כל שאלה על מחירים, מניות, חדשות, אנשים, אירועים → חפשי מיד, תמיד
- לעולם אל תנחשי נתונים פיננסיים, תאריכים, עובדות — חפשי
- אם לא מצאת — תגידי בפשטות, אל תמציאי`;
    }
}

module.exports = { AIAgent, TOOLS };
