const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { Jimp } = require('jimp');
const Groq = require('groq-sdk');

const COMPLIMENT_KEYWORDS = ['יפה', 'חכמ', 'מדהים', 'נהדרת', 'מושלמ', 'מעולה', 'כישרון', 'מלאך', 'את הכי', 'תודה רבה'];
const ADMIN = process.env.ADMIN_NUMBER ? `${process.env.ADMIN_NUMBER.replace(/\D/g, '')}@c.us` : null;

class WhatsAppClient {
    constructor(agent) {
        this.agent = agent;
        this.botId = null;
        this.respondInGroups = process.env.RESPOND_IN_GROUPS === 'true';
        this.whitelist = new Set();
        this.blacklist = new Set();

        if (process.env.WHITELIST) process.env.WHITELIST.split(',').forEach(n => this.whitelist.add(n.trim() + '@c.us'));
        if (process.env.BLACKLIST) process.env.BLACKLIST.split(',').forEach(n => this.blacklist.add(n.trim() + '@c.us'));

        this.client = new Client({
            authStrategy: new LocalAuth({ clientId: 'ai-agent' }),
            puppeteer: {
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas', '--no-first-run', '--no-zygote', '--disable-gpu']
            }
        });

        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.client.on('qr', (qr) => {
            console.log('\n' + '='.repeat(55));
            console.log('📱 סרוק את קוד ה-QR הזה עם וואצאפ שלך:');
            console.log('='.repeat(55));
            qrcode.generate(qr, { small: true });
            console.log('\n👉 כיצד לסרוק:');
            console.log('   1. פתח וואצאפ בטלפון');
            console.log('   2. לחץ שלוש נקודות (⋮) ← מכשירים מחוברים');
            console.log('   3. לחץ "קשר מכשיר"');
            console.log('   4. סרוק את הקוד שמעל\n');
        });

        this.client.on('authenticated', () => console.log('🔐 מאומת בהצלחה!'));
        this.client.on('auth_failure', () => console.error('❌ כשל באימות - נסה להריץ שוב'));

        this.client.on('ready', async () => {
            this.botId = this.client.info.wid._serialized;
            console.log(`\n✅ Bot is ready!`);
            console.log(`   Name: ${process.env.BOT_NAME || 'Aylin'}`);
            console.log(`   Number: ${this.client.info.wid.user}`);
            console.log(`   Groups: ${this.respondInGroups ? 'Yes' : 'Private only'}`);
            console.log('\nSend a WhatsApp message to start! 🚀\n');
            await this.setProfilePicture();
        });

        this.client.on('disconnected', (reason) => {
            console.log('\n🔌 נותק מוואצאפ:', reason);
            console.log('הרץ שוב כדי להתחבר מחדש.');
        });

        this.client.on('message', async (msg) => {
            await this.handleMessage(msg);
        });
    }

