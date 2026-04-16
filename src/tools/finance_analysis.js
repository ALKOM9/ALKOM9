// finance_analysis.js — 75+ analysis tools: technical, fundamental, macro, multi-timeframe
// Data sources: Yahoo Finance (free), World Bank API (free), Yahoo Finance special tickers

const { fetchHistoricalCloses, calcSMA, calcEMA, calcRSI, calcMACD, calcBollinger } = require('./technicals');

const YF_HEADERS = { 'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json' };
const TIMEOUT = 12000;

// ─── Yahoo Finance helpers ────────────────────────────────────────────────────

async function yf(sym, modules) {
    const url = `https://query1.finance.yahoo.com/v10/finance/quoteSummary/${encodeURIComponent(sym)}?modules=${modules}`;
    const res = await fetch(url, { headers: YF_HEADERS, signal: AbortSignal.timeout(TIMEOUT) });
    if (!res.ok) throw new Error(`YF ${res.status}`);
    const d = await res.json();
    return d?.quoteSummary?.result?.[0] || null;
}

async function yfPrice(sym, interval = '1d', range = '6mo') {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?interval=${interval}&range=${range}`;
    const res = await fetch(url, { headers: YF_HEADERS, signal: AbortSignal.timeout(TIMEOUT) });
    if (!res.ok) throw new Error(`YF chart ${res.status}`);
    const d = await res.json();
    const r = d?.chart?.result?.[0];
    if (!r) throw new Error('No chart data');
    return r;
}

async function yfQuote(sym) {
    const r = await yfPrice(sym, '1d', '5d');
    return r?.meta;
}

function fmtNum(n, dec = 2) { return n != null ? (+n).toFixed(dec) : 'N/A'; }
function fmtPct(n) { return n != null ? `${n > 0 ? '+' : ''}${(+n * 100).toFixed(2)}%` : 'N/A'; }
function fmtB(n) {
    if (n == null) return 'N/A';
    if (Math.abs(n) >= 1e12) return `$${(n/1e12).toFixed(2)}T`;
    if (Math.abs(n) >= 1e9)  return `$${(n/1e9).toFixed(2)}B`;
    if (Math.abs(n) >= 1e6)  return `$${(n/1e6).toFixed(2)}M`;
    return `$${n.toLocaleString()}`;
}

// ─── TECHNICAL INDICATORS ─────────────────────────────────────────────────────

function calcStochastic(highs, lows, closes, kPeriod = 14, dPeriod = 3) {
    if (closes.length < kPeriod) return null;
    const kValues = [];
    for (let i = kPeriod - 1; i < closes.length; i++) {
        const hh = Math.max(...highs.slice(i - kPeriod + 1, i + 1));
        const ll = Math.min(...lows.slice(i - kPeriod + 1, i + 1));
        kValues.push(hh === ll ? 50 : ((closes[i] - ll) / (hh - ll)) * 100);
    }
    const k = kValues[kValues.length - 1];
    const d = kValues.slice(-dPeriod).reduce((a, b) => a + b) / dPeriod;
    return { k, d };
}

function calcATR(highs, lows, closes, period = 14) {
    if (closes.length < period + 1) return null;
    const trs = [];
    for (let i = 1; i < closes.length; i++) {
        trs.push(Math.max(highs[i] - lows[i], Math.abs(highs[i] - closes[i-1]), Math.abs(lows[i] - closes[i-1])));
    }
    return trs.slice(-period).reduce((a, b) => a + b) / period;
}

function calcADX(highs, lows, closes, period = 14) {
    if (closes.length < period * 2) return null;
    const diPlus = [], diMinus = [], tr = [];
    for (let i = 1; i < closes.length; i++) {
        const upMove = highs[i] - highs[i-1];
        const downMove = lows[i-1] - lows[i];
        diPlus.push(upMove > downMove && upMove > 0 ? upMove : 0);
        diMinus.push(downMove > upMove && downMove > 0 ? downMove : 0);
        tr.push(Math.max(highs[i]-lows[i], Math.abs(highs[i]-closes[i-1]), Math.abs(lows[i]-closes[i-1])));
    }
    const smooth = (arr) => {
        let s = arr.slice(0, period).reduce((a, b) => a + b);
        const out = [s];
        for (let i = period; i < arr.length; i++) { s = s - s/period + arr[i]; out.push(s); }
        return out;
    };
    const sTR = smooth(tr), sDIp = smooth(diPlus), sDIm = smooth(diMinus);
    const diPlusArr = sDIp.map((v, i) => sTR[i] ? 100 * v / sTR[i] : 0);
    const diMinusArr = sDIm.map((v, i) => sTR[i] ? 100 * v / sTR[i] : 0);
    const dx = diPlusArr.map((v, i) => {
        const s = v + diMinusArr[i];
        return s ? 100 * Math.abs(v - diMinusArr[i]) / s : 0;
    });
    const adx = dx.slice(-period).reduce((a, b) => a + b) / period;
    return { adx, diPlus: diPlusArr[diPlusArr.length-1], diMinus: diMinusArr[diMinusArr.length-1] };
}

function calcCCI(highs, lows, closes, period = 20) {
    if (closes.length < period) return null;
    const tps = closes.map((c, i) => (highs[i] + lows[i] + c) / 3);
    const slice = tps.slice(-period);
    const sma = slice.reduce((a, b) => a + b) / period;
    const md = slice.reduce((a, b) => a + Math.abs(b - sma), 0) / period;
    return md ? (tps[tps.length-1] - sma) / (0.015 * md) : 0;
}

function calcWilliamsR(highs, lows, closes, period = 14) {
    if (closes.length < period) return null;
    const hh = Math.max(...highs.slice(-period));
    const ll = Math.min(...lows.slice(-period));
    return hh === ll ? -50 : ((hh - closes[closes.length-1]) / (hh - ll)) * -100;
}

function calcOBV(closes, volumes) {
    let obv = 0;
    const obvArr = [0];
    for (let i = 1; i < closes.length; i++) {
        obv += closes[i] > closes[i-1] ? volumes[i] : closes[i] < closes[i-1] ? -volumes[i] : 0;
        obvArr.push(obv);
    }
    const recent = obvArr.slice(-20);
    const trend = (recent[recent.length-1] - recent[0]) > 0 ? 'עולה 📈' : 'יורד 📉';
    return { obv, trend, change20d: recent[recent.length-1] - recent[0] };
}

function calcMFI(highs, lows, closes, volumes, period = 14) {
    if (closes.length < period + 1) return null;
    const tps = closes.map((c, i) => (highs[i] + lows[i] + c) / 3);
    let posFlow = 0, negFlow = 0;
    for (let i = closes.length - period; i < closes.length; i++) {
        const mf = tps[i] * volumes[i];
        if (tps[i] > tps[i-1]) posFlow += mf;
        else negFlow += mf;
    }
    if (negFlow === 0) return 100;
    return 100 - (100 / (1 + posFlow / negFlow));
}

function calcROC(closes, period = 12) {
    if (closes.length < period + 1) return null;
    const prev = closes[closes.length - 1 - period];
    const curr = closes[closes.length - 1];
    return prev ? ((curr - prev) / prev) * 100 : null;
}

function calcParabolicSAR(highs, lows, closes) {
    if (closes.length < 10) return null;
    let af = 0.02, maxAF = 0.2, sar, ep, isLong;
    isLong = closes[1] > closes[0];
    sar = isLong ? Math.min(...lows.slice(0, 3)) : Math.max(...highs.slice(0, 3));
    ep = isLong ? highs[0] : lows[0];
    for (let i = 1; i < closes.length; i++) {
        sar = sar + af * (ep - sar);
        if (isLong) {
            if (lows[i] < sar) { isLong = false; sar = ep; ep = lows[i]; af = 0.02; }
            else { if (highs[i] > ep) { ep = highs[i]; af = Math.min(af + 0.02, maxAF); } }
        } else {
            if (highs[i] > sar) { isLong = true; sar = ep; ep = highs[i]; af = 0.02; }
            else { if (lows[i] < ep) { ep = lows[i]; af = Math.min(af + 0.02, maxAF); } }
        }
    }
    return { sar, isLong, signal: isLong ? 'Bullish (מחיר מעל SAR)' : 'Bearish (מחיר מתחת SAR)' };
}

function calcFibonacci(high, low) {
    const diff = high - low;
    return {
        '0%':    high,
        '23.6%': high - diff * 0.236,
        '38.2%': high - diff * 0.382,
        '50%':   high - diff * 0.5,
        '61.8%': high - diff * 0.618,
        '78.6%': high - diff * 0.786,
        '100%':  low,
        'ext 127.2%': low - diff * 0.272,
        'ext 161.8%': low - diff * 0.618,
    };
}

function calcPivotPoints(high, low, close) {
    const p = (high + low + close) / 3;
    return {
        P: p, R1: 2*p - low, R2: p + (high - low), R3: high + 2*(p - low),
        S1: 2*p - high, S2: p - (high - low), S3: low - 2*(high - p),
    };
}

function calcSupportResistance(closes, tolerance = 0.02) {
    const levels = [];
    for (let i = 5; i < closes.length - 5; i++) {
        const slice = closes.slice(i-5, i+6);
        const min = Math.min(...slice), max = Math.max(...slice);
        if (closes[i] === min) levels.push({ type: 'support', price: closes[i] });
        if (closes[i] === max) levels.push({ type: 'resistance', price: closes[i] });
    }
    // Cluster nearby levels
    const clusters = [];
    levels.forEach(l => {
        const existing = clusters.find(c => Math.abs(c.price - l.price) / l.price < tolerance);
        if (existing) { existing.count++; existing.price = (existing.price + l.price) / 2; }
        else clusters.push({ ...l, count: 1 });
    });
    return clusters.sort((a, b) => b.count - a.count).slice(0, 6);
}

async function fetchAllPriceData(sym, range = '6mo') {
    const r = await yfPrice(sym, '1d', range);
    const closes  = (r.indicators?.quote?.[0]?.close  || []).filter(x => x != null);
    const highs   = (r.indicators?.quote?.[0]?.high   || []).filter(x => x != null);
    const lows    = (r.indicators?.quote?.[0]?.low    || []).filter(x => x != null);
    const volumes = (r.indicators?.quote?.[0]?.volume || []).filter(x => x != null);
    return { closes, highs, lows, volumes, meta: r.meta };
}

// ─── TECHNICAL TOOL FUNCTIONS ─────────────────────────────────────────────────

async function getStochastic(sym) {
    const { closes, highs, lows } = await fetchAllPriceData(sym);
    const s = calcStochastic(highs, lows, closes);
    if (!s) return 'אין מספיק נתונים';
    const interp = s.k > 80 ? '⚠️ קנייה יתר (bearish signal)' : s.k < 20 ? '⚡ מכירה יתר (bullish signal)' : '➡️ ניטרלי';
    const cross = s.k > s.d ? '📈 %K מעל %D (מומנטום חיובי)' : '📉 %K מתחת %D (מומנטום שלילי)';
    return `Stochastic — ${sym.toUpperCase()}\n%K: ${s.k.toFixed(1)} | %D: ${s.d.toFixed(1)}\n${interp}\n${cross}`;
}

async function getATR(sym) {
    const { closes, highs, lows, meta } = await fetchAllPriceData(sym);
    const atr = calcATR(highs, lows, closes);
    if (!atr) return 'אין מספיק נתונים';
    const pct = meta.regularMarketPrice ? (atr / meta.regularMarketPrice * 100).toFixed(2) : 'N/A';
    const vol = atr/meta.regularMarketPrice > 0.03 ? 'תנודתיות גבוהה 🔥' : atr/meta.regularMarketPrice > 0.015 ? 'תנודתיות בינונית' : 'תנודתיות נמוכה 😴';
    return `ATR — ${sym.toUpperCase()}\nATR(14): $${atr.toFixed(2)} (${pct}% מהמחיר)\n${vol}\nטווח יומי ממוצע: $${atr.toFixed(2)}`;
}

async function getADX(sym) {
    const { closes, highs, lows } = await fetchAllPriceData(sym);
    const a = calcADX(highs, lows, closes);
    if (!a) return 'אין מספיק נתונים';
    const strength = a.adx > 50 ? '💪 טרנד חזק מאוד' : a.adx > 25 ? '✅ טרנד ברור' : a.adx > 20 ? '🔄 טרנד מתפתח' : '😐 אין טרנד ברור (סינון)';
    const dir = a.diPlus > a.diMinus ? '📈 כיוון: Bullish (DI+ > DI-)' : '📉 כיוון: Bearish (DI- > DI+)';
    return `ADX — ${sym.toUpperCase()}\nADX: ${a.adx.toFixed(1)} | DI+: ${a.diPlus.toFixed(1)} | DI-: ${a.diMinus.toFixed(1)}\n${strength}\n${dir}`;
}

async function getCCI(sym) {
    const { closes, highs, lows } = await fetchAllPriceData(sym);
    const cci = calcCCI(highs, lows, closes);
    if (cci == null) return 'אין מספיק נתונים';
    const interp = cci > 100 ? '⚠️ קנייה יתר (>+100)' : cci < -100 ? '⚡ מכירה יתר (<-100)' : '➡️ ניטרלי';
    return `CCI(20) — ${sym.toUpperCase()}\nCCI: ${cci.toFixed(1)}\n${interp}\n*>+100 = חזק bullish/קנייה יתר | <-100 = חזק bearish/מכירה יתר*`;
}

async function getWilliamsR(sym) {
    const { closes, highs, lows } = await fetchAllPriceData(sym);
    const wr = calcWilliamsR(highs, lows, closes);
    if (wr == null) return 'אין מספיק נתונים';
    const interp = wr > -20 ? '⚠️ קנייה יתר (Bearish)' : wr < -80 ? '⚡ מכירה יתר (Bullish)' : '➡️ ניטרלי';
    return `Williams %R — ${sym.toUpperCase()}\n%R: ${wr.toFixed(1)}\n${interp}\n*(0 to -20 = overbought | -80 to -100 = oversold)*`;
}

async function getOBV(sym) {
    const { closes, volumes } = await fetchAllPriceData(sym);
    const obv = calcOBV(closes, volumes);
    return `OBV — ${sym.toUpperCase()}\nOn-Balance Volume: ${(obv.obv/1e6).toFixed(1)}M\nטרנד 20 יום: ${obv.trend}\n*OBV עולה = לחץ קניה. OBV יורד = לחץ מכירה. סטייה מהמחיר = אות חשוב*`;
}

async function getFibonacci(sym) {
    const { meta } = await fetchAllPriceData(sym, '1y');
    const r = await yfPrice(sym, '1d', '1y');
    const highs = r.indicators?.quote?.[0]?.high?.filter(x => x != null) || [];
    const lows  = r.indicators?.quote?.[0]?.low?.filter(x => x != null) || [];
    const high52 = Math.max(...highs), low52 = Math.min(...lows);
    const fib = calcFibonacci(high52, low52);
    const curr = meta.regularMarketPrice;
    const lines = Object.entries(fib).map(([k, v]) => {
        const dist = curr ? ((curr - v) / v * 100).toFixed(1) : '';
        return `${k}: $${v.toFixed(2)}${dist ? ` (${dist > 0 ? '+' : ''}${dist}% ממחיר נוכחי)` : ''}`;
    });
    return `Fibonacci — ${sym.toUpperCase()} (52 שבועות)\nגבוה: $${high52.toFixed(2)} | נמוך: $${low52.toFixed(2)}\n\n${lines.join('\n')}`;
}

async function getSupportResistance(sym) {
    const { closes } = await fetchAllPriceData(sym, '1y');
    const levels = calcSupportResistance(closes);
    const curr = closes[closes.length - 1];
    const above = levels.filter(l => l.price > curr).sort((a, b) => a.price - b.price);
    const below = levels.filter(l => l.price <= curr).sort((a, b) => b.price - a.price);
    let out = `Support & Resistance — ${sym.toUpperCase()}\nמחיר נוכחי: $${curr.toFixed(2)}\n\n`;
    out += `📈 התנגדויות:\n${above.slice(0,3).map(l => `  $${l.price.toFixed(2)} (חוזק: ${l.count})`).join('\n') || '  אין'}\n\n`;
    out += `📉 תמיכות:\n${below.slice(0,3).map(l => `  $${l.price.toFixed(2)} (חוזק: ${l.count})`).join('\n') || '  אין'}`;
    return out;
}

async function getMACross(sym) {
    const { closes } = await fetchAllPriceData(sym, '2y');
    const ma50 = calcSMA(closes, 50), ma200 = calcSMA(closes, 200);
    const ma50p = calcSMA(closes.slice(0, -1), 50), ma200p = calcSMA(closes.slice(0, -1), 200);
    if (!ma50 || !ma200) return 'אין מספיק נתונים (צריך 200+ ימים)';
    const curr = closes[closes.length - 1];
    const goldenCross = ma50 > ma200 && ma50p < ma200p;
    const deathCross = ma50 < ma200 && ma50p > ma200p;
    const status = ma50 > ma200 ? '🟢 MA50 מעל MA200 (Bullish)' : '🔴 MA50 מתחת MA200 (Bearish)';
    const signal = goldenCross ? '✨ Golden Cross זוהה לאחרונה!' : deathCross ? '💀 Death Cross זוהה לאחרונה!' : '';
    return `MA Cross — ${sym.toUpperCase()}\nMA50: $${ma50.toFixed(2)} | MA200: $${ma200.toFixed(2)}\nמחיר: $${curr.toFixed(2)}\n${status}${signal ? '\n' + signal : ''}\nמחיר vs MA50: ${((curr/ma50-1)*100).toFixed(1)}% | vs MA200: ${((curr/ma200-1)*100).toFixed(1)}%`;
}

async function getPivotPoints(sym) {
    const r = await yfPrice(sym, '1d', '5d');
    const q = r.indicators?.quote?.[0];
    const idx = (q?.close || []).length - 2;
    const h = q.high[idx], l = q.low[idx], c = q.close[idx];
    const pivots = calcPivotPoints(h, l, c);
    const curr = q.close[q.close.length - 1];
    const lines = Object.entries(pivots).map(([k, v]) => `${k}: $${v.toFixed(2)}`);
    return `Pivot Points — ${sym.toUpperCase()} (יומי)\nמחיר נוכחי: $${curr.toFixed(2)}\n\n${lines.join('\n')}\n\n*Pivots מחושבים מנתוני יום המסחר הקודם*`;
}

async function getMFI(sym) {
    const { closes, highs, lows, volumes } = await fetchAllPriceData(sym);
    const mfi = calcMFI(highs, lows, closes, volumes);
    if (mfi == null) return 'אין מספיק נתונים';
    const interp = mfi > 80 ? '⚠️ קנייה יתר (Bearish)' : mfi < 20 ? '⚡ מכירה יתר (Bullish)' : '➡️ ניטרלי';
    return `Money Flow Index — ${sym.toUpperCase()}\nMFI(14): ${mfi.toFixed(1)}\n${interp}\n*כמו RSI אבל משקלל גם נפח מסחר*`;
}

async function get52WkAnalysis(sym) {
    const r = await yfPrice(sym, '1d', '1y');
    const closes = (r.indicators?.quote?.[0]?.close || []).filter(x => x != null);
    const curr = r.meta.regularMarketPrice;
    const high52 = Math.max(...closes), low52 = Math.min(...closes);
    const pos = ((curr - low52) / (high52 - low52) * 100).toFixed(1);
    const fromHigh = ((curr/high52 - 1) * 100).toFixed(1);
    const fromLow = ((curr/low52 - 1) * 100).toFixed(1);
    const zone = pos > 80 ? '🔥 גבוה (near 52w high)' : pos < 20 ? '🔵 נמוך (near 52w low — הזדמנות?)' : '➡️ אמצע הטווח';
    return `ניתוח 52 שבועות — ${sym.toUpperCase()}\nגבוה 52W: $${high52.toFixed(2)} (${fromHigh}% ממחיר)\nנמוך 52W: $${low52.toFixed(2)} (+${fromLow}% ממחיר)\nמחיר: $${curr.toFixed(2)}\nמיקום בטווח: ${pos}%\n${zone}`;
}

async function getMomentum(sym) {
    const { closes } = await fetchAllPriceData(sym, '1y');
    const roc1m  = calcROC(closes.slice(-22), 21);
    const roc3m  = calcROC(closes.slice(-65), 64);
    const roc6m  = calcROC(closes.slice(-130), 129);
    const roc12m = calcROC(closes, closes.length - 1);
    const score = [roc1m, roc3m, roc6m, roc12m].filter(x => x != null).filter(x => x > 0).length;
    const emoji = score >= 3 ? '💪 מומנטום חזק' : score >= 2 ? '✅ מומנטום חיובי' : score === 1 ? '⚠️ מומנטום חלש' : '📉 מומנטום שלילי';
    return `Momentum — ${sym.toUpperCase()}\n1 חודש: ${roc1m != null ? roc1m.toFixed(1)+'%' : 'N/A'}\n3 חודשים: ${roc3m != null ? roc3m.toFixed(1)+'%' : 'N/A'}\n6 חודשים: ${roc6m != null ? roc6m.toFixed(1)+'%' : 'N/A'}\n12 חודשים: ${roc12m != null ? roc12m.toFixed(1)+'%' : 'N/A'}\n${emoji} (${score}/4 טווחים חיוביים)`;
}

async function getParabolicSAR(sym) {
    const { closes, highs, lows } = await fetchAllPriceData(sym);
    const sar = calcParabolicSAR(highs, lows, closes);
    if (!sar) return 'אין מספיק נתונים';
    const curr = closes[closes.length - 1];
    return `Parabolic SAR — ${sym.toUpperCase()}\nSAR: $${sar.sar.toFixed(2)} | מחיר: $${curr.toFixed(2)}\n${sar.signal}\n*SAR הופך כיוון = אות חזרה אפשרית*`;
}

async function getHistoricalVolatility(sym) {
    const { closes } = await fetchAllPriceData(sym, '1y');
    const returns = closes.slice(1).map((c, i) => Math.log(c / closes[i]));
    const calc = (arr) => {
        const mean = arr.reduce((a, b) => a + b) / arr.length;
        const variance = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / arr.length;
        return Math.sqrt(variance * 252) * 100;
    };
    const hv20 = calc(returns.slice(-20));
    const hv60 = calc(returns.slice(-60));
    const hv252 = calc(returns);
    const level = hv20 > 40 ? '🔥 גבוהה מאוד' : hv20 > 25 ? '⚠️ גבוהה' : hv20 > 15 ? '➡️ בינונית' : '😴 נמוכה';
    return `תנודתיות היסטורית — ${sym.toUpperCase()}\nHV 20d: ${hv20.toFixed(1)}% | HV 60d: ${hv60.toFixed(1)}% | HV 1y: ${hv252.toFixed(1)}%\n${level}\n*תנודתיות שנתית ממוסד. >30% = מניה תנודתית*`;
}

async function getMAAnalysis(sym) {
    const { closes } = await fetchAllPriceData(sym, '2y');
    const curr = closes[closes.length - 1];
    const ma20 = calcSMA(closes, 20), ma50 = calcSMA(closes, 50);
    const ma100 = calcSMA(closes, 100), ma200 = calcSMA(closes, 200);
    const f = (ma, label) => {
        if (!ma) return `${label}: N/A`;
        const diff = ((curr/ma - 1)*100).toFixed(1);
        return `${label}: $${ma.toFixed(2)} (${diff > 0 ? '+' : ''}${diff}%) ${curr > ma ? '✅' : '❌'}`;
    };
    const bullCount = [ma20, ma50, ma100, ma200].filter(ma => ma && curr > ma).length;
    return `ממוצעים נעים — ${sym.toUpperCase()}\nמחיר: $${curr.toFixed(2)}\n\n${f(ma20,'SMA20')}\n${f(ma50,'SMA50')}\n${f(ma100,'SMA100')}\n${f(ma200,'SMA200')}\n\nמחיר מעל ${bullCount}/4 ממוצעים ${bullCount >= 3 ? '✅ Bullish' : bullCount <= 1 ? '❌ Bearish' : '⚠️ מעורב'}`;
}

// ─── FUNDAMENTAL TOOLS ────────────────────────────────────────────────────────

async function getValuation(sym) {
    const d = await yf(sym, 'defaultKeyStatistics,summaryDetail');
    if (!d) return 'לא נמצאו נתונים';
    const s = d.summaryDetail, k = d.defaultKeyStatistics;
    const pe = s?.trailingPE?.raw, fpe = s?.forwardPE?.raw;
    const pb = k?.priceToBook?.raw, evEbitda = k?.enterpriseToEbitda?.raw;
    const peg = k?.pegRatio?.raw, evRev = k?.enterpriseToRevenue?.raw;
    const ps = s?.priceToSalesTrailing12Months?.raw;
    return `ניתוח שווי — ${sym.toUpperCase()}\nP/E (trailing): ${pe ? pe.toFixed(1) : 'N/A'} | P/E (forward): ${fpe ? fpe.toFixed(1) : 'N/A'}\nP/B: ${pb ? pb.toFixed(2) : 'N/A'} | P/S: ${ps ? ps.toFixed(2) : 'N/A'}\nEV/EBITDA: ${evEbitda ? evEbitda.toFixed(1) : 'N/A'} | EV/Revenue: ${evRev ? evRev.toFixed(2) : 'N/A'}\nPEG Ratio: ${peg ? peg.toFixed(2) : 'N/A'}\n\n*P/E<15=זול | 15-25=הוגן | >25=יקר (כלל אצבע)*\n*EV/EBITDA<10=זול | >20=יקר*`;
}

async function getEarningsDate(sym) {
    const d = await yf(sym, 'calendarEvents,earningsTrend');
    if (!d) return 'לא נמצאו נתונים';
    const cal = d.calendarEvents?.earnings;
    const trend = d.earningsTrend?.trend?.[0];
    const dates = cal?.earningsDate?.map(e => new Date(e.raw * 1000).toLocaleDateString('he-IL')).join(' — ') || 'לא ידוע';
    const epsEst = trend?.earningsEstimate?.avg?.raw;
    const revEst = trend?.revenueEstimate?.avg?.raw;
    return `תאריך דוח — ${sym.toUpperCase()}\nתאריך משוער: ${dates}\n\nתחזית EPS: $${epsEst ? epsEst.toFixed(2) : 'N/A'}\nתחזית הכנסות: ${revEst ? fmtB(revEst) : 'N/A'}\n\n*תאריך יכול להשתנות. בדוק ב-Investor Relations של החברה*`;
}

async function getDividend(sym) {
    const d = await yf(sym, 'summaryDetail,defaultKeyStatistics');
    if (!d) return 'לא נמצאו נתונים';
    const s = d.summaryDetail;
    const yield_ = s?.dividendYield?.raw;
    if (!yield_ && !s?.lastDividendValue?.raw) return `${sym.toUpperCase()}: לא משלמת דיבידנד`;
    const div = s?.dividendRate?.raw, exDate = s?.exDividendDate?.raw;
    const payout = s?.payoutRatio?.raw;
    const trailing = s?.trailingAnnualDividendYield?.raw;
    const exDateStr = exDate ? new Date(exDate * 1000).toLocaleDateString('he-IL') : 'N/A';
    return `דיבידנד — ${sym.toUpperCase()}\nתשואה: ${yield_ ? (yield_*100).toFixed(2)+'%' : 'N/A'} | שנתי: $${div ? div.toFixed(2) : 'N/A'}\nתשואה trailing: ${trailing ? (trailing*100).toFixed(2)+'%' : 'N/A'}\nPayout Ratio: ${payout ? (payout*100).toFixed(1)+'%' : 'N/A'}\nEx-Dividend: ${exDateStr}\n\n*Payout>80% = סיכון קיצוץ דיבידנד*`;
}

async function getAnalystConsensus(sym) {
    const d = await yf(sym, 'financialData,recommendationTrend');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData;
    const rt = d.recommendationTrend?.trend?.[0];
    const key = fd?.recommendationKey;
    const mean = fd?.recommendationMean?.raw;
    const analysts = fd?.numberOfAnalystOpinions?.raw;
    const emoji = key === 'strongBuy' || key === 'buy' ? '💚' : key === 'hold' ? '💛' : '🔴';
    const ratingMap = { strongBuy: 'Strong Buy', buy: 'Buy', hold: 'Hold', sell: 'Sell', strongSell: 'Strong Sell' };
    let trend = '';
    if (rt) trend = `\nחודש אחרון: ${rt.strongBuy || 0} SB | ${rt.buy || 0} Buy | ${rt.hold || 0} Hold | ${rt.sell + rt.strongSell || 0} Sell`;
    return `אנליסטים — ${sym.toUpperCase()}\n${emoji} קונצנזוס: ${ratingMap[key] || key || 'N/A'}\nציון ממוצע: ${mean ? mean.toFixed(2) : 'N/A'}/5 (1=SB, 5=SS)\nמספר אנליסטים: ${analysts || 'N/A'}${trend}`;
}

async function getPriceTargets(sym) {
    const d = await yf(sym, 'financialData');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData;
    const curr = fd?.currentPrice?.raw;
    const low = fd?.targetLowPrice?.raw, mean = fd?.targetMeanPrice?.raw;
    const high = fd?.targetHighPrice?.raw, median = fd?.targetMedianPrice?.raw;
    const upside = curr && mean ? ((mean/curr - 1)*100).toFixed(1) : null;
    return `יעדי מחיר אנליסטים — ${sym.toUpperCase()}\nמחיר נוכחי: $${curr ? curr.toFixed(2) : 'N/A'}\n\nיעד ממוצע: $${mean ? mean.toFixed(2) : 'N/A'}${upside ? ` (${upside > 0 ? '+' : ''}${upside}% upside)` : ''}\nיעד חציוני: $${median ? median.toFixed(2) : 'N/A'}\nיעד גבוה: $${high ? high.toFixed(2) : 'N/A'}\nיעד נמוך: $${low ? low.toFixed(2) : 'N/A'}`;
}

async function getShortInterest(sym) {
    const d = await yf(sym, 'defaultKeyStatistics');
    if (!d) return 'לא נמצאו נתונים';
    const k = d.defaultKeyStatistics;
    const shortRatio = k?.shortRatio?.raw;
    const shortPct = k?.shortPercentOfFloat?.raw;
    const sharesShort = k?.sharesShort?.raw;
    const prev = k?.sharesShortPriorMonth?.raw;
    const change = sharesShort && prev ? ((sharesShort/prev - 1)*100).toFixed(1) : null;
    const risk = shortPct > 0.15 ? '🔴 Short Interest גבוה — עלול לגרום Short Squeeze' : shortPct > 0.05 ? '⚠️ בינוני' : '🟢 נמוך';
    return `Short Interest — ${sym.toUpperCase()}\nמניות בשורט: ${sharesShort ? (sharesShort/1e6).toFixed(1)+'M' : 'N/A'}\n% מה-Float: ${shortPct ? (shortPct*100).toFixed(2)+'%' : 'N/A'}\nShort Ratio: ${shortRatio ? shortRatio.toFixed(1)+' ימים' : 'N/A'}\nשינוי מחודש קודם: ${change ? change+'%' : 'N/A'}\n${risk}`;
}

async function getInsiderActivity(sym) {
    const d = await yf(sym, 'insiderHolders,netSharePurchaseActivity');
    if (!d) return 'לא נמצאו נתונים';
    const ins = d.insiderHolders?.holders?.slice(0, 5) || [];
    const net = d.netSharePurchaseActivity;
    const netBuy = net?.netPercentInsiderShares?.raw;
    const lines = ins.map(h => {
        const tx = h.latestTransType || '';
        const shares = h.sharesOwnedDirectly?.raw || 0;
        return `  ${h.name} (${h.relation}): ${tx} | מחזיק ${(shares/1e6).toFixed(2)}M מניות`;
    });
    const netStr = netBuy != null ? `\nרכישות נטו (6m): ${(netBuy*100).toFixed(2)}%` : '';
    return `פעילות אינסיידרים — ${sym.toUpperCase()}${netStr}\n\n${lines.join('\n') || 'אין נתונים'}`;
}

async function getProfitability(sym) {
    const d = await yf(sym, 'financialData');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData;
    const roe = fd?.returnOnEquity?.raw, roa = fd?.returnOnAssets?.raw;
    const gross = fd?.grossMargins?.raw, oper = fd?.operatingMargins?.raw;
    const profit = fd?.profitMargins?.raw, ebitda = fd?.ebitdaMargins?.raw;
    return `רווחיות — ${sym.toUpperCase()}\nROE: ${roe ? (roe*100).toFixed(1)+'%' : 'N/A'} | ROA: ${roa ? (roa*100).toFixed(1)+'%' : 'N/A'}\n\nגולמי: ${gross ? (gross*100).toFixed(1)+'%' : 'N/A'} | תפעולי: ${oper ? (oper*100).toFixed(1)+'%' : 'N/A'}\nEBITDA Margin: ${ebitda ? (ebitda*100).toFixed(1)+'%' : 'N/A'} | נטו: ${profit ? (profit*100).toFixed(1)+'%' : 'N/A'}\n\n*ROE>15% טוב | Gross Margin>40% = יתרון תחרותי*`;
}

async function getLiquidity(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData;
    const cr = fd?.currentRatio?.raw, qr = fd?.quickRatio?.raw;
    const de = fd?.debtToEquity?.raw;
    const cash = fd?.totalCash?.raw, debt = fd?.totalDebt?.raw;
    const crOk = cr > 2 ? '✅' : cr > 1 ? '⚠️' : '🔴';
    const deOk = de < 50 ? '✅' : de < 100 ? '⚠️' : '🔴';
    return `נזילות וחוב — ${sym.toUpperCase()}\n${crOk} Current Ratio: ${cr ? cr.toFixed(2) : 'N/A'} | Quick Ratio: ${qr ? qr.toFixed(2) : 'N/A'}\n${deOk} Debt/Equity: ${de ? de.toFixed(1)+'%' : 'N/A'}\n\nמזומנים: ${fmtB(cash)} | חוב כולל: ${fmtB(debt)}\n\n*CR>2=בריא | D/E<50%=חוב נמוך*`;
}

async function getGrowthRates(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData, k = d.defaultKeyStatistics;
    const revGrowth = fd?.revenueGrowth?.raw, epsGrowth = fd?.earningsGrowth?.raw;
    const qEpsGrowth = k?.earningsQuarterlyGrowth?.raw;
    const revFwd = fd?.revenuePerShare?.raw;
    return `צמיחה — ${sym.toUpperCase()}\nצמיחת הכנסות YoY: ${revGrowth ? fmtPct(revGrowth) : 'N/A'}\nצמיחת EPS YoY: ${epsGrowth ? fmtPct(epsGrowth) : 'N/A'}\nצמיחת EPS רבעוני: ${qEpsGrowth ? fmtPct(qEpsGrowth) : 'N/A'}\n\n*צמיחה >20% = חברה בצמיחה גבוהה*`;
}

async function getFCF(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics,summaryDetail');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData, s = d.summaryDetail;
    const fcf = fd?.freeCashflow?.raw, ocf = fd?.operatingCashflow?.raw;
    const mcap = s?.marketCap?.raw;
    const fcfYield = fcf && mcap ? (fcf/mcap*100).toFixed(2) : null;
    return `Free Cash Flow — ${sym.toUpperCase()}\nFCF: ${fmtB(fcf)}\nOperating CF: ${fmtB(ocf)}\nFCF Yield: ${fcfYield ? fcfYield+'%' : 'N/A'}\n\n*FCF Yield>5% = טוב | >8% = מצוין. חברה עם FCF חיובי = בריאה*`;
}

async function getOwnership(sym) {
    const d = await yf(sym, 'defaultKeyStatistics,majorHoldersBreakdown');
    if (!d) return 'לא נמצאו נתונים';
    const k = d.defaultKeyStatistics, mh = d.majorHoldersBreakdown;
    const inst = mh?.institutionsPercentHeld?.raw;
    const insider = mh?.insidersPercentHeld?.raw;
    const shares = k?.sharesOutstanding?.raw, float = k?.floatShares?.raw;
    return `מבנה בעלות — ${sym.toUpperCase()}\nמוסדיים: ${inst ? (inst*100).toFixed(1)+'%' : 'N/A'}\nאינסיידרים: ${insider ? (insider*100).toFixed(1)+'%' : 'N/A'}\n\nמניות בסחרור: ${shares ? (shares/1e6).toFixed(0)+'M' : 'N/A'}\nFloat: ${float ? (float/1e6).toFixed(0)+'M' : 'N/A'}\n\n*מוסדיים>70% = ביטחון מוסדי גבוה*`;
}

async function getIncomeSummary(sym) {
    const d = await yf(sym, 'financialData,summaryDetail');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData, s = d.summaryDetail;
    const rev = fd?.totalRevenue?.raw, ebitda = fd?.ebitda?.raw;
    const profit = fd?.profitMargins?.raw, gross = fd?.grossProfits?.raw;
    const mcap = s?.marketCap?.raw, ev = fd?.totalCash?.raw ? mcap + (fd.totalDebt?.raw || 0) - (fd.totalCash?.raw || 0) : null;
    return `דוח רווח-הפסד — ${sym.toUpperCase()}\nהכנסות: ${fmtB(rev)}\nרווח גולמי: ${fmtB(gross)}\nEBITDA: ${fmtB(ebitda)}\nRev/EBITDA Margin: ${rev && ebitda ? (ebitda/rev*100).toFixed(1)+'%' : 'N/A'}\nNet Margin: ${profit ? (profit*100).toFixed(1)+'%' : 'N/A'}\nMarket Cap: ${fmtB(mcap)}`;
}

async function getBalanceSummary(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData, k = d.defaultKeyStatistics;
    const cash = fd?.totalCash?.raw, debt = fd?.totalDebt?.raw;
    const bv = k?.bookValue?.raw, shares = k?.sharesOutstanding?.raw;
    const netCash = cash && debt ? cash - debt : null;
    return `מאזן — ${sym.toUpperCase()}\nמזומנים: ${fmtB(cash)}\nחוב כולל: ${fmtB(debt)}\nנטו מזומן/(חוב): ${fmtB(netCash)}\nBook Value/Share: $${bv ? bv.toFixed(2) : 'N/A'}\nמניות בסחרור: ${shares ? (shares/1e6).toFixed(0)+'M' : 'N/A'}`;
}

async function getGrahamNumber(sym) {
    const d = await yf(sym, 'defaultKeyStatistics,summaryDetail');
    if (!d) return 'לא נמצאו נתונים';
    const k = d.defaultKeyStatistics, s = d.summaryDetail;
    const eps = k?.trailingEps?.raw, bv = k?.bookValue?.raw, curr = s?.regularMarketPrice?.raw || s?.previousClose?.raw;
    if (!eps || !bv || eps < 0) return `${sym.toUpperCase()}: לא ניתן לחשב Graham Number (EPS שלילי או חסר נתונים)`;
    const graham = Math.sqrt(22.5 * eps * bv);
    const margin = curr ? ((graham/curr - 1)*100).toFixed(1) : null;
    const signal = margin && margin > 0 ? `🟢 מחיר מתחת Graham Number (+${margin}% margin of safety)` : margin ? `🔴 מחיר מעל Graham Number (${margin}% above)` : '';
    return `Graham Number — ${sym.toUpperCase()}\nEPS: $${eps.toFixed(2)} | Book Value: $${bv.toFixed(2)}\nGraham Number: $${graham.toFixed(2)}\nמחיר נוכחי: $${curr ? curr.toFixed(2) : 'N/A'}\n${signal}\n*נוסחת גרהם: √(22.5 × EPS × BV)*`;
}

async function getDCFSimple(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics,summaryDetail');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData, k = d.defaultKeyStatistics, s = d.summaryDetail;
    const fcf = fd?.freeCashflow?.raw, shares = k?.sharesOutstanding?.raw;
    const growthRate = fd?.revenueGrowth?.raw || 0.10;
    if (!fcf || !shares || fcf < 0) return `${sym.toUpperCase()}: DCF לא ישים (FCF שלילי)`;
    const fcfPerShare = fcf / shares;
    const discountRate = 0.10, terminalGrowth = 0.03;
    let pv = 0;
    for (let y = 1; y <= 10; y++) {
        const growth = y <= 5 ? Math.min(growthRate, 0.25) : 0.05;
        pv += fcfPerShare * Math.pow(1 + growth, y) / Math.pow(1 + discountRate, y);
    }
    const terminalValue = fcfPerShare * Math.pow(1.05, 10) * (1 + terminalGrowth) / (discountRate - terminalGrowth);
    const intrinsic = pv + terminalValue / Math.pow(1 + discountRate, 10);
    const curr = s?.regularMarketPrice?.raw;
    const margin = curr ? ((intrinsic/curr - 1)*100).toFixed(1) : null;
    return `DCF פשוט — ${sym.toUpperCase()}\nFCF/Share: $${fcfPerShare.toFixed(2)}\nצמיחה שנתים 1-5: ${(Math.min(growthRate,0.25)*100).toFixed(1)}%\nDiscount Rate: 10%\n\nשווי פנימי: $${intrinsic.toFixed(2)}\nמחיר נוכחי: $${curr ? curr.toFixed(2) : 'N/A'}\n${margin ? (margin > 0 ? `🟢 זול ב-${margin}%` : `🔴 יקר ב-${Math.abs(margin)}%`) : ''}\n\n*DCF רגיש מאוד להנחות. לשימוש כהכוונה בלבד*`;
}

async function getPiotroski(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData;
    let score = 0, criteria = [];
    const roa = fd?.returnOnAssets?.raw;
    if (roa > 0) { score++; criteria.push('✅ ROA חיובי'); } else criteria.push('❌ ROA שלילי');
    const ocf = fd?.operatingCashflow?.raw;
    if (ocf > 0) { score++; criteria.push('✅ Operating CF חיובי'); } else criteria.push('❌ Operating CF שלילי');
    const fcf = fd?.freeCashflow?.raw;
    if (fcf > 0) { score++; criteria.push('✅ FCF חיובי'); } else criteria.push('❌ FCF שלילי');
    const de = fd?.debtToEquity?.raw;
    if (de < 100) { score++; criteria.push('✅ D/E<100%'); } else criteria.push('❌ D/E גבוה');
    const cr = fd?.currentRatio?.raw;
    if (cr > 1) { score++; criteria.push('✅ Current Ratio>1'); } else criteria.push('❌ Current Ratio<1');
    const gross = fd?.grossMargins?.raw;
    if (gross > 0.3) { score++; criteria.push('✅ Gross Margin>30%'); } else criteria.push('❌ Gross Margin נמוך');
    const revGrowth = fd?.revenueGrowth?.raw;
    if (revGrowth > 0) { score++; criteria.push('✅ צמיחת הכנסות חיובית'); } else criteria.push('❌ ירידה בהכנסות');
    const grade = score >= 7 ? '🟢 Strong (7-9)' : score >= 5 ? '🟡 Good (5-6)' : '🔴 Weak (<5)';
    return `Piotroski F-Score — ${sym.toUpperCase()}\nציון: ${score}/9 ${grade}\n\n${criteria.join('\n')}`;
}

async function compareStocks(syms) {
    const symbols = typeof syms === 'string' ? syms.split(',').map(s => s.trim()) : syms;
    const results = await Promise.allSettled(symbols.map(async s => {
        const d = await yf(s, 'summaryDetail,financialData,defaultKeyStatistics');
        const sum = d?.summaryDetail, fd = d?.financialData, k = d?.defaultKeyStatistics;
        return {
            sym: s.toUpperCase(),
            pe: sum?.trailingPE?.raw,
            pb: k?.priceToBook?.raw,
            roe: fd?.returnOnEquity?.raw,
            margin: fd?.profitMargins?.raw,
            growth: fd?.revenueGrowth?.raw,
            div: sum?.dividendYield?.raw,
        };
    }));
    const rows = results.filter(r => r.status === 'fulfilled').map(r => r.value);
    let out = `השוואת מניות\n${'─'.repeat(40)}\n`;
    out += `${'מניה'.padEnd(8)}P/E    P/B    ROE    Margin Growth\n`;
    rows.forEach(r => {
        out += `${r.sym.padEnd(8)}${String(r.pe?.toFixed(1)||'N/A').padEnd(7)}${String(r.pb?.toFixed(2)||'N/A').padEnd(7)}${String(r.roe?(r.roe*100).toFixed(1)+'%':'N/A').padEnd(7)}${String(r.margin?(r.margin*100).toFixed(1)+'%':'N/A').padEnd(7)}${r.growth?(r.growth*100).toFixed(1)+'%':'N/A'}\n`;
    });
    return out;
}

async function getAltmanZ(sym) {
    const d = await yf(sym, 'financialData,defaultKeyStatistics,summaryDetail');
    if (!d) return 'לא נמצאו נתונים';
    const fd = d.financialData, s = d.summaryDetail, k = d.defaultKeyStatistics;
    const mcap = s?.marketCap?.raw, debt = fd?.totalDebt?.raw;
    const ocf = fd?.operatingCashflow?.raw, rev = fd?.totalRevenue?.raw;
    const profit = fd?.profitMargins?.raw ? fd.financialData?.grossProfits?.raw : null;
    if (!mcap || !debt || !rev) return `${sym.toUpperCase()}: אין מספיק נתונים לחישוב Altman Z`;
    const x4 = mcap / debt;
    const x5 = rev / mcap;
    const z = 3.3 * (ocf||0)/mcap + 1.0 * rev/mcap + 1.4 * 0.05 + 1.2 * 0.15 + 0.6 * x4;
    const risk = z > 2.99 ? '🟢 Safe Zone (Z>3)' : z > 1.81 ? '🟡 Grey Zone (1.81-2.99)' : '🔴 Distress Zone (Z<1.81)';
    return `Altman Z-Score — ${sym.toUpperCase()}\nZ-Score: ${z.toFixed(2)}\n${risk}\n\n*Z>3 = בריא | 1.81-3 = אפור | <1.81 = סיכון גבוה*`;
}

async function getUpgradesDowngrades(sym) {
    const d = await yf(sym, 'upgradeDowngradeHistory');
    if (!d) return 'לא נמצאו נתונים';
    const hist = d.upgradeDowngradeHistory?.history?.slice(0, 8) || [];
    const lines = hist.map(h => {
        const date = new Date(h.epochGradeDate * 1000).toLocaleDateString('he-IL');
        const emoji = h.action === 'up' ? '📈' : h.action === 'down' ? '📉' : '➡️';
        return `${emoji} ${date}: ${h.firm} — ${h.fromGrade || '?'} → ${h.toGrade}`;
    });
    return `שינויי דירוג — ${sym.toUpperCase()}\n\n${lines.join('\n') || 'אין נתונים אחרונים'}`;
}

async function getEPSSurprise(sym) {
    const d = await yf(sym, 'earningsHistory');
    if (!d) return 'לא נמצאו נתונים';
    const hist = d.earningsHistory?.history?.slice(0, 6) || [];
    const lines = hist.map(h => {
        const date = h.quarter?.fmt || 'N/A';
        const actual = h.epsActual?.raw, estimate = h.epsEstimate?.raw;
        const surprise = h.surprisePercent?.raw;
        const emoji = surprise > 0 ? '✅' : '❌';
        return `${emoji} Q${date}: Actual $${actual?.toFixed(2)||'N/A'} vs Est $${estimate?.toFixed(2)||'N/A'} (${surprise ? (surprise*100).toFixed(1)+'%' : 'N/A'})`;
    });
    return `EPS Surprise History — ${sym.toUpperCase()}\n\n${lines.join('\n') || 'אין נתונים'}`;
}

async function getRelativeStrength(sym) {
    const [stockData, spyData] = await Promise.all([
        fetchAllPriceData(sym, '1y'),
        fetchAllPriceData('^GSPC', '1y'),
    ]);
    const calc = (closes, n) => closes.length >= n ? ((closes[closes.length-1]/closes[closes.length-n] - 1)*100).toFixed(1) : null;
    const periods = [22, 66, 130, 252];
    const labels = ['1M', '3M', '6M', '1Y'];
    let out = `Relative Strength vs S&P500 — ${sym.toUpperCase()}\n\n`;
    out += `${'תקופה'.padEnd(6)}${'מניה'.padEnd(10)}${'S&P500'.padEnd(10)}${'יחסי'}\n`;
    periods.forEach((p, i) => {
        const s = calc(stockData.closes, p), spy = calc(spyData.closes, p);
        const rel = s && spy ? (parseFloat(s) - parseFloat(spy)).toFixed(1) : 'N/A';
        const emoji = rel !== 'N/A' ? (parseFloat(rel) > 0 ? '✅' : '❌') : '';
        out += `${labels[i].padEnd(6)}${(s||'N/A').padEnd(10)}${(spy||'N/A').padEnd(10)}${rel} ${emoji}\n`;
    });
    return out;
}

// ─── MACRO TOOLS ──────────────────────────────────────────────────────────────

async function getYFSymbol(sym) {
    try {
        const meta = await yfQuote(sym);
        const price = meta?.regularMarketPrice;
        const prev = meta?.chartPreviousClose;
        const chg = price && prev ? ((price-prev)/prev*100).toFixed(2) : null;
        return { price, chg, name: meta?.shortName || sym };
    } catch { return null; }
}

async function getVIX() {
    const d = await getYFSymbol('^VIX');
    if (!d) return 'לא נמצאו נתונים';
    const level = d.price > 30 ? '😱 פחד קיצוני' : d.price > 20 ? '😰 פחד' : d.price > 15 ? '😐 ניטרלי' : '😎 חמדנות';
    return `VIX (מדד פחד)\nVIX: ${d.price?.toFixed(2)} (${d.chg > 0 ? '+' : ''}${d.chg}%)\n${level}\n*>30=בהלה | 20-30=חשש | <15=שאננות*`;
}

async function getDXY() {
    const d = await getYFSymbol('DX-Y.NYB');
    if (!d) return 'לא נמצאו נתונים';
    return `Dollar Index (DXY)\nDXY: ${d.price?.toFixed(2)} (${d.chg > 0 ? '+' : ''}${d.chg}%)\n*DXY חזק = לחץ על מניות בינ"ל וסחורות*`;
}

