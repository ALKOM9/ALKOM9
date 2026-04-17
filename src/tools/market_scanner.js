// market_scanner.js — Full US Market Scanner (Long-only recommendations)
// Universe: ~500 strongest US stocks (full S&P 500 + top growth stocks outside index)
// 3-stage funnel: Quick Screen (~500) → MTF Technical (top 25) → Deep Analysis + Entry/Exit (top 8)

const { calcRSI, calcEMA, calcMACD, calcSMA } = require('./technicals');

// ─── Universe: ~500 strongest US stocks (full S&P 500 + high-quality growth) ──
const UNIVERSE = [
    // ── Mega-cap / Magnificent 7 ──────────────────────────────────────────────
    'AAPL','MSFT','NVDA','GOOGL','GOOG','META','AMZN','TSLA','AVGO','ORCL',

    // ── Semiconductors ────────────────────────────────────────────────────────
    'AMD','QCOM','TXN','AMAT','LRCX','KLAC','MU','MRVL','ADI','MCHP',
    'ON','SWKS','QRVO','ENTG','MPWR','KEYS','CDNS','SNPS','ANSS','COHR',
    'WOLF','CRUS','MTSI','RMBS','SLAB','AMBA','ALGM','DIOD','VICR','SITM',

    // ── Software / Enterprise ─────────────────────────────────────────────────
    'CRM','ADBE','NOW','INTU','PANW','CSCO','IBM','ACN','CTSH','IT',
    'WDAY','VEEV','TEAM','HUBS','PAYC','PTC','EPAM','GDDY','MANH','PCTY',
    'TOST','CWAN','RAMP','ALTR','BSY','DAVA','DV','EFX','VRSN','FFIV',

    // ── Cybersecurity ─────────────────────────────────────────────────────────
    'CRWD','FTNT','ZS','PANW','S','OKTA','TENB','RPM','CHKP','VRNS',
    'QLYS','CYBR','SAIL','ACIW','EVTC',

    // ── Cloud / SaaS / AI ─────────────────────────────────────────────────────
    'PLTR','SNOW','DDOG','NET','MDB','GTLB','AI','PATH','SMAR','FIVN',
    'APPF','NCNO','PCOR','BRZE','CFLT','ESTC','SUMO','SPSC','FORR',
    'ARM','APP','IOT','SMCI','MSTR','HOOD',

    // ── Internet / Consumer Tech ──────────────────────────────────────────────
    'NFLX','UBER','ABNB','BKNG','EXPE','DASH','LYFT','SPOT','PINS','SNAP',
    'YELP','ANGI','TRIP','OPEN','CARG','IAC','CARS','TCOM',

    // ── Payments / Fintech ────────────────────────────────────────────────────
    'V','MA','PYPL','SQ','FIS','FISV','GPN','WEX','WU','RPAY',
    'AFRM','NU','SOFI','UPST','BILL','FLYW','RELY','COOP','UWMC',

    // ── Big Banks ─────────────────────────────────────────────────────────────
    'JPM','BAC','WFC','GS','MS','C','USB','PNC','TFC','COF',
    'BK','STT','SCHW','IBKR','RF','HBAN','CFG','KEY','MTB','ZION',

    // ── Capital Markets / Asset Managers ─────────────────────────────────────
    'BX','KKR','APO','ARES','CG','BLK','MSCI','SPGI','MCO','ICE','CME',
    'NDAQ','CBOE','FDS','AMG','IVZ','WDR','VCTR','HLNE',

    // ── Insurance ─────────────────────────────────────────────────────────────
    'AXP','MET','PRU','AFL','ALL','PGR','TRV','CB','AIG','HIG','GL',
    'LNC','UNM','BRK-B','RNR','RE','EG','WRB','RYAN','ACGL',

    // ── Healthcare / Big Pharma ───────────────────────────────────────────────
    'LLY','JNJ','ABBV','MRK','PFE','UNH','CI','CVS','HUM','ELV',
    'CNC','MOH','HCA','UHS','THC','ENSG','AMED',

    // ── Medical Devices ───────────────────────────────────────────────────────
    'TMO','ABT','DHR','BSX','MDT','SYK','EW','ZBH','BAX','BDX',
    'ISRG','HOLX','ALGN','IDXX','IQV','CRL','A','MTD','PODD','DXCM',
    'GEHC','NVST','OMCL','ITGR','LMAT','INSP','SWAV','AXNX','IRTC',

    // ── Biotech ───────────────────────────────────────────────────────────────
    'REGN','GILD','MRNA','AMGN','BIIB','VRTX','BMY','INCY','SGEN','ALNY',
    'ARGX','ROIV','RXRX','IMVT','KYMR','CGON','NTLA','BEAM','VERV',
    'RARE','FOLD','ACAD','NKTR','SAGE','MRUS','PRTA',

    // ── Consumer Discretionary ────────────────────────────────────────────────
    'HD','LOW','MCD','SBUX','NKE','LULU','TJX','ROST','CMG','YUM',
    'DPZ','EAT','TXRH','SHAK','CAVA','WEN','QSR','JACK',
    'DHI','LEN','PHM','TOL','NVR','MDC','KBH','MHO','SKY',
    'TSCO','DG','DLTR','BJ','FIVE','OLLI','BTI','CASY',
    'F','GM','APTV','LEA','BWA','GNTX','FOX','SNA','LKQ',

    // ── Luxury / Apparel ──────────────────────────────────────────────────────
    'DECK','SKX','ONON','CROX','HBI','PVH','TPR','CPRI','RH','WSM',
    'ETSY','EBAY','W','REAL','RVLV','RENT',

    // ── Consumer Staples ──────────────────────────────────────────────────────
    'WMT','COST','PG','KO','PEP','PM','MO','KMB','CL','MDLZ',
    'GIS','K','CPB','HSY','MKC','SJM','CAG','CHD','CLX','EL',
    'ULTA','COTY','IPAR','ELF','SFM',

    // ── Energy ────────────────────────────────────────────────────────────────
    'XOM','CVX','COP','EOG','SLB','MPC','PSX','VLO','HES','DVN',
    'FANG','OXY','HAL','BKR','APA','MRO','RRC','AR','EQT','CNX',
    'NOG','DINO','SM','CIVI','MGY','MTDR',

    // ── Industrials / Aerospace & Defense ────────────────────────────────────
    'CAT','DE','HON','RTX','LMT','BA','GE','GEV','ETN','EMR',
    'ROK','PH','ITW','MMM','AME','IEX','FAST','GWW','SWK','ROP',
    'VRSK','TT','JCI','CARR','OTIS','IR','GNRC','BLDR','VMI','AAON',
    'HWM','SPR','TDG','HEI','KTOS','RCAT','ACHR','JOBY',

    // ── Transportation / Logistics ────────────────────────────────────────────
    'UPS','FDX','UNP','CSX','NSC','ODFL','JBHT','CHRW','XPO',
    'EXPD','SAIA','ARCB','WERN','LSTR','HUBG',

    // ── Waste / Environment ───────────────────────────────────────────────────
    'WM','RSG','CWST','SRCL','CLH',

    // ── Materials ─────────────────────────────────────────────────────────────
    'LIN','APD','SHW','PPG','NEM','FCX','NUE','STLD','X','AA',
    'ATI','MLM','VMC','MOS','CF','IFF','ECL','CE','HUN','EMN',
    'RPM','OLN','AXTA','IOSP','TPC',

    // ── Utilities ─────────────────────────────────────────────────────────────
    'NEE','DUK','SO','D','AEP','EXC','XEL','SRE','ES','PEG',
    'WEC','ED','DTE','ETR','EIX','PPL','AEE','CMS','NI','LNT',
    'EVRG','NRG','VST','CEG','CWEN','AES',

    // ── Clean Energy ─────────────────────────────────────────────────────────
    'FSLR','ENPH','SEDG','RUN','ARRY','NOVA','SPWR','CSIQ',

    // ── REITs ────────────────────────────────────────────────────────────────
    'AMT','PLD','EQIX','CCI','SPG','PSA','EQR','AVB','MAA','O',
    'VICI','GLPI','WELL','VTR','PEAK','KIM','REG','FRT','NNN','STOR',
    'COLD','REXR','ELS','SUI','UDR','ESS','CPT',

    // ── Telecom / Media ───────────────────────────────────────────────────────
    'T','VZ','TMUS','CMCSA','CHTR','DIS','WBD','PARA','NWSA',
    'OMC','IPG','TTD','MGNI','PUBM','IAS',

    // ── Data / Cloud Infrastructure ───────────────────────────────────────────
    'EQIX','DLR','CONE','LFST','GLBE','WEX','DFIN',

    // ── High-Momentum Growth (outside S&P 500) ────────────────────────────────
    'COIN','MSTR','CELH','AXON','DUOL','HIMS','ELF','TMDX','IOT',
    'MNDY','GTLB','BILL','DKNG','PENN','RSI','FLUT',
    'SE','MELI','NU','GRAB','RELY','COOP',
    'RIVN','LCID','NIO','LI','XPEV',
    'RBLX','U','BMBL','MTCH','IAC',

    // ── ETFs (excluded from picks, included for market context) ───────────────
    'SPY','QQQ','IWM','XLK','XLF','XLV','XLE','XLI','XLY','XLP',
];