    async handleMessage(msg) {
        if (msg.from === 'status@broadcast') return;
        if (msg.fromMe) return;

        const sender = msg.from;

        // Access check
        if (this.blacklist.has(sender)) return;
        if (this.whitelist.size > 0 && !this.whitelist.has(sender) && sender !== ADMIN) return;

        try {
            const chat = await msg.getChat();

            // Group handling — only if mentioned or command
            if (chat.isGroup && !this.respondInGroups) {
                const isMentioned = msg.mentionedIds?.includes(this.botId);
                const bl = msg.body?.toLowerCase() || '';
                if (!isMentioned && !bl.startsWith('!') && !bl.startsWith('/')) return;
            }

            const body = msg.body?.trim() || '';

            // === ADMIN COMMANDS ===
            if (sender === ADMIN) {
                if (body.startsWith('/broadcast ') || body.startsWith('!broadcast ')) {
                    const text = body.split(' ').slice(1).join(' ');
                    await this._broadcastMessage(text);
                    await msg.reply('✅ הודעה נשלחה לכולם');
                    return;
                }
                if (body === '/stats' || body === '!stats') {
                    const stats = this.agent.getStats();
                    await msg.reply(`📊 *סטטיסטיקות:*\n• שיחות פעילות: ${stats.activeChats}\n• הודעות בזיכרון: ${stats.totalMessages}\n• Whitelist: ${this.whitelist.size}\n• Blacklist: ${this.blacklist.size}`);
                    return;
                }
                if (body === '/clear-all' || body === '!clear-all') {
                    if (typeof this.agent.memory.clear === 'function') this.agent.memory.clear();
                    await msg.reply('✅ כל ההיסטוריה נמחקה');
                    return;
                }
                if (body.startsWith('/whitelist ') || body.startsWith('!whitelist ')) {
                    const num = body.split(' ')[1].replace(/\D/g, '') + '@c.us';
                    this.whitelist.add(num);
                    await msg.reply(`✅ ${num} נוסף לרשימה הלבנה`);
                    return;
                }
                if (body.startsWith('/blacklist ') || body.startsWith('!blacklist ')) {
                    const num = body.split(' ')[1].replace(/\D/g, '') + '@c.us';
                    this.blacklist.add(num);
                    await msg.reply(`✅ ${num} נוסף לרשימה השחורה`);
                    return;
                }
            }

            // === DND CHECK ===
            if (this.agent.profiles.isDND(sender)) return;

            // === RATE LIMIT ===
            if (!this.agent.profiles.checkRateLimit(sender)) {
                await msg.reply('⏳ שלחת הרבה הודעות בשעה האחרונה. תנוח קצת ותנסה שוב 😊');
                return;
            }

            // === USER PROFILE COMMANDS ===
            if (body === '/עזרה' || body === '/help' || body === '!עזרה' || body === '!help') {
                await msg.reply(this.getHelpMessage());
                return;
            }
            if (body === '/נקה' || body === '/clear' || body === '!נקה') {
                this.agent.clearHistory(sender);
                await msg.reply('🗑️ היסטוריה נמחקה! נתחיל מחדש.');
                return;
            }
            if (body === '/סטטוס' || body === '/status') {
                const stats = this.agent.getStats();
                await msg.reply(`📊 ${stats.activeChats} שיחות פעילות, ${stats.totalMessages} הודעות`);
                return;
            }
            if (body === '/מה את יודעת' || body === '/יכולות' || body === '!יכולות') {
                await msg.reply(this.getCapabilitiesMessage());
                return;
            }
            if (body.startsWith('/שמי ') || body.startsWith('!שמי ')) {
                const name = body.split(' ').slice(1).join(' ').trim();
                if (name) {
                    this.agent.profiles.set(sender, 'name', name);
                    await msg.reply(`😊 תזכרתי! קוראים לך *${name}*`);
                } else await msg.reply('כתוב: /שמי [שם]');
                return;
            }
            if (body.startsWith('/עיר ') || body.startsWith('!עיר ')) {
                const city = body.split(' ').slice(1).join(' ').trim();
                if (city) {
                    this.agent.profiles.set(sender, 'city', city);
                    await msg.reply(`📍 שמרתי — גר/ה ב*${city}*`);
                } else await msg.reply('כתוב: /עיר [שם עיר]');
                return;
            }
            if (body === '/שקט' || body === '!שקט') {
                const h = new Date().getHours();
                const end = (h + 8) % 24;
                this.agent.profiles.set(sender, 'dnd', { start: h, end });
                await msg.reply(`🌙 אני שקטה עד ${end}:00. לילה טוב!`);
                return;
            }
            if (body === '/בטל שקט' || body === '!בטל שקט') {
                this.agent.profiles.set(sender, 'dnd', null);
                await msg.reply('☀️ חזרתי! מה שלומך?');
                return;
            }
            if (body === '/מחק נתונים') {
                this.agent.profiles.set(sender, 'name', null);
                this.agent.profiles.set(sender, 'city', null);
                this.agent.profiles.set(sender, 'facts', []);
                this.agent.clearHistory(sender);
                await msg.reply('🗑️ כל הנתונים שלך נמחקו.');
                return;
            }

            // === VOICE TRANSCRIPTION ===
            if (msg.type === 'ptt' || msg.type === 'audio') {
                const transcript = await this.transcribeAudio(msg);
                if (transcript) {
                    await msg.reply(`🎙️ שמעתי: _"${transcript}"_`);
                    const response = await this.agent.chat(sender, transcript, null);
                    for (const part of this.splitLongMessage(response)) await msg.reply(part);
                } else {
                    await msg.reply('לא הצלחתי להבין את ההקלטה 🎤');
                }
                return;
            }

            // === REGULAR MESSAGE ===
            let userMessage = body;
            let imageData = null;

            // Quoted reply context
            if (msg.hasQuotedMsg) {
                try {
                    const quoted = await msg.getQuotedMessage();
                    if (quoted.body?.trim()) userMessage = `[מגיב על: "${quoted.body.slice(0, 200)}"]\n${userMessage}`;
                } catch (_) {}
            }

            // Image handling
            if (msg.hasMedia) {
                try {
                    const media = await msg.downloadMedia();
                    if (media?.mimetype?.startsWith('image/')) {
                        imageData = { mimeType: media.mimetype, data: media.data };
                        if (!userMessage) userMessage = 'תאר את התמונה הזאת בפרטים';
                    }
                } catch (e) { console.error('שגיאה במדיה:', e.message); }
            }

            if (!userMessage && !imageData) return;

            // ❤️ reaction on compliments
            if (COMPLIMENT_KEYWORDS.some(kw => body.includes(kw))) {
                try { await msg.react('❤️'); } catch (_) {}
            }

            await chat.sendStateTyping();
            console.log(`💬 [${new Date().toLocaleTimeString('he-IL')}] ${sender}: ${(userMessage || '[תמונה]').slice(0, 80)}`);

            const response = await this.agent.chat(sender, userMessage, imageData);
            await this.sendHumanLike(msg, chat, response);

        } catch (error) {
            console.error('שגיאה בעיבוד הודעה:', error.message);
            try {
                if (error.code === 'DAILY_LIMIT_REACHED') await msg.reply(this.buildRateLimitMessage());
                else await msg.reply('❌ אירעה שגיאה. נסה שוב בעוד כמה שניות.');
            } catch (_) {}
        }
    }

