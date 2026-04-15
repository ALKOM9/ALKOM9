const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');
const PROFILES_FILE = path.join(DATA_DIR, 'profiles.json');

class UserProfile {
    constructor() {
        this.profiles = new Map();
        this.load();
    }

    load() {
        try {
            if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
            if (fs.existsSync(PROFILES_FILE)) {
                const data = JSON.parse(fs.readFileSync(PROFILES_FILE, 'utf8'));
                for (const [id, profile] of Object.entries(data)) {
                    this.profiles.set(id, profile);
                }
                console.log(`   Profiles: loaded ${this.profiles.size} user profiles`);
            }
        } catch (err) {
            console.log('   Profiles: starting fresh (' + err.message + ')');
        }
    }

    save() {
        try {
            if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
            const data = {};
            for (const [id, profile] of this.profiles.entries()) {
                data[id] = profile;
            }
            fs.writeFileSync(PROFILES_FILE, JSON.stringify(data, null, 2), 'utf8');
        } catch (err) {
            console.error('Profiles save error:', err.message);
        }
    }

    get(chatId) {
        if (!this.profiles.has(chatId)) {
            this.profiles.set(chatId, {
                name: null,
                nickname: null,
                city: null,
                language: null,
                interests: [],
                facts: [],
                todos: [],
                shopping: [],
                notes: [],
                reminders: [],
                habits: {},
                dnd: null,
                safeMode: false,
                personalityMode: 'friend',
                lastSeen: null,
                messageCount: 0,
                rateLimit: { count: 0, resetAt: 0 },
                storyState: null,
                triviaState: null,
                songGuessState: null,
                cryptoPortfolio: []
            });
        }
        return this.profiles.get(chatId);
    }

    set(chatId, key, value) {
        const profile = this.get(chatId);
        profile[key] = value;
        this.save();
    }

    addFact(chatId, fact) {
        const profile = this.get(chatId);
        if (!profile.facts) profile.facts = [];
        if (!profile.facts.includes(fact)) {
            profile.facts.push(fact);
            if (profile.facts.length > 50) profile.facts.shift();
        }
        this.save();
    }

    addTodo(chatId, list, item) {
        const profile = this.get(chatId);
        if (!profile[list]) profile[list] = [];
        profile[list].push({ text: item, done: false, addedAt: Date.now() });
        this.save();
    }

    completeTodo(chatId, list, index) {
        const profile = this.get(chatId);
        if (profile[list] && profile[list][index]) {
            profile[list][index].done = true;
            this.save();
            return true;
        }
        return false;
    }

    removeTodo(chatId, list, index) {
        const profile = this.get(chatId);
        if (profile[list] && profile[list][index] !== undefined) {
            profile[list].splice(index, 1);
            this.save();
            return true;
        }
        return false;
    }

    addNote(chatId, note) {
        const profile = this.get(chatId);
        if (!profile.notes) profile.notes = [];
        profile.notes.push({ text: note, savedAt: new Date().toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem' }) });
        if (profile.notes.length > 100) profile.notes.shift();
        this.save();
    }

    addReminder(chatId, text, timestamp) {
        const profile = this.get(chatId);
        if (!profile.reminders) profile.reminders = [];
        profile.reminders.push({ text, timestamp, sent: false });
        this.save();
    }

    getAllPendingReminders() {
        const pending = [];
        const now = Date.now();
        for (const [chatId, profile] of this.profiles.entries()) {
            if (!profile.reminders) continue;
            for (const r of profile.reminders) {
                if (!r.sent && r.timestamp <= now) {
                    pending.push({ chatId, ...r });
                }
            }
        }
        return pending;
    }

    markReminderSent(chatId, timestamp) {
        const profile = this.get(chatId);
        if (!profile.reminders) return;
        for (const r of profile.reminders) {
            if (r.timestamp === timestamp) r.sent = true;
        }
        this.save();
    }

    isDND(chatId) {
        const profile = this.get(chatId);
        if (!profile.dnd) return false;
        const now = new Date();
        const israelTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Jerusalem' }));
        const [sh, sm] = profile.dnd.start.split(':').map(Number);
        const [eh, em] = profile.dnd.end.split(':').map(Number);
        const cur = israelTime.getHours() * 60 + israelTime.getMinutes();
        const start = sh * 60 + sm;
        const end = eh * 60 + em;
        if (start <= end) return cur >= start && cur < end;
        return cur >= start || cur < end;
    }

    updateLastSeen(chatId) {
        const profile = this.get(chatId);
        const prev = profile.lastSeen;
        profile.lastSeen = Date.now();
        profile.messageCount = (profile.messageCount || 0) + 1;
        this.save();
        return prev;
    }

    checkRateLimit(chatId) {
        const profile = this.get(chatId);
        const now = Date.now();
        if (!profile.rateLimit || profile.rateLimit.resetAt < now) {
            profile.rateLimit = { count: 1, resetAt: now + 3600000 };
            this.save();
            return true;
        }
        if (profile.rateLimit.count >= 60) return false;
        profile.rateLimit.count++;
        this.save();
        return true;
    }

    getAll() {
        return this.profiles;
    }
}

module.exports = UserProfile;