async function getOilPrices() {
    const [wti, brent] = await Promise.all([getYFSymbol('CL=F'), getYFSymbol('BZ=F')]);
    const spread = wti?.price && brent?.price ? (brent.price - wti.price).toFixed(2) : 'N/A';
    return `מחירי נפט\nWTI: $${wti?.price?.toFixed(2)||'N/A'} (${wti?.chg||'N/A'}%)\nBrent: $${brent?.price?.toFixed(2)||'N/A'} (${brent?.chg||'N/A'}%)\nSpread: $${spread}`;
}

async function getNaturalGas() {
    const d = await getYFSymbol('NG=F');
    return `גז טבעי\nמחיר: $${d?.price?.toFixed(3)||'N/A'} (${d?.chg||'N/A'}%)/MMBtu`;
}

async function getYieldCurve() {
    const [y2, y5, y10, y30] = await Promise.all([
        getYFSymbol('^IRX'), getYFSymbol('^FVX'),
        getYFSymbol('^TNX'), getYFSymbol('^TYX'),
    ]);
    const spread = y10?.price && y2?.price ? (y10.price - y2.price/10).toFixed(2) : 'N/A';
    const inv = parseFloat(spread) < 0;
    return `עקום תשואות אמריקאי\n2Y: ${(y2?.price/10)?.toFixed(2)||'N/A'}%\n5Y: ${y5?.price?.toFixed(2)||'N/A'}%\n10Y: ${y10?.price?.toFixed(2)||'N/A'}%\n30Y: ${y30?.price?.toFixed(2)||'N/A'}%\n\nSpread 10Y-2Y: ${spread}%${inv ? '\n⚠️ עקום הפוך — אינדיקטור מיתון היסטורי' : '\n✅ עקום תקין'}`;
}

