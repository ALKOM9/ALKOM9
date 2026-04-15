require('dotenv').config();

const { WhatsAppClient } = require('./src/whatsapp');
const { AIAgent } = require('./src/agent');

const ADMIN = process.env.ADMIN_NUMBER ? `${process.env.ADMIN_NUMBER.replace(/\D/g, '')}@c.us` : null;

async function main() {
    const anthropicKey = process.env.ANTHROPIC_API_KEY;
    const groqKey = process.env.GROQ_API_KEY;

    if (!anthropicKey && (!groqKey || groqKey === 'your_api_key_here')) {
        console.error('\nERROR: No API keys found!');
        console.error('Set ANTHROPIC_API_KEY or GROQ_API_KEY in .env\n');
        process.exit(1);
    }

    console.log('\n' + '='.repeat(55));
    console.log('  Aylin WhatsApp AI — Powered by Claude + Groq');
    console.log('='.repeat(55));
    if (anthropicKey) console.log('  Primary AI: Claude (Anthropic)');
    else console.log('  Primary AI: Groq (fallback only mode)');
    console.log('='.repeat(55) + '\n');

    const agent = new AIAgent(anthropicKey, groqKey);
    const whatsapp = new WhatsAppClient(agent);

    // Reminder worker — check every 60 seconds
    setInterval(async () => {
        try {
            const pending = agent.profiles.getAllPendingReminders();
            for (const { chatId, reminder } of pending) {
                try {
                    await whatsapp.client.sendMessage(chatId, `⏰ תזכורת: ${reminder.text}`);
                    agent.profiles.markReminderSent(chatId, reminder.id);
                } catch (e) {
                    console.error('שגיאה בשליחת תזכורת:', e.message);
                }
            }
        } catch (e) {
            console.error('שגיאה בworker תזכורות:', e.message);
        }
    }, 60_000);

    // Health monitoring — check every 5 minutes
    let lastHealthCheck = Date.now();
    setInterval(async () => {
        try {
            const state = await whatsapp.client.getState();
            if (state !== 'CONNECTED') {
                console.warn(`⚠️ WhatsApp state: ${state}`);
                if (ADMIN) {
                    try {
                        await whatsapp.client.sendMessage(ADMIN, `⚠️ Aylin Bot Alert: מצב חיבור = ${state}`);
                    } catch (_) {}
                }
            }
            lastHealthCheck = Date.now();
        } catch (e) {
            console.error('שגיאת health check:', e.message);
        }
    }, 5 * 60_000);

    // Start dashboard if enabled
    if (process.env.DASHBOARD_ENABLED === 'true') {
        try {
            const { startDashboard } = require('./src/dashboard/server');
            startDashboard(whatsapp.client, agent);
        } catch (e) {
            console.warn('Dashboard not started:', e.message);
        }
    }

    await whatsapp.start();
}

main().catch(error => {
    console.error('\n❌ שגיאה קריטית:', error.message);
    process.exit(1);
});