// Deduplicate
const _seen = new Set();
const UNIVERSE_DEDUP = UNIVERSE.filter(s => { if (_seen.has(s)) return false; _seen.add(s); return true; });

// Stocks to exclude from picks (ETFs only)
const ETF_BLACKLIST = new Set([
    'SPY','QQQ','IWM','XLK','XLF','XLV','XLE','XLI','XLY','XLP',
]);

// ─── Cache ────────────────────────────────────────────────────────────────────
let _cache = null;
let _cacheTime = 0;
const CACHE_TTL = 4 * 60 * 60 * 1000; // 4 hours

// ─── Yahoo Finance helpers (with crumb support) ───────────────────────────────
let _crumb = null, _cookie = null, _crumbExp = 0;

async function _ensureCrumb() {
    if (_crumb && Date.now() < _crumbExp) return;
    try {
        const r1 = await fetch('https://fc.yahoo.com', {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
            redirect: 'follow', signal: AbortSignal.timeout(6000),
        });
        const raw = r1.headers.get('set-cookie') || '';
        const m = raw.match(/A[13]=([^;]+)/);
        _cookie = m ? `A3=${m[1]}` : raw.split(';')[0];
        const r2 = await fetch('https://query2.finance.yahoo.com/v1/test/getcrumb', {
            headers: { 'User-Agent': 'Mozilla/5.0', 'Cookie': _cookie },
            signal: AbortSignal.timeout(6000),
        });
        if (r2.ok) { _crumb = (await r2.text()).trim(); _crumbExp = Date.now() + 30 * 60 * 1000; }
    } catch (_) {}
}