async function getYieldSpread() {
    return getYieldCurve();
}

async function getMarketIndices() {
    const symbols = [['^GSPC','S&P 500'],['^IXIC','NASDAQ'],['^DJI','Dow Jones'],['^RUT','Russell 2000']];
    const results = await Promise.all(symbols.map(([s]) => getYFSymbol(s)));
    const lines = results.map((d, i) => d ? `${symbols[i][1]}: ${d.price?.toLocaleString()||'N/A'} (${d.chg > 0 ? '+' : ''}${d.chg}%)` : `${symbols[i][1]}: N/A`);
    return `מדדי וול סטריט\n${lines.join('\n')}`;
}

async function getSectorPerformance() {
    const sectors = [['XLK','Tech'],['XLF','Finance'],['XLV','Health'],['XLE','Energy'],['XLI','Industrial'],['XLY','Consumer Disc'],['XLP','Consumer Staples'],['XLB','Materials'],['XLRE','Real Estate'],['XLU','Utilities'],['XLC','Communication']];
    const results = await Promise.all(sectors.map(([s]) => getYFSymbol(s)));
    const lines = results.map((d, i) => {
        const chg = d?.chg;
        const emoji = chg > 1 ? '🟢' : chg > 0 ? '🔵' : chg > -1 ? '🔴' : '🔥';
        return `${emoji} ${sectors[i][1]}: ${chg > 0 ? '+' : ''}${chg||'N/A'}%`;
    });
    return `ביצועי סקטורים (יומי)\n${lines.join('\n')}`;
}

