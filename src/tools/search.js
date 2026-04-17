// Multi-source search: DuckDuckGo + Google News + Wikipedia + Finance + URL fetch
// Enhanced with source reliability scoring and deep cross-reference search

// ─── Source Reliability ────────────────────────────────────────────────────────

const RELIABLE_DOMAINS = new Set([
    // Global news
    'reuters.com','apnews.com','bbc.com','bbc.co.uk','theguardian.com',
    'nytimes.com','wsj.com','bloomberg.com','ft.com','economist.com',
    'npr.org','pbs.org','washingtonpost.com','time.com','newsweek.com',
    // Israeli news
    'haaretz.com','ynetnews.com','ynet.co.il','jpost.com','timesofisrael.com',
    'calcalist.co.il','themarker.com','walla.co.il','n12.co.il','kan.org.il',
    'mako.co.il','ice.co.il','globes.co.il',
    // Government & official
    'gov.il','moh.gov.il','who.int','cdc.gov','nih.gov','fda.gov',
    'un.org','nato.int','imf.org','worldbank.org',
    // Academic & science
    'wikipedia.org','britannica.com','pubmed.ncbi.nlm.nih.gov',
    'nature.com','science.org','arxiv.org',
    // Finance & data
    'finance.yahoo.com','investing.com','marketwatch.com',
    'coinmarketcap.com','coingecko.com',
    // Tech
    'techcrunch.com','wired.com','theverge.com','arstechnica.com',
    'stackoverflow.com','github.com','developer.mozilla.org',
]);

const QUESTIONABLE_DOMAINS = new Set([
    'rt.com','sputniknews.com','infowars.com','naturalnews.com',
    'thegatewaypundit.com','beforeitsnews.com','zerohedge.com',
    'globalresearch.ca','veteranstoday.com',
]);

function getDomain(url) {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return ''; }
}

function reliabilityScore(url) {
    const domain = getDomain(url);
    if (!domain) return { score: 5, label: '❓ לא ידוע' };
    if (RELIABLE_DOMAINS.has(domain))      return { score: 9, label: '✅ אמין' };
    if (QUESTIONABLE_DOMAINS.has(domain))  return { score: 2, label: '⚠️ מפוקפק' };
    if (domain.endsWith('.gov') || domain.endsWith('.gov.il') ||
        domain.endsWith('.ac.il') || domain.endsWith('.edu'))
        return { score: 8, label: '🔵 כנראה אמין' };
    if (domain.endsWith('.org'))           return { score: 6, label: '🔵 ארגון' };
    return { score: 5, label: '❓ לא מאומת' };
}

// ─── Basic Search (quick) ─────────────────────────────────────────────────────

// Finance/investment queries that should NOT go to Wikipedia
const FINANCE_QUERY_PATTERNS = /best stock|stocks to (buy|invest|watch)|stock (pick|recommend)|invest in|entry.?point|exit.?point|מניה.{0,15}(לקנות|להשקיע|מומלצת|טובה)|איזו מניה|המלצת מניה|לקנות מניה|השקעה במניה/i;

async function searchWeb(query) {
    const lower = query.toLowerCase();
    const isFinanceQuery = FINANCE_QUERY_PATTERNS.test(query);

    // For investment/stock-pick queries, skip Wikipedia (irrelevant) — use DDG only
    const tasks = isFinanceQuery
        ? [searchDuckDuckGoLite(query)]
        : [searchDuckDuckGoLite(query), searchWikipedia(query)];

    const symMatch = query.match(/\b[A-Z]{2,5}\b/);
    if (symMatch && /stock|share|ticker|nasdaq|nyse|מניה|מניות/i.test(query))
        tasks.push(getStockPrice(symMatch[0]));

    if (/bitcoin|btc|eth|ethereum|crypto|קריפטו|ביטקוין|אתריום|solana|doge|xrp|bnb/i.test(lower))
        tasks.push(getCryptoPrice(lower));

    const results = await Promise.allSettled(tasks);
    const combined = results.filter(r => r.status === 'fulfilled' && r.value).map(r => r.value);
    if (combined.length === 0) return `לא מצאתי תוצאות עבור "${query}".`;
    return combined.join('\n\n---\n\n').slice(0, 3000);
}

// ─── Deep Search (multi-source + reliability) ─────────────────────────────────

