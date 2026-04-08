const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

class WhatsAppClient {
    constructor(agent) {
        this.agent = agent;
        this.botId = null;
        this.respondInGroups = process.env.RESPOND_IN_GROUPS === 'true';

        this.client = new Client({
            authStrategy: new LocalAuth({ clientId: 'ai-agent' }),
            puppeteer: {
                headless: true,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
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

        this.client.on('authenticated', () => {
            console.log('🔐 מאומת בהצלחה!');
        });

        this.client.on('auth_failure', () => {
            console.error('❌ כשל באימות - נסה להריץ שוב');
        });

        this.client.on('ready', () => {
            this.botId = this.client.info.wid._serialized;
            const botName = process.env.BOT_NAME || 'עוזר AI';
            console.log('\n✅ האייג\'נט מוכן ועובד!');
            console.log(`💬 שם: ${botName}`);
            console.log(`📱 מספר: ${this.client.info.wid.user}`);
            if (this.respondInGroups) {
                console.log('👥 מגיב: בשיחות פרטיות + קבוצות');
            } else {
                console.log('💬 מגיב: בשיחות פרטיות בלבד');
            }
            console.log('\nשלח הודעה בוואצאפ כדי להתחיל! 🚀\n');
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
        // התעלם מהודעות סטטוס ומהודעות ששלח הבוט עצמו
        if (msg.from === 'status@broadcast') return;
        if (msg.fromMe) return;

        try {
            const chat = await msg.getChat();

            // בדיקת קבוצה
            if (chat.isGroup && !this.respondInGroups) {
                // בקבוצות - ענה רק אם תויגת
                const isMentioned = msg.mentionedIds?.includes(this.botId);
                const bodyLower = msg.body?.toLowerCase() || '';
                const startsWithTrigger = bodyLower.startsWith('!') || bodyLower.startsWith('/');

                if (!isMentioned && !startsWithTrigger) return;
            }

            // פקודות מיוחדות
            const body = msg.body?.trim() || '';

            if (body === '/עזרה' || body === '/help' || body === '!עזרה' || body === '!help') {
                await msg.reply(this.getHelpMessage());
                return;
            }

            if (body === '/נקה' || body === '/clear' || body === '!נקה' || body === '!clear') {
                this.agent.clearHistory(msg.from);
                await msg.reply('🗑️ היסטוריית השיחה נמחקה! נתחיל מחדש.');
                return;
            }

            if (body === '/סטטוס' || body === '/status') {
                const stats = this.agent.getStats();
                await msg.reply(`📊 סטטוס:\nשיחות פעילות: ${stats.activeChats}\nהודעות בזיכרון: ${stats.totalMessages}`);
                return;
            }

            // עיבוד הודעה רגילה
            let userMessage = body;
            let imageData = null;

            // טיפול בתמונות
            if (msg.hasMedia) {
                try {
                    const media = await msg.downloadMedia();
                    if (media && media.mimetype?.startsWith('image/')) {
                        imageData = {
                            mimeType: media.mimetype,
                            data: media.data
                        };
                        if (!userMessage) {
                            userMessage = 'תאר את התמונה הזאת בפרטים';
                        }
                    }
                } catch (mediaError) {
                    console.error('שגיאה בהורדת מדיה:', mediaError.message);
                }
            }

            if (!userMessage && !imageData) return;

            // הראה אינדיקטור הקלדה
            await chat.sendStateTyping();

            console.log(`💬 [${new Date().toLocaleTimeString('he-IL')}] ${msg.from}: ${userMessage?.slice(0, 80) || '[תמונה]'}`);

            // שלח לאייג'נט AI
            const response = await this.agent.chat(msg.from, userMessage, imageData);

            // פצל הודעות ארוכות (מגבלת וואצאפ ~4096 תווים)
            const parts = this.splitLongMessage(response);
            for (const part of parts) {
                await msg.reply(part);
            }

        } catch (error) {
            console.error('שגיאה בעיבוד הודעה:', error.message);
            try {
                await msg.reply('❌ אירעה שגיאה. נסה שוב בעוד כמה שניות.');
            } catch (_) { /* התעלם */ }
        }
    }

    splitLongMessage(text, maxLen = 3900) {
        if (!text || text.length <= maxLen) return [text || 'לא הגיעה תשובה'];

        const parts = [];
        let remaining = text;

        while (remaining.length > 0) {
            if (remaining.length <= maxLen) {
                parts.push(remaining);
                break;
            }

            // נסה לחתוך בסוף שורה
            let cutAt = maxLen;
            const lastNewline = remaining.lastIndexOf('\n', maxLen);
            if (lastNewline > maxLen * 0.6) {
                cutAt = lastNewline;
            }

            parts.push(remaining.slice(0, cutAt).trim());
            remaining = remaining.slice(cutAt).trim();
        }

        return parts;
    }

    getHelpMessage() {
        const botName = process.env.BOT_NAME || 'עוזר AI';
        return `🤖 ${botName} - עוזר AI חכם

מה אני יכול לעשות?
- לענות על כל שאלה
- לחפש מידע עדכני ברשת
- לבדוק מזג אוויר בכל עיר
- לבצע חישובים מתמטיים
- לתרגם בין שפות
- לנתח ולתאר תמונות (שלח לי תמונה!)
- לכתוב, לערוך ולסכם טקסטים
- לעזור עם כל שאלה!

פקודות:
/עזרה - הצג הודעה זו
/נקה - מחק היסטוריית שיחה
/סטטוס - מידע על הבוט

פשוט כתוב לי מה אתה צריך!`;
    }

    async start() {
        console.log('⏳ מאתחל... זה עשוי לקחת כמה שניות.\n');
        await this.client.initialize();
    }
}

module.exports = { WhatsAppClient };