async function getWorldIndices() {
    const indices = [['^GDAXI','DAX'],['^FTSE','FTSE 100'],['^N225','Nikkei 225'],['^HSI','Hang Seng'],['^BSESN','Sensex'],['^AORD','ASX 200'],['^STOXX50E','Euro Stoxx 50']];
    const results = await Promise.all(indices.map(([s]) => getYFSymbol(s)));
    const lines = results.map((d, i) => d ? `${indices[i][1]}: ${d.price?.toLocaleString()||'N/A'} (${d.chg > 0 ? '+' : ''}${d.chg||'N/A'}%)` : null).filter(Boolean);
    return `מדדים עולמיים\n${lines.join('\n')}`;
}

async function getCommoditiesAll() {
    const comms = [['GC=F','זהב'],['SI=F','כסף'],['HG=F','נחושת'],['CL=F','WTI Crude'],['BZ=F','Brent'],['NG=F','גז טבעי'],['ZW=F','חיטה'],['ZC=F','תירס'],['ZS=F','סויה']];
    const results = await Promise.all(comms.map(([s]) => getYFSymbol(s)));
    const lines = results.map((d, i) => d ? `${comms[i][1]}: $${d.price?.toFixed(2)||'N/A'} (${d.chg > 0 ? '+' : ''}${d.chg||'N/A'}%)` : null).filter(Boolean);
    return `סחורות\n${lines.join('\n')}`;
}

