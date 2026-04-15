#!/usr/bin/env node
// setup.js — first-time setup and health check for Aylin bot
const { execSync } = require('child_process');
const fs = require('fs');

console.log('\n' + '='.repeat(50));
console.log('  Aylin WhatsApp AI — Setup');
console.log('='.repeat(50) + '\n');

let ok = true;

console.log('Installing dependencies...');
try { execSync('npm install', { stdio: 'inherit' }); console.log('  Dependencies installed\n'); }
catch (e) { console.error('  npm install failed\n'); ok = false; }

for (const d of ['data', 'data/logs']) {
    if (!fs.existsSync(d)) { fs.mkdirSync(d, { recursive: true }); console.log(`  Created ${d}/`); }
}

if (!fs.existsSync('.env')) {
    if (fs.existsSync('.env.example')) {
        fs.copyFileSync('.env.example', '.env');
        console.log('\n.env created from .env.example');
        console.log('  Open .env and fill in your API keys!\n');
    }
    ok = false;
} else { console.log('\n.env exists'); }

require('dotenv').config();
const hasAnthropic = process.env.ANTHROPIC_API_KEY && !process.env.ANTHROPIC_API_KEY.includes('...');
const hasGroq = process.env.GROQ_API_KEY && !['your_api_key_here','your_groq_key_here'].includes(process.env.GROQ_API_KEY);

if (hasAnthropic) console.log('  ANTHROPIC_API_KEY set (Claude)');
if (hasGroq) console.log('  GROQ_API_KEY set (Groq)');
if (!hasAnthropic && !hasGroq) { console.log('  No API keys set!'); ok = false; }

const required = [
    'src/agent.js','src/whatsapp.js','src/memory.js','src/userProfile.js',
    'src/providers/claude.js','src/tools/search.js','src/tools/weather.js',
    'src/tools/finance.js','src/tools/info.js','src/tools/productivity.js',
    'src/tools/utils.js','src/tools/games.js','src/tools/technicals.js'
];
console.log('\nChecking files:');
for (const f of required) {
    if (fs.existsSync(f)) console.log(`  OK  ${f}`);
    else { console.log(`  MISSING  ${f}`); ok = false; }
}

console.log('\n' + '='.repeat(50));
console.log(ok ? '\nAll good! Run: node index.js\n' : '\nFix the issues above, then run: node index.js\n');
