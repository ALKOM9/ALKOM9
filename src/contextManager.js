// Context Manager — auto-summarizes long conversations to preserve context
// Saves summaries to data/summaries.json
// Injected into buildSystemPrompt so Aylin always "remembers" past sessions

const fs = require('fs');
const path = require('path');

const SUMMARIES_FILE = path.join(process.cwd(), 'data', 'summaries.json');
const SUMMARIZE_THRESHOLD = 16; // Summarize when history exceeds this many messages
const MAX_SUMMARY_AGE_DAYS = 30; // Drop summaries older than this

class ContextManager {
    constructor() {
        this.summaries = {}; // { chatId: { summary, keyFacts[], updatedAt, turnCount } }
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(SUMMARIES_FILE)) {
                this.summaries = JSON.parse(fs.readFileSync(SUMMARIES_FILE, 'utf8'));
                this._pruneOld();
            }
        } catch (e) {
            this.summaries = {};
        }
    }

    save() {
        try {
            const dir = path.dirname(SUMMARIES_FILE);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(SUMMARIES_FILE, JSON.stringify(this.summaries, null, 2));
        } catch (e) {
            console.error('ContextManager save error:', e.message);
        }
    }

    // Returns true if this chat needs summarization
    needsSummary(chatId, historyLength) {
        return historyLength >= SUMMARIZE_THRESHOLD;
    }

    // Store a generated summary for a chat
    setSummary(chatId, summary, keyFacts = []) {
        this.summaries[chatId] = {
            summary,
            keyFacts,
            updatedAt: new Date().toISOString(),
            turnCount: (this.summaries[chatId]?.turnCount || 0) + 1,
        };
        this.save();
    }

    // Get the current summary for a chat (for system prompt injection)
    getSummary(chatId) {
        return this.summaries[chatId] || null;
    }

    // Build a summary prompt to send to the AI
    buildSummaryRequest(history) {
        const turns = [];
        for (let i = 0; i < history.length; i += 2) {
            const user = history[i]?.content || '';
            const bot = history[i + 1]?.content || '';
            turns.push(`User: ${String(user).slice(0, 200)}\nBot: ${String(bot).slice(0, 200)}`);
        }
        const dialogue = turns.slice(0, -4).join('\n\n'); // Summarize all but last 4 turns

        return [
            {
                role: 'user',
                content: `Summarize this conversation in 3-5 sentences IN HEBREW. Focus on: what topics were discussed, what the user asked for, important facts mentioned. Also extract up to 5 key facts about the user (name, city, preferences, etc.) as a JSON array.

Format your response as JSON:
{"summary":"...","keyFacts":["fact1","fact2"]}

Conversation to summarize:
${dialogue}`
            }
        ];
    }

    // Parse the AI's summary response
    parseSummaryResponse(text) {
        try {
            const match = text.match(/\{[\s\S]*\}/);
            if (!match) return null;
            const parsed = JSON.parse(match[0]);
            return {
                summary: parsed.summary || '',
                keyFacts: Array.isArray(parsed.keyFacts) ? parsed.keyFacts.slice(0, 5) : [],
            };
        } catch (e) {
            // Fallback: treat the whole text as a summary
            return { summary: text.slice(0, 500), keyFacts: [] };
        }
    }

    // Build the context injection string for system prompt
    buildContextBlock(chatId) {
        const entry = this.summaries[chatId];
        if (!entry || !entry.summary) return '';

        let block = `\n--- זיכרון שיחות קודמות ---\n${entry.summary}`;
        if (entry.keyFacts?.length) {
            block += `\nעובדות מפתח שנלמדו: ${entry.keyFacts.join(' | ')}`;
        }
        block += '\n---';
        return block;
    }

    // Get messages to keep in active history (last N turns, rest is summarized)
    trimHistory(history) {
        if (history.length < SUMMARIZE_THRESHOLD) return history;
        // Keep last 8 messages (4 turns) in active context
        return history.slice(-8);
    }

    // Remove summaries older than MAX_SUMMARY_AGE_DAYS
    _pruneOld() {
        const cutoff = Date.now() - MAX_SUMMARY_AGE_DAYS * 86400000;
        for (const [chatId, entry] of Object.entries(this.summaries)) {
            if (new Date(entry.updatedAt).getTime() < cutoff) {
                delete this.summaries[chatId];
            }
        }
    }
}

module.exports = new ContextManager(); // Singleton