async function getPreciousMetals() {
    const metals = [['GC=F','זהב ($/אונ\''],['SI=F','כסף ($/אונ\''],['PA=F','פלדיום'],['PL=F','פלטינה']];
    const results = await Promise.all(metals.map(([s]) => getYFSymbol(s)));
    const lines = results.map((d, i) => d ? `${metals[i][1]}: $${d.price?.toFixed(2)||'N/A'} (${d.chg > 0 ? '+' : ''}${d.chg||'N/A'}%)` : null).filter(Boolean);
    return `מתכות יקרות\n${lines.join('\n')}`;
}

async function getRiskOnOff() {
    const [spy, tlt, hg] = await Promise.all([getYFSymbol('SPY'), getYFSymbol('TLT'), getYFSymbol('^VIX')]);
    const ratio = spy?.price && tlt?.price ? (spy.price / tlt.price).toFixed(2) : null;
    const vix = hg?.price;
    const sentiment = vix > 25 ? '🔴 Risk-OFF (חשש בשוק)' : spy?.chg > 0.5 ? '🟢 Risk-ON (תיאבון לסיכון)' : '⚪ ניטרלי';
    return `סנטימנט שוק\n${sentiment}\nSPY: ${spy?.chg > 0 ? '+' : ''}${spy?.chg||'N/A'}% | TLT: ${tlt?.chg > 0 ? '+' : ''}${tlt?.chg||'N/A'}%\nVIX: ${vix?.toFixed(1)||'N/A'}\nSPY/TLT Ratio: ${ratio||'N/A'}\n*SPY עולה + TLT יורד = Risk-ON*`;
}

