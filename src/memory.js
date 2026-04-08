/**
 * זיכרון שיחות - שומר היסטוריה לכל צ'אט בנפרד
 */
class ConversationMemory {
    constructor(maxTurns = 15) {
        this.chats = new Map();
        this.maxTurns = maxTurns; // כמה סיבובי שיחה לשמור
    }

    /**
     * מחזיר את היסטוריית השיחה בפורמט Gemini
     */
    getHistory(chatId) {
        return this.chats.get(chatId) || [];
    }

    /**
     * מוסיף סיבוב שיחה לזיכרון
     */
    addMessage(chatId, userText, assistantText) {
        if (!this.chats.has(chatId)) {
            this.chats.set(chatId, []);
        }

        const history = this.chats.get(chatId);

        history.push({
            role: 'user',
            parts: [{ text: userText }]
        });

        history.push({
            role: 'model',
            parts: [{ text: assistantText }]
        });

        // שמור רק את הסיבובים האחרונים
        const maxEntries = this.maxTurns * 2; // כל סיבוב = 2 הודעות
        if (history.length > maxEntries) {
            history.splice(0, history.length - maxEntries);
        }
    }

    /**
     * מוחק את היסטוריית הצ'אט
     */
    clearHistory(chatId) {
        this.chats.delete(chatId);
    }

    /**
     * סטטיסטיקות
     */
    getStats() {
        let totalMessages = 0;
        for (const history of this.chats.values()) {
            totalMessages += history.length;
        }
        return {
            activeChats: this.chats.size,
            totalMessages
        };
    }
}

module.exports = ConversationMemory;
