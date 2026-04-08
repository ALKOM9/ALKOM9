require('dotenv').config();

const { WhatsAppClient } = require('./src/whatsapp');
const { AIAgent } = require('./src/agent');

async function main() {
    if (!process.env.GEMINI_API_KEY || process.env.GEMINI_API_KEY === 'your_api_key_here') {
        console.error('\n❌ שגיאה: לא הוגדר מפתח API!');
        console.error('הרץ תחילה: node setup.js');
        console.error('או עדכן את קובץ .env עם מפתח ה-API שלך\n');
        process.exit(1);
    }

    console.log('\n' + '='.repeat(55));
    console.log('🤖 אייג\'נט AI לוואצאפ - מופעל על ידי Google Gemini');
    console.log('='.repeat(55));

    const agent = new AIAgent(process.env.GEMINI_API_KEY);
    const whatsapp = new WhatsAppClient(agent);

    await whatsapp.start();
}

main().catch(error => {
    console.error('\n❌ שגיאה קריטית:', error.message);
    process.exit(1);
});