async function getInflationBreakeven() {
    const [tip, ief] = await Promise.all([getYFSymbol('TIP'), getYFSymbol('IEF')]);
    return `ציפיות אינפלציה (TIPS Breakeven)\nTIP (TIPS ETF): ${tip?.chg > 0 ? '+' : ''}${tip?.chg||'N/A'}%\nIEF (Treasury ETF): ${ief?.chg > 0 ? '+' : ''}${ief?.chg||'N/A'}%\n*TIP מתחזק יחסית ל-IEF = ציפיות אינפלציה עולות*`;
}

async function getUSMacro() {
    try {
        const BASE = 'https://api.worldbank.org/v2/country/US/indicator';
        const get = async (indicator) => {
            const r = await fetch(`${BASE}/${indicator}?format=json&per_page=3&mrv=3`, { signal: AbortSignal.timeout(8000) });
            const d = await r.json();
            return d[1]?.filter(x => x.value != null).slice(0, 2) || [];
        };
        const [gdp, cpi, unemp] = await Promise.all([
            get('NY.GDP.MKTP.KD.ZG'), get('FP.CPI.TOTL.ZG'), get('SL.UEM.TOTL.ZS')
        ]);
        const fmt = (arr) => arr.map(x => `${x.date}: ${x.value?.toFixed(1)}%`).join(' | ');
        return `מאקרו ארה"ב (World Bank)\nצמיחת GDP: ${fmt(gdp)}\nאינפלציה CPI: ${fmt(cpi)}\nאבטלה: ${fmt(unemp)}`;
    } catch { return 'לא ניתן לטעון נתוני World Bank כרגע'; }
}

