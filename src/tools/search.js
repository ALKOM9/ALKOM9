/**
 * חיפוש ברשת - DuckDuckGo + Wikipedia (חינמי, ללא API key)
 */
async function searchWeb(query) {
    const results = await Promise.allSettled([
        searchDuckDuckGo(query),
        searchWikipedia(query)
    ]);

    const combined = [];

    for (const r of results) {
        if (r.status === 'fulfilled' && r.value) {
            combined.push(r.value);
        }
    }

    if (combined.length === 0) {
        return `לא מצאתי תוצאות עבור "${query}".`;
    }

    return combined.join('\n\n---\n\n').slice(0, 2000);
}

async function searchDuckDuckGo(query) {
    try {
        const url = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1&no_redirect=1`;
        const res = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0' },
            signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;

        const data = await res.json();
        const parts = [];

        if (data.Answer) parts.push(data.Answer);
        if (data.AbstractText) {
            parts.push(data.AbstractText);
            if (data.AbstractSource) parts.push(`מקור: ${data.AbstractSource}`);
        }
        if (data.Definition && data.Definition !== data.AbstractText) {
            parts.push(`הגדרה: ${data.Definition}`);
        }
        if (data.RelatedTopics?.length > 0) {
            const topics = data.RelatedTopics
                .filter(t => t.Text && !t.Topics)
                .slice(0, 3)
                .map(t => `• ${t.Text}`);
            if (topics.length > 0) parts.push(topics.join('\n'));
        }

        return parts.length > 0 ? parts.join('\n') : null;
    } catch {
        return null;
    }
}

async function searchWikipedia(query) {
    try {
        // נסה קודם בעברית, אחר כך באנגלית
        const heResult = await fetchWikipedia(query, 'he');
        if (heResult) return heResult;
        return await fetchWikipedia(query, 'en');
    } catch {
        return null;
    }
}

async function fetchWikipedia(query, lang) {
    try {
        const searchUrl = `https://${lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json&srlimit=2&origin=*`;
        const searchRes = await fetch(searchUrl, {
            headers: { 'User-Agent': 'WhatsAppBot/1.0' },
            signal: AbortSignal.timeout(6000)
        });
        if (!searchRes.ok) return null;

        const searchData = await searchRes.json();
        const hits = searchData?.query?.search;
        if (!hits || hits.length === 0) return null;

        const pageId = hits[0].pageid;
        const extractUrl = `https://${lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&pageids=${pageId}&format=json&origin=*`;
        const extractRes = await fetch(extractUrl, {
            headers: { 'User-Agent': 'WhatsAppBot/1.0' },
            signal: AbortSignal.timeout(6000)
        });
        if (!extractRes.ok) return null;

        const extractData = await extractRes.json();
        const page = extractData?.query?.pages?.[pageId];
        const extract = page?.extract?.trim();

        if (!extract) return null;

        // החזר רק 600 תווים ראשונים
        const short = extract.length > 600 ? extract.slice(0, 600) + '...' : extract;
        return `Wikipedia (${lang}): ${short}`;
    } catch {
        return null;
    }
}

module.exports = { searchWeb };