async function deepSearch(query) {
    // Parallel: DDG with URLs, Wikipedia, Google News
    const [ddgRes, wikiRes, newsRes] = await Promise.allSettled([
        searchDuckDuckGoWithURLs(query),
        searchWikipedia(query),
        searchGoogleNews(query),
    ]);

    const ddg  = ddgRes.status  === 'fulfilled' ? ddgRes.value  : { text: null, urls: [] };
    const wiki = wikiRes.status === 'fulfilled' ? wikiRes.value : null;
    const news = newsRes.status === 'fulfilled' ? newsRes.value : null;

    // Fetch top 2 result pages in parallel
    const topURLs = ddg.urls.slice(0, 2);
    const fetchedPages = await Promise.allSettled(
        topURLs.map(({ url, title }) =>
            fetchWebpage(url, 1200).then(text => ({
                url, title, text, reliability: reliabilityScore(url)
            }))
        )
    );

    // Build reliability-tagged report
    const sections = [];
    const pageContents = [];

    if (wiki) sections.push(`📖 Wikipedia (✅ אמין):\n${wiki.replace(/^Wikipedia \(\w+\):\n/, '')}`);
    if (news) sections.push(`📰 חדשות עדכניות:\n${news}`);
    if (ddg.text) sections.push(`🔍 חיפוש:\n${ddg.text}`);

    for (const p of fetchedPages) {
        if (p.status !== 'fulfilled') continue;
        const { url, title, text, reliability } = p.value;
        if (!text || text.startsWith('Error') || text.startsWith('HTTP')) continue;
        pageContents.push({ url, title, text: text.slice(0, 1000), reliability });
        sections.push(`🌐 ${title || getDomain(url)} [${reliability.label}]:\n${text.slice(0, 1000)}`);
    }

    const contradictionNote = detectContradictions(pageContents);
    if (contradictionNote) sections.push(`⚠️ שים לב — מקורות לא מסכימים:\n${contradictionNote}`);

    if (sections.length === 0) return `לא מצאתי תוצאות עבור "${query}".`;
    return `🔎 חיפוש מעמיק: "${query}"\n\n${sections.join('\n\n---\n\n').slice(0, 4500)}`;
}

function detectContradictions(pages) {
    if (pages.length < 2) return null;
    const numberSets = pages.map(p => {
        const nums = [...(p.text.matchAll(/\b(\d[\d,]*\.?\d*)\b/g))].map(m => parseFloat(m[1].replace(/,/g,'')));
        return nums.filter(n => n > 100);
    });
    const contradictions = [];
    for (let i = 0; i < pages.length - 1 && contradictions.length < 2; i++) {
        for (const n of numberSets[i]) {
            const hasClose = numberSets[i+1].some(m => Math.abs(m - n) / (n || 1) < 0.2);
            if (!hasClose && numberSets[i+1].length > 0) {
                contradictions.push(`${pages[i].reliability.label} ו-${pages[i+1].reliability.label} מציינים ערכים שונים`);
                break;
            }
        }
    }
    return contradictions.length ? contradictions.join('\n') : null;
}

// ─── DuckDuckGo ───────────────────────────────────────────────────────────────

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
        const titleRe   = /<a[^>]*class="result-link"[^>]*>([\s\S]*?)<\/a>/g;
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

async function searchDuckDuckGoWithURLs(query) {
    try {
        const res = await fetch(
            `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`,
            { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000) }
        );
        if (!res.ok) return { text: null, urls: [] };
        const d = await res.json();
        const parts = [];
        const urls  = [];

        if (d.Answer) parts.push(d.Answer);
        if (d.AbstractText) {
            parts.push(d.AbstractText);
            if (d.AbstractURL) urls.push({ url: d.AbstractURL, title: d.AbstractSource });
            if (d.AbstractSource) parts.push('מקור: ' + d.AbstractSource);
        }
        if (d.RelatedTopics?.length) {
            d.RelatedTopics.filter(t => t.Text && !t.Topics).slice(0, 5).forEach(t => {
                const rel = t.FirstURL ? reliabilityScore(t.FirstURL) : { label: '' };
                parts.push(`• ${t.Text}${rel.label ? ' [' + rel.label + ']' : ''}`);
                if (t.FirstURL) urls.push({ url: t.FirstURL, title: t.Text.slice(0, 60) });
            });
        }
        if (d.Results?.length) {
            d.Results.forEach(r => {
                if (r.FirstURL) urls.push({ url: r.FirstURL, title: r.Text?.slice(0, 60) });
            });
        }
        return { text: parts.length ? parts.join('\n') : null, urls };
    } catch { return { text: null, urls: [] }; }
}

async function searchDuckDuckGoInstant(query) {
    const result = await searchDuckDuckGoWithURLs(query);
    return result.text;
}

// ─── Google News RSS ──────────────────────────────────────────────────────────

