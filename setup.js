const readline = require('readline');
const fs = require('fs');
const path = require('path');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(question) {
    return new Promise(resolve => rl.question(question, resolve));
}

function line(char = '=', len = 55) {
    console.log(char.repeat(len));
}

async function main() {
    console.clear();
    line();
    console.log('  WhatsApp AI Agent - Setup Wizard');
    line();
    console.log('');

    const nodeVersion = parseInt(process.version.slice(1));
    if (nodeVersion < 18) {
        console.error('ERROR: Node.js version 18+ is required!');
        console.error('Current version: ' + process.version);
        console.error('Download from: https://nodejs.org\n');
        rl.close();
        process.exit(1);
    }

    console.log('Welcome! Let\'s set up your WhatsApp AI bot.');
    console.log('The bot uses Google Gemini - completely FREE!\n');

    line('-');
    console.log('Step 1: Get a FREE Google API Key');
    line('-');
    console.log('');
    console.log('1. Open in browser: https://aistudio.google.com/app/apikey');
    console.log('2. Sign in with your Google account');
    console.log('3. Click "Create API Key"');
    console.log('4. Copy the key (looks like: AIzaSy...)');
    console.log('');

    const apiKey = await ask('Paste your API key here: ');

    if (!apiKey?.trim() || apiKey.trim() === 'your_api_key_here') {
        console.log('\nNo API key entered. Setup cancelled.');
        rl.close();
        return;
    }

    const trimmedKey = apiKey.trim();

    if (!trimmedKey.startsWith('AIza') || trimmedKey.length < 30) {
        console.log('\nWARNING: The key does not look valid. Make sure you copied it correctly.');
        const cont = await ask('Continue anyway? (yes/no): ');
        if (!cont.toLowerCase().startsWith('y')) {
            rl.close();
            return;
        }
    }

    console.log('');
    const botNameInput = await ask('Bot name (press Enter for default "AI Assistant"): ');
    const botName = botNameInput?.trim() || 'AI Assistant';

    console.log('');
    console.log('Should the bot respond in WhatsApp groups?');
    console.log('  no (default) - only private messages');
    console.log('  yes - also in groups (only when tagged)');
    const groupsInput = await ask('Respond in groups? (yes/no, Enter = no): ');
    const respondInGroups = groupsInput?.trim().toLowerCase().startsWith('y');

    const envContent = `# WhatsApp AI Agent Settings
GEMINI_API_KEY=${trimmedKey}
BOT_NAME=${botName}
RESPOND_IN_GROUPS=${respondInGroups}
`;

    const envPath = path.join(process.cwd(), '.env');
    fs.writeFileSync(envPath, envContent, 'utf8');

    console.log('');
    line();
    console.log('  Setup complete!');
    line();
    console.log('');
    console.log('Bot name: ' + botName);
    console.log('Responds in groups: ' + (respondInGroups ? 'Yes' : 'No (private messages only)'));
    console.log('');
    console.log('To start the bot, run:');
    console.log('   npm start');
    console.log('');
    console.log('After starting:');
    console.log('  1. A QR code will appear on screen');
    console.log('  2. Open WhatsApp -> Linked Devices -> Link a Device');
    console.log('  3. Scan the QR code');
    console.log('  4. Send a message to the bot!\n');

    rl.close();
}

main().catch(error => {
    console.error('Error:', error.message);
    rl.close();
    process.exit(1);
});
