// Technical indicators: RSI, MACD, EMA, SMA, Bollinger Bands, Volume
// Data source: Yahoo Finance historical + Stockrow fundamentals

// ─── Yahoo Finance crumb (shared singleton via finance_analysis, or standalone) ──
let _techCrumb = null;
let _techCookie = null;
let _techCrumbExpiry = 0;

async function _getTechHeaders() {
    if (_techCrumb && Date.now() < _techCrumbExpiry) {
        return { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Cookie': _techCookie || '' };
    }
    try {
        const r1 = await fetch('https://fc.yahoo.com', {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
            redirect: 'follow', signal: AbortSignal.timeout(6000),
        });
        const rawCookies = r1.headers.get('set-cookie') || '';
        const m = rawCookies.match(/A[13]=([^;]+)/);
        _techCookie = m ? `A3=${m[1]}` : rawCookies.split(';')[0];
        const r2 = await fetch('https://query2.finance.yahoo.com/v1/test/getcrumb', {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Cookie': _techCookie },
            signal: AbortSignal.timeout(6000),
        });
        if (r2.ok) { _techCrumb = (await r2.text()).trim(); _techCrumbExpiry = Date.now() + 30 * 60 * 1000; }
    } catch (_) {}
    return { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Cookie': _techCookie || '' };
}

async function fetchHistoricalCloses(symbol, days = 100) {
    const sym = symbol.toUpperCase();
    const range = days > 252 ? '2y' : '6mo';
    const crumbPart = _techCrumb ? `&crumb=${encodeURIComponent(_techCrumb)}` : '';
    const url = `https://query2.finance.yahoo.com/v8/finance/chart/${sym}?interval=1d&range=${range}${crumbPart}`;

    let res = await fetch(url, { headers: await _getTechHeaders(), signal: AbortSignal.timeout(10000) });
    // Retry once on 401 with fresh crumb
    if (res.status === 401) {
        _techCrumbExpiry = 0;
        const headers = await _getTechHeaders();
        const urlRetry = `https://query2.finance.yahoo.com/v8/finance/chart/${sym}?interval=1d&range=${range}${_techCrumb ? `&crumb=${encodeURIComponent(_techCrumb)}` : ''}`;
        res = await fetch(urlRetry, { headers, signal: AbortSignal.timeout(10000) });
    }

    if (!res.ok) throw new Error(`Yahoo Finance error: ${res.status}`);
    const d = await res.json();
    const result = d?.chart?.result?.[0];
    if (!result) throw new Error('No data');
    const closes = result.indicators?.quote?.[0]?.close || [];
    const volumes = result.indicators?.quote?.[0]?.volume || [];
    const timestamps = result.timestamp || [];
    return { closes: closes.filter(c => c !== null), volumes, timestamps, meta: result.meta };
}

function calcSMA(closes, period) {
    if (closes.length < period) return null;
    const slice = closes.slice(-period);
    return slice.reduce((a, b) => a + b, 0) / period;
}

function calcEMA(closes, period) {
    if (closes.length < period) return null;
    const k = 2 / (period + 1);
    let ema = closes.slice(0, period).reduce((a, b) => a + b, 0) / period;
    for (let i = period; i < closes.length; i++) {
        ema = closes[i] * k + ema * (1 - k);
    }
    return ema;
}

function calcRSI(closes, period = 14) {
    if (closes.length < period + 1) return null;
    const changes = closes.slice(-period - 1 - 10).map((v, i, a) => i > 0 ? a[i] - a[i - 1] : 0).slice(1);
    const gains = changes.map(c => c > 0 ? c : 0);
    const losses = changes.map(c => c < 0 ? -c : 0);
    let avgGain = gains.slice(0, period).reduce((a, b) => a + b) / period;
    let avgLoss = losses.slice(0, period).reduce((a, b) => a + b) / period;
    for (let i = period; i < gains.length; i++) {
        avgGain = (avgGain * (period - 1) + gains[i]) / period;
        avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
    }
    if (avgLoss === 0) return 100;
    const rs = avgGain / avgLoss;
    return 100 - 100 / (1 + rs);
}

function calcMACD(closes) {
    const ema12 = calcEMA(closes, 12);
    const ema26 = calcEMA(closes, 26);
    if (ema12 === null || ema26 === null) return null;
    const macdLine = ema12 - ema26;
    // Signal line = 9-period EMA of MACD values
    // For simplicity, calculate MACD line for last 9+1 points
    const macdValues = [];
    for (let i = Math.max(0, closes.length - 35); i <= closes.length - 26; i++) {
        const slice = closes.slice(0, closes.length - (closes.length - 26 - (i - (closes.length - 35))));
        const e12 = calcEMA(closes.slice(0, closes.length - (closes.length - 12 - i + (closes.length - 35))), 12);
        const e26 = calcEMA(closes.slice(0, closes.length - (closes.length - 26 - i + (closes.length - 35))), 26);
        if (e12 && e26) macdValues.push(e12 - e26);
    }
    const signal = macdValues.length >= 9 ? calcEMA(macdValues, 9) : null;
    const histogram = signal !== null ? macdLine - signal : null;
    return { macd: macdLine, signal, histogram };
}

function calcBollinger(closes, period = 20, multiplier = 2) {
    if (closes.length < period) return null;
    const slice = closes.slice(-period);
    const sma = slice.reduce((a, b) => a + b) / period;
    const variance = slice.reduce((a, b) => a + Math.pow(b - sma, 2), 0) / period;
    const std = Math.sqrt(variance);
    return { upper: sma + multiplier * std, middle: sma, lower: sma - multiplier * std, std };
}

function interpretRSI(rsi) {
    if (rsi >= 70) return `📈 RSI: ${rsi.toFixed(1)} — *קנייה יתר* (אזהרה)`;
    if (rsi <= 30) return `📉 RSI: ${rsi.toFixed(1)} — *מכירה יתר* (הזדמנות?)`;
    if (rsi >= 55) return `📈 RSI: ${rsi.toFixed(1)} — מגמה חיובית`;
    if (rsi <= 45) return `📉 RSI: ${rsi.toFixed(1)} — מגמה שלילית`;
    return `➡️ RSI: ${rsi.toFixed(1)} — ניטרלי`;
}

function interpretMACD(m) {
    if (!m) return null;
    const signal = m.histogram > 0
        ? (m.histogram > Math.abs(m.signal) * 0.1 ? '📈 MACD: אות קנייה (קרוס חיובי)' : '📈 MACD: מגמה חיובית')
        : (Math.abs(m.histogram) > Math.abs(m.signal) * 0.1 ? '📉 MACD: אות מכירה (קרוס שלילי)' : '📉 MACD: מגמה שלילית');
    return `${signal}\n  MACD: ${m.macd.toFixed(3)} | Signal: ${m.signal?.toFixed(3) || 'N/A'} | Hist: ${m.histogram?.toFixed(3) || 'N/A'}`;
}

async function getTechnicalAnalysis(symbol) {
    try {
        const { closes, volumes, meta } = await fetchHistoricalCloses(symbol, 100);
        if (closes.length < 30) return `לא מספיק נתונים לניתוח טכני עבור ${symbol}`;

        const price = closes[closes.length - 1];
        const sma20 = calcSMA(closes, 20);
        const sma50 = calcSMA(closes, 50);
        const ema9 = calcEMA(closes, 9);
        const rsi = calcRSI(closes, 14);
        const macd = calcMACD(closes);
        const bb = calcBollinger(closes, 20);

        const priceVsSMA20 = sma20 ? (price > sma20 ? '📈 מעל' : '📉 מתחת') + ` SMA20 (${sma20.toFixed(2)})` : '';
        const priceVsSMA50 = sma50 ? (price > sma50 ? '📈 מעל' : '📉 מתחת') + ` SMA50 (${sma50.toFixed(2)})` : '';
        const bbStatus = bb ? (price > bb.upper ? '⚠️ מעל הגבול העליון (קנייה יתר)' : price < bb.lower ? '💡 מתחת לגבול התחתון (הזדמנות?)' : `בתוך הבנדז (${((price - bb.lower) / (bb.upper - bb.lower) * 100).toFixed(0)}%)`) : null;

        let output = `📊 ניתוח טכני — ${symbol.toUpperCase()}\n`;
        output += `💰 מחיר נוכחי: ${price.toFixed(2)} ${meta.currency || 'USD'}\n\n`;

        if (priceVsSMA20) output += `${priceVsSMA20}\n`;
        if (priceVsSMA50) output += `${priceVsSMA50}\n`;
        if (ema9) output += `EMA9: ${ema9.toFixed(2)}\n`;
        output += '\n';

        if (rsi !== null) output += `${interpretRSI(rsi)}\n`;
        if (macd) output += `${interpretMACD(macd)}\n`;
        if (bb) {
            output += `\n📐 בולינגר בנדז:\n  עליון: ${bb.upper.toFixed(2)} | אמצע: ${bb.middle.toFixed(2)} | תחתון: ${bb.lower.toFixed(2)}\n`;
            if (bbStatus) output += `  ${bbStatus}\n`;
        }

        // Volume check
        const recentVol = volumes.slice(-5).filter(v => v).reduce((a, b) => a + b, 0) / 5;
        const avgVol = volumes.slice(-20).filter(v => v).reduce((a, b) => a + b, 0) / 20;
        if (recentVol && avgVol) {
            const volRatio = recentVol / avgVol;
            output += `\n📊 נפח: ${volRatio > 1.5 ? '🔥 גבוה מהרגיל' : volRatio < 0.5 ? '🔇 נמוך מהרגיל' : '🔄 רגיל'} (${(volRatio * 100).toFixed(0)}%)`;
        }

        // Overall signal
        let bullish = 0, bearish = 0;
        if (sma20 && price > sma20) bullish++; else bearish++;
        if (sma50 && price > sma50) bullish++; else bearish++;
        if (rsi && rsi < 50) bearish++; else if (rsi) bullish++;
        if (macd?.histogram > 0) bullish++; else if (macd) bearish++;

        const signal = bullish > bearish ? '🟢 אות כולל: שורי (Bullish)' : bullish < bearish ? '🔴 אות כולל: דובי (Bearish)' : '🟡 אות כולל: ניטרלי';
        output += `\n\n${signal}`;
        output += '\n\n⚠️ לידיעה בלבד — לא המלצת השקעה';

        return output;
    } catch (e) {
        return `שגיאה בניתוח טכני של ${symbol}: ${e.message}`;
    }
}

async function getStockrowData(ticker) {
    try {
        const sym = ticker.toUpperCase();
        // Stockrow public financial data endpoints
        const urls = [
            `https://stockrow.com/api/companies/${sym}/financials?ticker=${sym}&dimension=MRQ&type=Q`,
            `https://stockrow.com/api/companies/${sym}/indicators`
        ];

        const results = await Promise.allSettled(urls.map(url =>
            fetch(url, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Referer': `https://stockrow.com/${sym}`
                },
                signal: AbortSignal.timeout(10000)
            }).then(r => r.ok ? r.json() : null)
        ));

        let output = `📈 Stockrow — ${sym}:\n`;
        let found = false;

        for (const r of results) {
            if (r.status === 'fulfilled' && r.value && !r.value.error) {
                const d = r.value;
                // Parse whatever data came back
                if (Array.isArray(d) && d.length > 0) {
                    const item = d[0];
                    const keys = Object.keys(item).slice(0, 8);
                    for (const key of keys) {
                        if (item[key] !== null && item[key] !== undefined) {
                            output += `  ${key}: ${typeof item[key] === 'number' ? item[key].toLocaleString() : item[key]}\n`;
                            found = true;
                        }
                    }
                } else if (typeof d === 'object') {
                    for (const [key, val] of Object.entries(d).slice(0, 10)) {
                        if (val !== null && val !== undefined) {
                            output += `  ${key}: ${typeof val === 'number' ? val.toLocaleString() : val}\n`;
                            found = true;
                        }
                    }
                }
            }
        }

        if (!found) {
            // Fallback: scrape the HTML page for basic data
            return await scrapeStockrow(sym);
        }
        return output;
    } catch (e) {
        return await scrapeStockrow(ticker.toUpperCase());
    }
}