async function searchGoogleNews(query) {
    try {
        const url = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}&hl=iw&gl=IL&ceid=IL:iw`;
        const res = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(8000)
        });
        if (!res.ok) return null;
        const xml  = await res.text();
        const items = [];
        const itemRe = /<item>([\s\S]*?)<\/item>/g;
        let m;
        while ((m = itemRe.exec(xml)) !== null && items.length < 5) {
            const item   = m[1];
            const titleM = item.match(/<title><!\[CDATA\[(.*?)\]\]><\/title>/) || item.match(/<title>(.*?)<\/title>/);
            const sourceM = item.match(/<source[^>]*>(.*?)<\/source>/);
            const linkM   = item.match(/<link>(.*?)<\/link>/);
            const dateM   = item.match(/<pubDate>(.*?)<\/pubDate>/);
            if (!titleM) continue;
            const title  = titleM[1].trim();
            const source = sourceM?.[1]?.trim() || '';
            const link   = linkM?.[1]?.trim() || '';
            const date   = dateM?.[1]?.trim()?.slice(5, 16) || '';
            const rel    = link ? reliabilityScore(link) : { label: '' };
            items.push(`• ${title} — ${source}${rel.label ? ' ' + rel.label : ''}${date ? ' (' + date + ')' : ''}`);
        }
        return items.length ? items.join('\n') : null;
    } catch { return null; }
}

// ─── Wikipedia ────────────────────────────────────────────────────────────────

async function searchWikipedia(query) {
    try {
        return (await fetchWikipedia(query, 'he')) || (await fetchWikipedia(query, 'en'));
    } catch { return null; }
}

async function fetchWikipedia(query, lang) {
    try {
        const s = await fetch(
            `https://${lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json&srlimit=2&origin=*`,
            { headers: { 'User-Agent': 'WhatsAppBot/1.0' }, signal: AbortSignal.timeout(6000) }
        );
        if (!s.ok) return null;
        const sd   = await s.json();
        const hits = sd?.query?.search;
        if (!hits?.length) return null;
        const pid = hits[0].pageid;
        const e = await fetch(
            `https://${lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&pageids=${pid}&format=json&origin=*`,
            { headers: { 'User-Agent': 'WhatsAppBot/1.0' }, signal: AbortSignal.timeout(6000) }
        );
        if (!e.ok) return null;
        const ed = await e.json();
        const extract = ed?.query?.pages?.[pid]?.extract?.trim();
        if (!extract) return null;
        return `Wikipedia (${lang}):\n` + (extract.length > 800 ? extract.slice(0, 800) + '...' : extract);
    } catch { return null; }
}

// ─── Finance ──────────────────────────────────────────────────────────────────

async function getStockPrice(symbol) {
    try {
        const res = await fetch(
            `https://query1.finance.yahoo.com/v8/finance/chart/${symbol.toUpperCase()}?interval=1d&range=1d`,
            { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000) }
        );
        if (!res.ok) return null;
        const d    = await res.json();
        const meta = d?.chart?.result?.[0]?.meta;
        if (!meta) return null;
        const price = meta.regularMarketPrice;
        const prev  = meta.chartPreviousClose;
        const chg   = price && prev ? ((price - prev) / prev * 100).toFixed(2) : null;
        const cur   = meta.currency || 'USD';
        let r = `${symbol.toUpperCase()}: ${price} ${cur}`;
        if (chg !== null) r += ` (${chg > 0 ? '+' : ''}${chg}%)`;
        if (meta.regularMarketDayHigh) r += `\nגבוה: ${meta.regularMarketDayHigh} | נמוך: ${meta.regularMarketDayLow}`;
        return r;
    } catch { return null; }
}

async function getCryptoPrice(query) {
    try {
        const map = {
            bitcoin:'bitcoin',btc:'bitcoin',ethereum:'ethereum',eth:'ethereum',
            solana:'solana',sol:'solana',bnb:'binancecoin',xrp:'ripple',
            cardano:'cardano',ada:'cardano',dogecoin:'dogecoin',doge:'dogecoin'
        };
        const words = query.match(/\b\w+\b/g) || [];
        const id = words.map(w => map[w]).find(Boolean);
        if (!id) return null;
        const res = await fetch(
            `https://api.coingecko.com/api/v3/simple/price?ids=${id}&vs_currencies=usd,ils&include_24hr_change=true`,
            { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000) }
        );
        if (!res.ok) return null;
        const d = await res.json();
        const c = d[id];
        if (!c) return null;
        const chg = c.usd_24h_change?.toFixed(2);
        return `${id}: $${c.usd?.toLocaleString()} (${chg > 0 ? '+' : ''}${chg}% 24h)\n₪${c.ils?.toLocaleString() || 'N/A'}`;
    } catch { return null; }
}

// ─── Web Fetch ────────────────────────────────────────────────────────────────

async function fetchWebpage(url, maxChars = 3000) {
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
            .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim();
        return text.length > maxChars ? text.slice(0, maxChars) + '...' : text;
    } catch (e) { return `Error: ${e.message}`; }
}

module.exports = { searchWeb, deepSearch, fetchWebpage, getStockPrice, getCryptoPrice, reliabilityScore };