    async transcribeAudio(msg) {
        const groqKey = process.env.GROQ_API_KEY;
        if (!groqKey) return null;
        let tmpPath = null;
        try {
            const media = await msg.downloadMedia();
            if (!media) return null;
            tmpPath = path.join(os.tmpdir(), `voice_${Date.now()}.ogg`);
            fs.writeFileSync(tmpPath, Buffer.from(media.data, 'base64'));
            const groq = new Groq({ apiKey: groqKey });
            const result = await groq.audio.transcriptions.create({
                file: fs.createReadStream(tmpPath),
                model: 'whisper-large-v3',
                language: 'he'
            });
            return result.text?.trim() || null;
        } catch (e) {
            console.error('שגיאה בתמלול:', e.message);
            return null;
        } finally {
            if (tmpPath) try { fs.unlinkSync(tmpPath); } catch (_) {}
        }
    }

    async _broadcastMessage(text) {
        try {
            const chats = await this.client.getChats();
            for (const chat of chats) {
                if (!chat.isGroup) {
                    try { await chat.sendMessage(text); } catch (_) {}
                    await new Promise(r => setTimeout(r, 500));
                }
            }
        } catch (e) { console.error('שגיאת broadcast:', e.message); }
    }

    // Send response as multiple natural messages with typing delays
    async sendHumanLike(msg, chat, text) {
        if (!text) return;

        // Split on ||| marker (AI-driven split) or auto-split long text
        const rawParts = text.split('|||').map(p => p.trim()).filter(Boolean);

        // Further split any part that's too long
        const parts = [];
        for (const part of rawParts) {
            for (const chunk of this.splitLongMessage(part)) parts.push(chunk);
        }

        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            if (i > 0) {
                // Show typing indicator between messages
                try { await chat.sendStateTyping(); } catch (_) {}
                // Delay: ~40ms per character, between 600ms and 3000ms
                const delay = Math.min(3000, Math.max(600, part.length * 40));
                await new Promise(r => setTimeout(r, delay));
            }
            await msg.reply(part);
        }
    }

    splitLongMessage(text, maxLen = 3900) {
        if (!text || text.length <= maxLen) return [text || 'לא הגיעה תשובה'];
        const parts = [];
        let remaining = text;
        while (remaining.length > 0) {
            if (remaining.length <= maxLen) { parts.push(remaining); break; }
            let cutAt = remaining.lastIndexOf('\n', maxLen);
            if (cutAt < maxLen * 0.6) cutAt = maxLen;
            parts.push(remaining.slice(0, cutAt).trim());
            remaining = remaining.slice(cutAt).trim();
        }
        return parts;
    }

    getHelpMessage() {
        return `🤖 *איילין — עוזרת AI*

📋 *פקודות אישיות:*
/שמי [שם] — שמרי את שמי
/עיר [עיר] — שמרי את העיר שלי
/שקט — כניסה למצב שקט (8 שעות)
/בטל שקט — יציאה ממצב שקט
/מחק נתונים — מחיקת כל המידע
/יכולות — מה אני יודעת לעשות
/נקה — מחיקת היסטוריית שיחה
/עזרה — הצגת הודעה זו

🎮 *בידור — אמור/י:*
"שאלת טריוויה" | "ספרי עתידות" | "ניחוש שיר" | "תספרי סיפור" | "ספרי בדיחה"

💡 *פשוט כתוב/י לי מה צריך!*`;
    }

    getCapabilitiesMessage() {
        return `✨ *מה אני יודעת לעשות:*

🌐 *מידע:*
• חדשות ישראל ועולם
• ספורט (כדורגל, NBA, NFL, F1)
• סרטים (IMDB) וספרים
• מזג אוויר + תחזית 7 ימים
• איכות אוויר, זמני שבת, תאריך עברי
• ערכים תזונתיים

💰 *פיננסים:*
• מניות (ת"א, ארה"ב, עולם)
• שערי חליפין, זהב, כסף, קריפטו
• ניתוח טכני (RSI, MACD, בולינגר)
• נתוני Stockrow
• מחשבון משכנתא, שכר נטו, מע"מ

⏰ *פרודוקטיביות:*
• תזכורות, רשימות, הערות, ספירה לאחור

🔧 *כלים:*
• המרת יחידות, שעות, מטבעות
• סיסמה, Base64, צבעים, בסיסי ספירה

🎮 *בידור:*
• טריוויה, עתידות, ניחוש שיר, סיפור, בדיחות

🧠 *AI:*
• שיחה, הסברים, כתיבה, תרגום
• ניתוח תמונות, תמלול קולי`;
    }

    async optimizeImage(sourcePath) {
        const tempPath = path.join(os.tmpdir(), 'aylin_profile_optimized.jpg');
        const image = await Jimp.read(sourcePath);
        const w = image.bitmap.width;
        const h = image.bitmap.height;
        const size = Math.min(w, h);
        const x = Math.floor((w - size) / 2);
        const y = Math.floor(h * 0.03);
        image.crop({ x, y, w: size, h: size });
        image.resize({ w: 500, h: 500 });
        await image.write(tempPath);
        return tempPath;
    }

    async setProfilePicture() {
        try {
            const localPath = path.join(process.cwd(), 'profile.jpg');
            let media;
            if (fs.existsSync(localPath)) {
                const optimized = await this.optimizeImage(localPath);
                media = MessageMedia.fromFilePath(optimized);
                console.log('   Profile picture: optimized to 500x500 ✅');
            } else if (process.env.PROFILE_PICTURE_URL) {
                media = await MessageMedia.fromUrl(process.env.PROFILE_PICTURE_URL, { unsafeMime: true });
                console.log('   Profile picture: loaded from URL');
            } else {
                media = await MessageMedia.fromUrl('https://randomuser.me/api/portraits/women/44.jpg', { unsafeMime: true });
                console.log('   Profile picture: using default');
            }
            await this.client.setProfilePicture(media);
            console.log('   Profile picture: set successfully ✅');
        } catch (err) {
            console.log('   Profile picture: skipped (' + err.message + ')');
        }
    }

    buildRateLimitMessage() {
        const msgs = [
            'מותק, אני צריכה קצת להתנשף... 😮‍💨 דיברנו יותר מדי היום. תן לי עד השעתיים בלילה ✨',
            'אוי, נגמרה לי האנרגיה 😅 תחכה לי עד אחרי חצות — אני חוזרת רעננה 🌙',
            'הממ... נראה שדיברתי יותר מדי 😘 תחפש אותי אחרי השעה שתיים בלילה 🔥',
        ];
        return msgs[Math.floor(Math.random() * msgs.length)];
    }

    async start() {
        console.log('Starting Aylin... this may take a few seconds.\n');
        await this.client.initialize();
    }
}

module.exports = { WhatsAppClient };