function _yfUrl(base) {
    return _crumb ? `${base}${base.includes('?') ? '&' : '?'}crumb=${encodeURIComponent(_crumb)}` : base;
}

function _headers() {
    return { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Cookie': _cookie || '' };
}

// Fetch basic price data for a symbol (lightweight — 1mo chart)
async function quickFetch(sym, retry = true) {
    try {
        await _ensureCrumb();
        const url = _yfUrl(`https://query2.finance.yahoo.com/v8/finance/chart/${sym}?interval=1d&range=1y`);
        const res = await fetch(url, { headers: _headers(), signal: AbortSignal.timeout(10000) });
        if (res.status === 401 && retry) { _crumbExp = 0; return quickFetch(sym, false); }
        if (!res.ok) return null;
        const d = await res.json();
        const r = d?.chart?.result?.[0];
        if (!r) return null;
        const closes = (r.indicators?.quote?.[0]?.close || []).filter(c => c != null);
        const volumes = (r.indicators?.quote?.[0]?.volume || []).filter(v => v != null);
        if (closes.length < 20) return null;
        return { sym, closes, volumes, meta: r.meta };
    } catch { return null; }
}

// ─── Stage 1: Quick Screen ────────────────────────────────────────────────────
// Score each stock on simple criteria — fast parallel scan
async function quickScore(data) {
    if (!data) return null;
    const { sym, closes, volumes, meta } = data;
    const curr = closes[closes.length - 1];
    const prev20 = closes[closes.length - 21] || closes[0];
    const prev60 = closes[closes.length - 61] || closes[0];
    const prev5  = closes[closes.length - 6]  || closes[0];

    // RSI
    const rsi = calcRSI(closes, 14);

    // EMAs
    const ema20  = calcEMA(closes, 20);
    const ema50  = calcEMA(closes, 50);
    const ema200 = calcEMA(closes, 200);

    // Momentum
    const mom1m  = prev20  ? ((curr - prev20) / prev20) * 100  : 0;
    const mom3m  = prev60  ? ((curr - prev60) / prev60) * 100  : 0;
    const mom1w  = prev5   ? ((curr - prev5)  / prev5)  * 100  : 0;

    // 52-week range position (0-100%)
    const allCloses = closes.slice(-252);
    const hi52  = Math.max(...allCloses);
    const lo52  = Math.min(...allCloses);
    const range52 = hi52 !== lo52 ? ((curr - lo52) / (hi52 - lo52)) * 100 : 50;

    // Volume trend (avg last 5d vs avg last 20d)
    const avgVol5  = volumes.slice(-5).reduce((a, b) => a + b, 0) / 5;
    const avgVol20 = volumes.slice(-20).reduce((a, b) => a + b, 0) / 20;
    const volTrend = avgVol20 > 0 ? avgVol5 / avgVol20 : 1;

    // Scoring
    let score = 0;
    const reasons = [];

    // RSI sweet spot: 45-70 = momentum without being overbought
    if (rsi >= 45 && rsi <= 70)  { score += 3; reasons.push(`RSI ${rsi?.toFixed(0)} ✅`); }
    else if (rsi < 45 && rsi > 30) { score += 1; reasons.push(`RSI ${rsi?.toFixed(0)} ⚠️`); }
    else if (rsi > 70)             { score -= 1; reasons.push(`RSI ${rsi?.toFixed(0)} 🔴 overbought`); }

    // Above key MAs
    if (ema200 && curr > ema200) { score += 3; reasons.push('מעל EMA200 ✅'); }
    else                         { score -= 2; reasons.push('מתחת EMA200 ❌'); }
    if (ema50 && curr > ema50)   { score += 2; reasons.push('מעל EMA50'); }
    if (ema20 && curr > ema20)   { score += 1; reasons.push('מעל EMA20'); }

    // Momentum
    if (mom1m > 3)  { score += 2; reasons.push(`+${mom1m.toFixed(1)}% חודש`); }
    if (mom1m < -8) { score -= 2; }
    if (mom3m > 8)  { score += 2; reasons.push(`+${mom3m.toFixed(1)}% 3M`); }
    if (mom3m < -15){ score -= 2; }
    if (mom1w > 1)  { score += 1; }

    // Position in 52-week range: prefer 40-85%
    if (range52 >= 40 && range52 <= 85) { score += 2; }
    else if (range52 > 85)              { score -= 1; } // near peak
    else if (range52 < 25)              { score -= 2; } // downtrend

    // Volume confirmation
    if (volTrend > 1.2) { score += 1; reasons.push('נפח עולה'); }

    // Minimum price filter (no penny stocks)
    if (curr < 5) return null;

    return {
        sym, score, curr, rsi, ema200, ema50, mom1m, mom3m, range52, reasons,
        hi52, lo52,
    };
}

// ─── Stage 2: MTF Technical (on top 20) ──────────────────────────────────────
async function mtfScore(sym, closes) {
    try {
        // Short (1-4 weeks): last 30 bars
        const short = closes.slice(-30);
        const rsiShort = calcRSI(short, 14);
        const ema9s = calcEMA(short, 9);
        const ema21s = calcEMA(short, 21);
        const shortBull = (rsiShort >= 50) + (ema9s > ema21s);

        // Medium (1-3 months): last 90 bars
        const med = closes.slice(-90);
        const rsiMed = calcRSI(med, 14);
        const macdMed = calcMACD(med, 12, 26, 9);
        const ema50m = calcEMA(closes, 50);
        const curr = closes[closes.length - 1];
        const medBull = (rsiMed >= 50) + (macdMed?.histogram > 0) + (curr > ema50m);

        // Long (6-12 months): full data
        const rsiLong = calcRSI(closes, 14);
        const ema200l = calcEMA(closes, 200);
        const ema100l = calcEMA(closes, 100);
        const longBull = (curr > ema200l) + (curr > ema100l) + (rsiLong > 45);

        // Score: 0-9
        const total = shortBull + medBull + longBull;
        const combined = total >= 8 ? '🟢 STRONG BUY' : total >= 6 ? '🟢 BUY' : total >= 4 ? '⚪ NEUTRAL' : '🔴 AVOID';

        return {
            sym, mtfScore: total, combined,
            short: { rsi: rsiShort, signal: shortBull >= 2 ? 'bullish' : shortBull === 1 ? 'mixed' : 'bearish' },
            medium: { rsi: rsiMed, signal: medBull >= 2 ? 'bullish' : medBull === 1 ? 'mixed' : 'bearish' },
            long:   { signal: longBull >= 2 ? 'bullish' : longBull === 1 ? 'mixed' : 'bearish' },
            ema200: calcEMA(closes, 200), ema50: ema50m, curr,
        };
    } catch { return null; }
}

// ─── Stage 3: Entry / Exit / Stop ────────────────────────────────────────────
function calcEntryExit(closes, meta, analystTarget) {
    const curr = closes[closes.length - 1];
    const hi52 = Math.max(...closes.slice(-252));
    const lo52 = Math.min(...closes.slice(-252));

    // Fibonacci retracements from 52-week swing
    const swing = hi52 - lo52;
    const fib618 = hi52 - swing * 0.618; // strong support
    const fib50  = hi52 - swing * 0.5;
    const fib382 = hi52 - swing * 0.382;

    // Support: highest fib level still below current price
    let entry = null;
    if (curr > fib618) entry = fib618;
    else if (curr > fib50) entry = fib50;
    else entry = fib382;

    // If current price is close to entry (within 3%), use current as entry
    const entryFinal = Math.abs(curr - entry) / curr < 0.03 ? curr : Math.max(entry, curr * 0.97);

    // ATR for stop
    const highs  = (closes.map((c, i) => i === 0 ? c : Math.max(c, closes[i - 1])));
    const lows   = (closes.map((c, i) => i === 0 ? c : Math.min(c, closes[i - 1])));
    const trs    = closes.map((c, i) => i === 0 ? 0 : Math.max(highs[i] - lows[i], Math.abs(highs[i] - closes[i - 1]), Math.abs(lows[i] - closes[i - 1])));
    const atr14  = trs.slice(-14).reduce((a, b) => a + b, 0) / 14;

    const stop = entryFinal - atr14 * 2; // 2x ATR stop

    // Exit: analyst target OR fibonacci resistance OR 52-week high (if under it)
    let exit = null;
    if (analystTarget && analystTarget > curr * 1.05) {
        exit = analystTarget;
    } else if (curr < hi52 * 0.95) {
        exit = hi52; // aiming for 52-week high
    } else {
        exit = curr + swing * 0.382; // next fib extension
    }

    const riskReward = stop > 0 && exit > entryFinal
        ? ((exit - entryFinal) / (entryFinal - stop)).toFixed(1) : null;

    return {
        entry: entryFinal.toFixed(2),
        exit:  exit?.toFixed(2),
        stop:  stop.toFixed(2),
        riskReward,
        atr:   atr14.toFixed(2),
    };
}

// ─── Fundamental quick fetch (Yahoo quoteSummary) ─────────────────────────────
async function getFundamentals(sym) {
    try {
        await _ensureCrumb();
        const modules = 'defaultKeyStatistics,financialData,recommendationTrend';
        const url = _yfUrl(`https://query2.finance.yahoo.com/v10/finance/quoteSummary/${sym}?modules=${modules}`);
        const res = await fetch(url, { headers: _headers(), signal: AbortSignal.timeout(10000) });
        if (!res.ok) return null;
        const d = await res.json();
        const r = d?.quoteSummary?.result?.[0];
        if (!r) return null;

        const fin  = r.financialData || {};
        const stat = r.defaultKeyStatistics || {};
        const rec  = r.recommendationTrend?.trend?.[0] || {};

        const totalRec  = (rec.strongBuy || 0) + (rec.buy || 0) + (rec.hold || 0) + (rec.sell || 0) + (rec.strongSell || 0);
        const bullishRec = (rec.strongBuy || 0) + (rec.buy || 0);
        const buyPct = totalRec > 0 ? ((bullishRec / totalRec) * 100).toFixed(0) : null;

        return {
            targetPrice:    fin.targetMeanPrice?.raw,
            currentPrice:   fin.currentPrice?.raw,
            upside:         fin.targetMeanPrice?.raw && fin.currentPrice?.raw
                ? (((fin.targetMeanPrice.raw - fin.currentPrice.raw) / fin.currentPrice.raw) * 100).toFixed(1)
                : null,
            revenueGrowth:  fin.revenueGrowth?.raw ? (fin.revenueGrowth.raw * 100).toFixed(1) : null,
            grossMargin:    fin.grossMargins?.raw   ? (fin.grossMargins.raw * 100).toFixed(1)  : null,
            debtToEquity:   fin.debtToEquity?.raw,
            roe:            fin.returnOnEquity?.raw ? (fin.returnOnEquity.raw * 100).toFixed(1) : null,
            trailingPE:     stat.trailingPE?.raw,
            fwdPE:          stat.forwardPE?.raw,
            buyPct,
            totalRec,
        };
    } catch { return null; }
}

// ─── Rate-limited parallel fetch ─────────────────────────────────────────────
async function batchProcess(items, fn, concurrency = 10, delayMs = 100) {
    const results = [];
    for (let i = 0; i < items.length; i += concurrency) {
        const chunk = items.slice(i, i + concurrency);
        const chunkRes = await Promise.all(chunk.map(fn));
        results.push(...chunkRes);
        if (i + concurrency < items.length) await new Promise(r => setTimeout(r, delayMs));
    }
    return results;
}

// ─── Main Scanner ─────────────────────────────────────────────────────────────
async function scanMarket(forceRefresh = false) {
    // Cache check
    if (!forceRefresh && _cache && Date.now() < _cacheTime) {
        return _cache;
    }

    console.log('  🔍 Market scan starting — Stage 1: Quick screen...');

    // ── Stage 1: Fetch all ~500 stocks (15 at a time) ──
    const rawData = await batchProcess(
        UNIVERSE_DEDUP,
        sym => quickFetch(sym),
        15, 120,
    );

    // Score all
    const scored = (await Promise.all(rawData.map(d => d ? quickScore(d) : null)))
        .filter(Boolean)
        .filter(s => !ETF_BLACKLIST.has(s.sym))
        .sort((a, b) => b.score - a.score);

    console.log(`  📊 Stage 1 done: ${scored.length} stocks scored. Top 25 → Stage 2...`);

    // ── Stage 2: MTF Technical on top 25 ──
    const top20 = scored.slice(0, 25);
    const top20Data = rawData.filter(d => d && top20.some(s => s.sym === d.sym));

    const mtfResults = await batchProcess(
        top20Data,
        d => mtfScore(d.sym, d.closes),
        8, 150,
    );

    // Merge MTF scores with quick scores
    const merged = top20.map(qs => {
        const mtf = mtfResults.find(m => m?.sym === qs.sym);
        return {
            ...qs,
            mtfScore: mtf?.mtfScore || 0,
            mtfCombined: mtf?.combined || '❓',
            mtfShort:  mtf?.short,
            mtfMedium: mtf?.medium,
            mtfLong:   mtf?.long,
            ema200: mtf?.ema200,
            ema50:  mtf?.ema50,
        };
    }).sort((a, b) => (b.score + b.mtfScore) - (a.score + a.mtfScore));

    // Filter: only BUY or STRONG BUY signals from MTF
    const topCandidates = merged.filter(s =>
        s.mtfCombined.includes('BUY') || s.mtfScore >= 5
    ).slice(0, 8);

    console.log(`  🏆 Stage 2 done: ${topCandidates.length} BUY candidates → Stage 3 (fundamentals + entry/exit)...`);

    // ── Stage 3: Fundamentals + Entry/Exit on top 8 ──
    const finalData = rawData.filter(d => d && topCandidates.some(s => s.sym === d.sym));

    const fundamentals = await batchProcess(
        topCandidates.map(s => s.sym),
        sym => getFundamentals(sym),
        4, 250,
    );

    // Build final results
    const results = topCandidates.map((s, i) => {
        const fd = fundamentals[i];
        const priceData = finalData.find(d => d?.sym === s.sym);
        const closes = priceData?.closes || [];
        const entryExit = closes.length > 20
            ? calcEntryExit(closes, priceData?.meta, fd?.targetPrice)
            : null;

        // Fundamental score
        let fundScore = 0;
        if (fd?.buyPct && +fd.buyPct >= 70)  fundScore += 3;
        if (fd?.upside && +fd.upside > 15)   fundScore += 2;
        if (fd?.revenueGrowth && +fd.revenueGrowth > 5) fundScore += 2;
        if (fd?.grossMargin && +fd.grossMargin > 40)     fundScore += 1;
        if (fd?.debtToEquity && fd.debtToEquity < 1.5)  fundScore += 1;

        const totalScore = s.score + s.mtfScore + fundScore;

        return {
            sym: s.sym,
            totalScore,
            curr: s.curr,
            mtfSignal: s.mtfCombined,
            mtfScore:  s.mtfScore,
            fundScore,
            reasons:   s.reasons,
            // Technicals
            rsi:     s.rsi,
            mom1m:   s.mom1m,
            mom3m:   s.mom3m,
            range52: s.range52,
            ema200:  s.ema200,
            ema50:   s.ema50,
            // Fundamentals
            targetPrice:   fd?.targetPrice,
            upside:        fd?.upside,
            revenueGrowth: fd?.revenueGrowth,
            grossMargin:   fd?.grossMargin,
            buyPct:        fd?.buyPct,
            fwdPE:         fd?.fwdPE,
            // Entry/Exit
            entry:       entryExit?.entry,
            exit:        entryExit?.exit,
            stop:        entryExit?.stop,
            riskReward:  entryExit?.riskReward,
            atr:         entryExit?.atr,
        };
    }).sort((a, b) => b.totalScore - a.totalScore);

    console.log(`  ✅ Market scan complete! Top pick: ${results[0]?.sym}`);

    // Save to cache
    _cache = results;
    _cacheTime = Date.now() + CACHE_TTL;

    return results;
}

// ─── Formatted Output ─────────────────────────────────────────────────────────
async function getMarketScan(limit = 5) {
    const results = await scanMarket();
    if (!results || results.length === 0) {
        return '⚠️ לא הצלחתי לסרוק את השוק כרגע. נסה שוב עוד כמה דקות.';
    }

    const top = results.slice(0, limit);
    const lines = [`🔍 סריקת שוק — ${new Date().toLocaleDateString('he-IL')} (${top.length} המלצות מובילות)`, ''];

    top.forEach((s, i) => {
        const medal = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][i] || `${i + 1}.`;
        lines.push(`${medal} ${s.sym} — $${s.curr?.toFixed(2)} | ${s.mtfSignal}`);
        lines.push(`   ציון: ${s.totalScore} (טכני ${s.mtfScore}/9 | פונד. ${s.fundScore}/9)`);

        if (s.entry && s.exit && s.stop) {
            lines.push(`   📈 כניסה: $${s.entry} | יעד: $${s.exit} | סטופ: $${s.stop}`);
            if (s.riskReward) lines.push(`   ⚖️ Risk/Reward: 1:${s.riskReward}`);
        }

        const details = [];
        if (s.rsi)          details.push(`RSI ${s.rsi?.toFixed(0)}`);
        if (s.mom1m != null) details.push(`+${s.mom1m?.toFixed(1)}% חודש`);
        if (s.upside)       details.push(`upside ${s.upside}%`);
        if (s.buyPct)       details.push(`${s.buyPct}% אנליסטים קונים`);
        if (details.length) lines.push(`   ${details.join(' | ')}`);
        lines.push('');
    });

    lines.push('⚠️ זה לא ייעוץ השקעות — ניתוח טכני/פונדמנטלי בלבד.');
    return lines.join('\n');
}

module.exports = { scanMarket, getMarketScan };
