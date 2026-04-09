const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');
const MEMORY_FILE = path.join(DATA_DIR, 'memory.json');

class ConversationMemory {
    constructor(maxTurns = 60) {
        this.chats = new Map();
        this.maxTurns = maxTurns;
        this.load();
    }

    load() {
        try {
            if (!fs.existsSync(DATA_DIR)) {
                fs.mkdirSync(DATA_DIR, { recursive: true });
            }
            if (fs.existsSync(MEMORY_FILE)) {
                const data = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
                for (const [chatId, history] of Object.entries(data)) {
                    this.chats.set(chatId, history);
                }
                console.log(`   Memory: loaded ${this.chats.size} conversations from disk`);
            }
        } catch (err) {
            console.log('   Memory: starting fresh (' + err.message + ')');
        }
    }

    save() {
        try {
            if (!fs.existsSync(DATA_DIR)) {
                fs.mkdirSync(DATA_DIR, { recursive: true });
            }
            const data = {};
            for (const [chatId, history] of this.chats.entries()) {
                data[chatId] = history;
            }
            fs.writeFileSync(MEMORY_FILE, JSON.stringify(data), 'utf8');
        } catch (err) {
            console.error('Memory save error:', err.message);
        }
    }

    getHistory(chatId) {
        return this.chats.get(chatId) || [];
    }

    addMessage(chatId, userText, assistantText) {
        if (!this.chats.has(chatId)) {
            this.chats.set(chatId, []);
        }
        const history = this.chats.get(chatId);
        history.push({ role: 'user', content: userText });
        history.push({ role: 'assistant', content: assistantText });
        while (history.length > this.maxTurns * 2) {
            history.splice(0, 2);
        }
        this.save();
    }

    clearHistory(chatId) {
        this.chats.delete(chatId);
        this.save();
    }

    getStats() {
        let totalMessages = 0;
        for (const h of this.chats.values()) totalMessages += h.length;
        return { activeChats: this.chats.size, totalMessages };
    }
}

module.exports = ConversationMemory;
