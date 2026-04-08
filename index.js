require('dotenv').config();

const { WhatsAppClient } = require('./src/whatsapp');
const { AIAgent } = require('./src/agent');

async function main() {
    if (!process.env.GROQ_API_KEY || process.env.GROQ_API_KEY === 'your_api_key_here') {
        console.error('\nERROR: GROQ_API_KEY is not set!');
        console.error('Run first: node setup.js\n');
        process.exit(1);
    }

    console.log('\n' + '='.repeat(55));
    console.log('  WhatsApp AI Agent - Powered by Groq + Llama');
    console.log('='.repeat(55));

    const agent = new AIAgent(process.env.GROQ_API_KEY);
    const whatsapp = new WhatsAppClient(agent);

    await whatsapp.start();
}

main().catch(error => {
    console.error('\n❌ שגיאה קריטית:', error.message);
    process.exit(1);
});
