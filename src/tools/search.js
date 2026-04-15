// Multi-source search: DuckDuckGo + Wikipedia + Yahoo Finance + CoinGecko + URL fetch

async function searchWeb(query) {
    const lower = query.toLowerCase();
    const tasks = [searchDuckDuckGoLite(query), searchWikipedia(query)];

    const symMatch = query.match(/\b[A-Z]{2,5}\b/);
    if (symMatch && /stock|share|ticker|nasdaq|nyse|מניה|מניות/i.test(query)) {
        tasks.push(getStockPrice(symMatch[0]));
    }

    if (/bitcoin|btc|eth|ethereum|crypto|קריפטו|ביטקוין|אתריום|solana|doge|xrp|bnb/i.test(lower)) {
        tasks.push(getCryptoPrice(lower));
    }

    const results = await Promise.allSettled(tasks);
    const combined = results.filter(r => r.status === 'fulfilled' && r.value).map(r => r.value);
    if (combined.length === 0) return `לא מצאתי תוצאות עבור "${query}".`;
    return combined.join('\n\n---\n\n').slice(0, 3000);
}

async function searchDuckDuckGoLite(query) {
    try {
        const url = `https://lite.duckduckgo.com/lite/?q=${encodeURIComponent(query)}&kl=il-he`;
        const res = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
            signal: AbortSignal.timeout(9000)
        });
        if (!res.ok) return searchDuckDuckGoInstant(query);
        const html = await res.text();
        const snippets = [];
        const snippetRe = /<td[^>]*class="result-snippet"[^>]*>([\s\S]*?)<\/td>/g;
        const titleRe = /<a[^>]*class="result-link"[^>]*>([\s\S]*?)<\/a>/g;
        const titles = [];
        let m;
        while ((m = titleRe.exec(html)) !== null && titles.length < 6)
            titles.push(m[1].replace(/<[^>]+>/g, '').trim());
        let i = 0;
        while ((m = snippetRe.exec(html)) !== null && snippets.length < 5) {
            const snip = m[1].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
            if (snip.length > 20) { snippets.push((titles[i] ? titles[i] + '\n' : '') + snip); i++; }
        }
        if (snippets.length === 0) return searchDuckDuckGoInstant(query);
        return 'תוצאות:\n' + snippets.join('\n\n');
    } catch { return searchDuckDuckGoInstant(query); }
}

async function searchDuckDuckGoInstant(query) {
    try {
        const res = await fetch(`https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`, {
            headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        const parts = [];
        if (d.Answer) parts.push(d.Answer);
        if (d.AbstractText) { parts.push(d.AbstractText); if (d.AbstractSource) parts.push('מקור: ' + d.AbstractSource); }
        if (d.Definition && d.Definition !== d.AbstractText) parts.push('הגדרה: ' + d.Definition);
        if (d.RelatedTopics?.length) {
            const t = d.RelatedTopics.filter(t => t.Text && !t.Topics).slice(0, 4).map(t => '• ' + t.Text);
            if (t.length) parts.push(t.join('\n'));
        }
        return parts.length ? parts.join('\n') : null;
    } catch { return null; }
}

async function searchWikipedia(query) {
    try {
        return (await fetchWikipedia(query, 'he')) || (await fetchWikipedia(query, 'en'));
    } catch { return null; }
}

async function fetchWikipedia(query, lang) {
    try {
        const s = await fetch(`https://${lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json&srlimit=2&origin=*`,
            { headers: { 'User-Agent': 'WhatsAppBot/1.0' }, signal: AbortSignal.timeout(6000) });
        if (!s.ok) return null;
        const sd = await s.json();
        const hits = sd?.query?.search;
        if (!hits?.length) return null;
        const pid = hits[0].pageid;
        const e = await fetch(`https://${lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&pageids=${pid}&format=json&origin=*`,
            { headers: { 'User-Agent': 'WhatsAppBot/1.0' }, signal: AbortSignal.timeout(6000) });
        if (!e.ok) return null;
        const ed = await e.json();
        const extract = ed?.query?.pages?.[pid]?.extract?.trim();
        if (!extract) return null;
        return `Wikipedia (${lang}):\n` + (extract.length > 800 ? extract.slice(0, 800) + '...' : extract);
    } catch { return null; }
}

async function getStockPrice(symbol) {
    try {
        const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol.toUpperCase()}?interval=1d&range=1d`,
            { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000) });
        if (!res.ok) return null;
        const d = await res.json();
        const meta = d?.chart?.result?.[0]?.meta;
        if (!meta) return null;
        const price = meta.regularMarketPrice;
        const prev = meta.chartPreviousClose;
        const chg = price && prev ? ((price - prev) / prev * 100).toFixed(2) : null;
        const cur = meta.currency || 'USD';
        let r = `${symbol.toUpperCase()}: ${price} ${cur}`;
        if (chg !== null) r += ` (${chg > 0 ? '+' : ''}${chg}%)`;
        if (meta.regularMarketDayHigh) r += `\nגבוה: ${meta.regularMarketDayHigh} | נמוך: ${meta.regularMarketDayLow}`;
        return r;
    } catch { return null; }
}

async function getCryptoPrice(query) {
    try {
        const map = { bitcoin:'bitcoin',btc:'bitcoin',ethereum:'ethereum',eth:'ethereum',
            solana:'solana',sol:'solana',bnb:'binancecoin',xrp:'ripple',
            cardano:'cardano',ada:'cardano',dogecoin:'dogecoin',doge:'dogecoin' };
        const words = query.match(/\b\w+\b/g) || [];
        const id = words.map(w => map[w]).find(Boolean);
        if (!id) return null;
        const res = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${id}&vs_currencies=usd,ils&include_24hr_change=true`,
            { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000) });
        if (!res.ok) return null;
        const d = await res.json();
        const c = d[id];
        if (!c) return null;
        const chg = c.usd_24h_change?.toFixed(2);
        return `${id}: $${c.usd?.toLocaleString()} (${chg > 0 ? '+' : ''}${chg}% 24h)\n₪${c.ils?.toLocaleString() || 'N/A'}`;
    } catch { return null; }
}

async function fetchWebpage(url) {
    try {
        const res = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
            signal: AbortSignal.timeout(10000)
        });
        if (!res.ok) return `HTTP ${res.status}`;
        const html = await res.text();
        const text = html
            .replace(/<script[\s\S]*?<\/script>/gi, '')
            .replace(/<style[\s\S]*?<\/style>/gi, '')
            .replace(/<[^>]+>/g, ' ')
            .replace(/\s{3,}/g, '\n')
            .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim();
        return text.length > 3000 ? text.slice(0, 3000) + '...' : text;
    } catch (e) { return `Error: ${e.message}`; }
}

module.exports = { searchWeb, fetchWebpage, getStockPrice, getCryptoPrice };