async function scrapeStockrow(sym) {
    try {
        const cookies = process.env.STOCKROW_COOKIES || '';
        const headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        };
        if (cookies) headers['Cookie'] = cookies;

        const res = await fetch(`https://stockrow.com/${sym}`, {
            headers, signal: AbortSignal.timeout(12000)
        });
        if (!res.ok) return `לא ניתן לגשת ל-Stockrow עבור ${sym} (${res.status})`;
        const html = await res.text();

        // Extract key metrics from the page
        const metrics = {};
        const patterns = {
            'P/E': /P\/E[^>]*>\s*([\d.]+)/i,
            'P/S': /P\/S[^>]*>\s*([\d.]+)/i,
            'Market Cap': /Market Cap[^>]*>\s*([^<]+)/i,
            'Revenue': /Revenue[^>]*>\s*([^<]+)/i,
            'EPS': /EPS[^>]*>\s*([\d.-]+)/i,
            'Gross Margin': /Gross Margin[^>]*>\s*([\d.]+%)/i,
        };

        for (const [name, re] of Object.entries(patterns)) {
            const m = html.match(re);
            if (m) metrics[name] = m[1].trim();
        }

        if (Object.keys(metrics).length === 0) {
            return `Stockrow — ${sym}: הגעתי לדף אבל לא הצלחתי לחלץ נתונים. אם יש לך חשבון, הוסף STOCKROW_COOKIES ל-.env`;
        }

        let output = `📊 Stockrow — ${sym}:\n`;
        for (const [key, val] of Object.entries(metrics)) {
            output += `  ${key}: ${val}\n`;
        }
        return output;
    } catch (e) {
        return `שגיאה ב-Stockrow: ${e.message}`;
    }
}

module.exports = { getTechnicalAnalysis, getStockrowData, fetchHistoricalCloses, calcSMA, calcEMA, calcRSI, calcMACD, calcBollinger };
