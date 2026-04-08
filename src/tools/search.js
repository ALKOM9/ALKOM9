/**
 * חיפוש ברשת - משתמש ב-DuckDuckGo (חינמי, ללא מפתח API)
 */
async function searchWeb(query) {
    try {
        // DuckDuckGo Instant Answer API - חינמי וללא API key
        const url = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1&no_redirect=1`;

        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (compatible; WhatsAppBot/1.0; +https://github.com/ai-agent)'
            },
            signal: AbortSignal.timeout(8000) // 8 שניות timeout
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const results = [];

        // תשובה מיידית (חישובים, עובדות)
        if (data.Answer) {
            results.push(`תשובה: ${data.Answer}`);
        }

        // תיאור ראשי
        if (data.AbstractText) {
            results.push(data.AbstractText);
            if (data.AbstractSource) {
                results.push(`(מקור: ${data.AbstractSource})`);
            }
        }

        // הגדרה
        if (data.Definition && data.Definition !== data.AbstractText) {
            results.push(`הגדרה: ${data.Definition}`);
        }

        // נושאים קשורים
        if (data.RelatedTopics?.length > 0) {
            const relevant = data.RelatedTopics
                .filter(t => t.Text && !t.Topics) // רק פריטים עם טקסט ישיר
                .slice(0, 4)
                .map(t => `• ${t.Text}`);

            if (relevant.length > 0) {
                if (results.length > 0) results.push('');
                results.push('מידע נוסף:');
                results.push(...relevant);
            }
        }

        if (results.length === 0) {
            return `לא נמצא מידע ישיר עבור "${query}". ייתכן שמדובר בנושא עדכני מאוד או ספציפי מדי.`;
        }

        return results.join('\n');

    } catch (error) {
        if (error.name === 'TimeoutError') {
            return 'החיפוש לקח יותר מדי זמן. נסה שוב.';
        }
        console.error('שגיאת חיפוש:', error.message);
        return `לא הצלחתי לחפש עכשיו (${error.message}). תוכל לנסות שוב?`;
    }
}

module.exports = { searchWeb };