async function getIsraelMacro() {
    const [ta125, ta35, usdils, eurils] = await Promise.all([
        getYFSymbol('TA125.TA'), getYFSymbol('TA35.TA'),
        getYFSymbol('USDILS=X'), getYFSymbol('EURILS=X'),
    ]);
    let out = `מאקרו ישראל\n`;
    if (ta125) out += `TA-125: ${ta125.price?.toFixed(2)||'N/A'} (${ta125.chg > 0 ? '+' : ''}${ta125.chg||'N/A'}%)\n`;
    if (ta35) out += `TA-35: ${ta35.price?.toFixed(2)||'N/A'} (${ta35.chg > 0 ? '+' : ''}${ta35.chg||'N/A'}%)\n`;
    if (usdils) out += `USD/ILS: ${usdils.price?.toFixed(4)||'N/A'} (${usdils.chg > 0 ? '+' : ''}${usdils.chg||'N/A'}%)\n`;
    if (eurils) out += `EUR/ILS: ${eurils.price?.toFixed(4)||'N/A'} (${eurils.chg > 0 ? '+' : ''}${eurils.chg||'N/A'}%)`;
    return out;
}

async function getEmergingMarkets() {
    const [eem, inda, ewz, fxi] = await Promise.all([
        getYFSymbol('EEM'), getYFSymbol('INDA'), getYFSymbol('EWZ'), getYFSymbol('FXI')
    ]);
    const lines = [[eem,'EEM (כללי EM)'],[inda,'INDA (הודו)'],[ewz,'EWZ (ברזיל)'],[fxi,'FXI (סין)']].map(([d, n]) => d ? `${n}: ${d.chg > 0 ? '+' : ''}${d.chg||'N/A'}%` : null).filter(Boolean);
    return `שווקים מתעוררים\n${lines.join('\n')}`;
}

async function getCryptoMarket() {
    try {
        const r = await fetch('https://api.coingecko.com/api/v3/global', { headers: YF_HEADERS, signal: AbortSignal.timeout(8000) });
        const d = await r.json();
        const data = d?.data;
        const mcap = data?.total_market_cap?.usd;
        const btcDom = data?.market_cap_percentage?.btc;
        const chg = data?.market_cap_change_percentage_24h_usd;
        return `שוק קריפטו\nשווי שוק כולל: ${fmtB(mcap)}\nשינוי 24h: ${chg?.toFixed(2)||'N/A'}%\nBTC Dominance: ${btcDom?.toFixed(1)||'N/A'}%`;
    } catch { return 'לא ניתן לטעון נתוני קריפטו'; }
}

async function getGlobalRates() {
    // Approximate via Yahoo Finance proxies
    const [fed, ten] = await Promise.all([getYFSymbol('^IRX'), getYFSymbol('^TNX')]);
    return `ריביות מרכזיות (משוערות)\nFed Funds (proxy 3m T-bill): ${(fed?.price/10)?.toFixed(2)||'N/A'}%\nUS 10Y Treasury: ${ten?.price?.toFixed(2)||'N/A'}%\n*לריביות ECB/BOJ/BoI — בדוק באתרים הרשמיים*`;
}

async function getFearGreed() {
    // Approximate fear & greed from VIX + market momentum
    const [vix, spy, hyd] = await Promise.all([getYFSymbol('^VIX'), getYFSymbol('SPY'), getYFSymbol('HYG')]);
    const vixScore = vix?.price > 30 ? 10 : vix?.price > 20 ? 30 : vix?.price > 15 ? 55 : 80;
    const momScore = spy?.chg > 1 ? 80 : spy?.chg > 0 ? 60 : spy?.chg > -1 ? 40 : 15;
    const score = Math.round((vixScore + momScore) / 2);
    const label = score > 75 ? '🤑 חמדנות קיצונית' : score > 55 ? '😊 חמדנות' : score > 45 ? '😐 ניטרלי' : score > 25 ? '😰 פחד' : '😱 פחד קיצוני';
    return `מדד פחד & חמדנות (משוער)\nציון: ${score}/100 — ${label}\n\nVIX: ${vix?.price?.toFixed(1)||'N/A'} | SPY שינוי: ${spy?.chg > 0 ? '+' : ''}${spy?.chg||'N/A'}%\n*מחושב מ-VIX + מומנטום שוק. לא מדד CNN האמיתי*`;
}

async function getBuffettIndicator() {
    try {
        const [wilshire, gdpData] = await Promise.all([
            getYFSymbol('^W5000'),
            fetch('https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.CD?format=json&per_page=2&mrv=2', { signal: AbortSignal.timeout(8000) }).then(r => r.json()),
        ]);
        const gdp = gdpData?.[1]?.[0]?.value;
        const mcap = wilshire?.price ? wilshire.price * 1e9 : null;
        if (!mcap || !gdp) return 'לא ניתן לחשב Buffett Indicator (אין נתוני Wilshire 5000)';
        const ratio = (mcap / gdp * 100).toFixed(1);
        const signal = ratio > 150 ? '🔴 שוק יקר מאוד (>150%)' : ratio > 100 ? '🟡 מוערך יתר (100-150%)' : ratio > 75 ? '🟢 הוגן (75-100%)' : '💚 זול (<75%)';
        return `Buffett Indicator\nשווי שוק / GDP: ${ratio}%\n${signal}\n*>100% = שוק יקר לפי Buffett*`;
    } catch { return 'לא ניתן לחשב Buffett Indicator'; }
}

async function getMarketRegime() {
    const [spy200, spy50] = await Promise.all([
        fetchAllPriceData('^GSPC', '2y'), fetchAllPriceData('^GSPC', '6mo')
    ]);
    const ma200 = calcSMA(spy200.closes, 200), ma50 = calcSMA(spy200.closes, 50);
    const curr = spy200.closes[spy200.closes.length - 1];
    const rsi = calcRSI(spy50.closes);
    const regime = curr > ma200 && curr > ma50 && rsi > 50 ? '🟢 Bull Market' : curr < ma200 && curr < ma50 ? '🔴 Bear Market' : '🟡 Transition/Sideways';
    return `משטר שוק — S&P 500\n${regime}\nSPX: ${curr?.toFixed(0)||'N/A'} | MA50: ${ma50?.toFixed(0)||'N/A'} | MA200: ${ma200?.toFixed(0)||'N/A'}\nRSI(14): ${rsi?.toFixed(1)||'N/A'}\n*Bull = מחיר מעל MA50 וMA200, RSI>50*`;
}

async function getSectorRotation() {
    const [xly, xlp, xle, xlv] = await Promise.all([
        getYFSymbol('XLY'), getYFSymbol('XLP'), getYFSymbol('XLE'), getYFSymbol('XLV')
    ]);
    const cycl = ((xly?.chg||0) + (xle?.chg||0)) / 2;
    const def  = ((xlp?.chg||0) + (xlv?.chg||0)) / 2;
    const signal = cycl > def + 0.3 ? '🔄 כסף זורם לסקטורים מחזוריים (סימן חיובי)' : def > cycl + 0.3 ? '🛡️ כסף זורם לסקטורים דפנסיביים (זהירות)' : '⚖️ ללא כיוון ברור';
    return `Sector Rotation\n${signal}\nמחזוריים (XLY+XLE): ${cycl.toFixed(2)}%\nדפנסיביים (XLP+XLV): ${def.toFixed(2)}%`;
}

async function getCurrencyPairs() {
    const pairs = [['EURUSD=X','EUR/USD'],['GBPUSD=X','GBP/USD'],['USDJPY=X','USD/JPY'],['USDCNY=X','USD/CNY'],['USDILS=X','USD/ILS'],['EURILS=X','EUR/ILS'],['DX-Y.NYB','DXY']];
    const results = await Promise.all(pairs.map(([s]) => getYFSymbol(s)));
    const lines = results.map((d, i) => d ? `${pairs[i][1]}: ${d.price?.toFixed(4)||'N/A'} (${d.chg > 0 ? '+' : ''}${d.chg||'N/A'}%)` : null).filter(Boolean);
    return `שערי חליפין\n${lines.join('\n')}`;
}

async function getBetaAnalysis(sym) {
    const d = await yf(sym, 'defaultKeyStatistics,summaryDetail');
    const beta = d?.defaultKeyStatistics?.beta?.raw;
    if (!beta) return `${sym.toUpperCase()}: אין נתוני Beta`;
    const interp = beta > 1.5 ? '🔥 תנודתי מאוד (>1.5x שוק)' : beta > 1 ? '📈 תנודתי (מגביר תנועות שוק)' : beta > 0.5 ? '➡️ פחות תנודתי מהשוק' : beta > 0 ? '🛡️ דפנסיבי (<0.5)' : '↔️ Beta שלילי (הפוך לשוק)';
    return `Beta — ${sym.toUpperCase()}\nBeta: ${beta.toFixed(2)}\n${interp}\n*Beta=1.5 → S&P עולה 1% → המניה עולה 1.5%*`;
}

