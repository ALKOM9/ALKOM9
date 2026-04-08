/**
 * זיכרון שיחות - פורמט OpenAI/Groq
 */
class ConversationMemory {
    constructor(maxTurns = 15) {
        this.chats = new Map();
        this.maxTurns = maxTurns;
    }

    getHistory(chatId) {
        return this.chats.get(chatId) || [];
    }

    addMessage(chatId, userText, assistantText) {
        if (!this.chats.has(chatId)) {
            this.chats.set(chatId, []);
        }
        const history = this.chats.get(chatId);

        // פורמט OpenAI/Groq - content ולא parts
        history.push({ role: 'user', content: userText });
        history.push({ role: 'assistant', content: assistantText });

        // שמור רק את הסיבובים האחרונים
        while (history.length > this.maxTurns * 2) {
            history.splice(0, 2);
        }
    }

    clearHistory(chatId) {
        this.chats.delete(chatId);
    }

    getStats() {
        let totalMessages = 0;
        for (const h of this.chats.values()) totalMessages += h.length;
        return { activeChats: this.chats.size, totalMessages };
    }
}

module.exports = ConversationMemory;