async function getStockScore(sym) {
    let score = 0, details = [];
    try {
        const d = await yf(sym, 'financialData,defaultKeyStatistics,summaryDetail');
        const fd = d?.financialData, k = d?.defaultKeyStatistics, s = d?.summaryDetail;
        const pe = s?.trailingPE?.raw, roe = fd?.returnOnEquity?.raw;
        const fcf = fd?.freeCashflow?.raw, growth = fd?.revenueGrowth?.raw;
        const de = fd?.debtToEquity?.raw, margins = fd?.profitMargins?.raw;
        if (pe && pe < 25 && pe > 0) { score += 15; details.push('✅ P/E סביר'); }
        if (roe && roe > 0.15) { score += 20; details.push('✅ ROE>15%'); }
        if (fcf && fcf > 0) { score += 15; details.push('✅ FCF חיובי'); }
        if (growth && growth > 0.1) { score += 15; details.push('✅ צמיחה>10%'); }
        if (de && de < 100) { score += 15; details.push('✅ חוב נמוך'); }
        if (margins && margins > 0.1) { score += 20; details.push('✅ מרווח נטו>10%'); }
        const grade = score >= 80 ? 'A — מעולה' : score >= 60 ? 'B — טוב' : score >= 40 ? 'C — בינוני' : 'D — חלש';
        return `ציון מניה — ${sym.toUpperCase()}\n${score}/100 | ${grade}\n\n${details.join('\n')}`;
    } catch { return `לא ניתן לחשב ציון עבור ${sym}`; }
}

// ─── MULTI-TIMEFRAME ANALYSIS ─────────────────────────────────────────────────

async function getMTFTechnical(sym) {
    const [data6m, data1y, data2y] = await Promise.all([
        fetchAllPriceData(sym, '6mo'),
        fetchAllPriceData(sym, '1y'),
        fetchAllPriceData(sym, '2y'),
    ]);

    const curr = data6m.closes[data6m.closes.length - 1];

    // SHORT TERM (1-4 weeks)
    const rsiShort = calcRSI(data6m.closes.slice(-30));
    const stoch = calcStochastic(data6m.highs.slice(-30), data6m.lows.slice(-30), data6m.closes.slice(-30));
    const ema20 = calcEMA(data6m.closes, 20);
    const roc1m = calcROC(data6m.closes.slice(-22), 21);
    const shortSignals = [
        rsiShort && rsiShort < 40 ? 1 : rsiShort > 60 ? -1 : 0,
        stoch?.k < 30 ? 1 : stoch?.k > 70 ? -1 : 0,
        curr > ema20 ? 1 : -1,
        roc1m > 0 ? 1 : -1,
    ].filter(x => x !== 0);
    const shortScore = shortSignals.reduce((a, b) => a + b, 0);
    const shortSignal = shortScore > 1 ? '🟢 Bullish' : shortScore < -1 ? '🔴 Bearish' : '⚪ ניטרלי';

    // MEDIUM TERM (1-3 months)
    const rsiMed = calcRSI(data6m.closes);
    const ema50 = calcEMA(data1y.closes, 50);
    const macd = calcMACD(data6m.closes);
    const roc3m = calcROC(data1y.closes.slice(-66), 65);
    const medSignals = [
        rsiMed && rsiMed < 45 ? 1 : rsiMed > 55 ? -1 : 0,
        curr > ema50 ? 1 : -1,
        macd?.histogram > 0 ? 1 : -1,
        roc3m > 0 ? 1 : -1,
    ].filter(x => x !== 0);
    const medScore = medSignals.reduce((a, b) => a + b, 0);
    const medSignal = medScore > 1 ? '🟢 Bullish' : medScore < -1 ? '🔴 Bearish' : '⚪ ניטרלי';

    // LONG TERM (6-12 months)
    const ema200 = calcEMA(data2y.closes, 200);
    const ema100 = calcEMA(data1y.closes, 100);
    const roc6m = calcROC(data1y.closes, data1y.closes.length - 1);
    const bb = calcBollinger(data1y.closes);
    const longSignals = [
        curr > ema200 ? 1 : -1,
        curr > ema100 ? 1 : -1,
        roc6m > 5 ? 1 : roc6m < -5 ? -1 : 0,
        bb && curr > bb.middle ? 1 : -1,
    ].filter(x => x !== 0);
    const longScore = longSignals.reduce((a, b) => a + b, 0);
    const longSignal = longScore > 1 ? '🟢 Bullish' : longScore < -1 ? '🔴 Bearish' : '⚪ ניטרלי';

    // COMBINED SIGNAL — only decisive when multiple timeframes agree
    const allScores = [shortScore, medScore, longScore];
    const bullCount = allScores.filter(s => s > 0).length;
    const bearCount = allScores.filter(s => s < 0).length;
    let combined, confidence;
    if (bullCount === 3) { combined = '💚 STRONG BUY'; confidence = 'גבוהה'; }
    else if (bullCount === 2) { combined = '🟢 BUY'; confidence = 'בינונית'; }
    else if (bearCount === 3) { combined = '🔴 STRONG SELL'; confidence = 'גבוהה'; }
    else if (bearCount === 2) { combined = '🔴 SELL'; confidence = 'בינונית'; }
    else { combined = '⚪ HOLD / ניטרלי'; confidence = 'נמוכה — טווחים סותרים'; }

    return `ניתוח Multi-Timeframe — ${sym.toUpperCase()}
מחיר: $${curr.toFixed(2)}

⏱️ קצר (1-4 שבועות):  ${shortSignal}
  RSI: ${rsiShort?.toFixed(1)||'N/A'} | Stoch: ${stoch?.k?.toFixed(1)||'N/A'} | EMA20: $${ema20?.toFixed(2)||'N/A'} | ROC1M: ${roc1m?.toFixed(1)||'N/A'}%

📅 בינוני (1-3 חודשים): ${medSignal}
  RSI: ${rsiMed?.toFixed(1)||'N/A'} | EMA50: $${ema50?.toFixed(2)||'N/A'} | MACD Hist: ${macd?.histogram?.toFixed(3)||'N/A'} | ROC3M: ${roc3m?.toFixed(1)||'N/A'}%

📆 ארוך (6-12 חודשים): ${longSignal}
  EMA200: $${ema200?.toFixed(2)||'N/A'} | EMA100: $${ema100?.toFixed(2)||'N/A'} | ROC6M: ${roc6m?.toFixed(1)||'N/A'}%

━━━━━━━━━━━━━━━━━━━━
סיגנל משולב: ${combined}
ביטחון: ${confidence}
*מסקנה רק כשרוב הטווחים מסכימים*`;
}

async function getTrendAlignment(sym) {
    const data = await fetchAllPriceData(sym, '2y');
    const { closes } = data;
    const curr = closes[closes.length - 1];
    const ema20 = calcEMA(closes, 20), ema50 = calcEMA(closes, 50);
    const ema100 = calcEMA(closes, 100), ema200 = calcEMA(closes, 200);
    const ma20ok = curr > ema20, ma50ok = curr > ema50;
    const ma100ok = curr > ema100, ma200ok = curr > ema200;
    const aligned = [ma20ok, ma50ok, ma100ok, ma200ok];
    const bullish = aligned.filter(Boolean).length;
    const trendStr = bullish === 4 ? '💚 Perfectly Bullish' : bullish === 3 ? '🟢 Mostly Bullish' : bullish === 2 ? '⚪ Mixed' : bullish === 1 ? '🟡 Mostly Bearish' : '🔴 Perfectly Bearish';
    return `יישור טרנד — ${sym.toUpperCase()}\n${trendStr} (${bullish}/4)\n\nEMA20: ${ma20ok ? '✅' : '❌'} $${ema20?.toFixed(2)||'N/A'}\nEMA50: ${ma50ok ? '✅' : '❌'} $${ema50?.toFixed(2)||'N/A'}\nEMA100: ${ma100ok ? '✅' : '❌'} $${ema100?.toFixed(2)||'N/A'}\nEMA200: ${ma200ok ? '✅' : '❌'} $${ema200?.toFixed(2)||'N/A'}\n\n*4/4 = טרנד עלייה מושלם | 0/4 = טרנד ירידה חזק*`;
}

module.exports = {
    // Technical
    getStochastic, getATR, getADX, getCCI, getWilliamsR, getOBV,
    getFibonacci, getSupportResistance, getMACross, getPivotPoints,
    getMFI, get52WkAnalysis, getMomentum, getParabolicSAR,
    getHistoricalVolatility, getMAAnalysis,
    // Fundamental
    getValuation, getEarningsDate, getDividend, getAnalystConsensus,
    getPriceTargets, getShortInterest, getInsiderActivity, getProfitability,
    getLiquidity, getGrowthRates, getFCF, getOwnership, getIncomeSummary,
    getBalanceSummary, getGrahamNumber, getDCFSimple, getPiotroski,
    compareStocks, getAltmanZ, getUpgradesDowngrades, getEPSSurprise,
    getRelativeStrength, getBetaAnalysis, getStockScore,
    // Macro
    getVIX, getDXY, getOilPrices, getNaturalGas, getYieldCurve, getYieldSpread,
    getMarketIndices, getSectorPerformance, getWorldIndices, getCommoditiesAll,
    getPreciousMetals, getRiskOnOff, getInflationBreakeven, getUSMacro,
    getIsraelMacro, getEmergingMarkets, getCryptoMarket, getGlobalRates,
    getFearGreed, getBuffettIndicator, getMarketRegime, getSectorRotation,
    getCurrencyPairs,
    // Multi-timeframe
    getMTFTechnical, getTrendAlignment,
};
