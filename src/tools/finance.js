// Finance tools: forex, gold, TASE, crypto portfolio, calculators

async function getForex(pair) {
    try {
        const cleaned = pair.toUpperCase().replace(/\s+/g, '').replace('-', '/');
        const parts = cleaned.split('/');
        const from = parts[0];
        const to = parts[1] || 'ILS';
        if (!from || !to) return `זוג מטבעות לא תקין: ${pair}`;

        const res = await fetch(`https://open.er-api.com/v6/latest/${from}`, {
            signal: AbortSignal.timeout(8000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        if (d.result !== 'success') return null;
        const rate = d.rates?.[to];
        if (!rate) return `לא נמצא שער ל-${from}/${to}`;

        const commonPairs = { ILS: '₪', USD: '$', EUR: '€', GBP: '£', JPY: '¥', TRY: '₺' };
        const toSymbol = commonPairs[to] || to;
        const ilsExtra = to !== 'ILS' && d.rates?.ILS
            ? `\n1 ${from} = ₪${(rate * (d.rates.ILS / rate)).toFixed(3)}` : '';

        return `💱 ${from}/${to}: ${rate.toFixed(4)}\n1 ${from} = ${toSymbol}${rate.toFixed(4)}${ilsExtra}`;
    } catch (e) { return `שגיאה: ${e.message}`; }
}

async function getGoldPrice() {
    try {
        const [goldRes, rateRes] = await Promise.allSettled([
            fetch('https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=1d', {
                headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000)
            }),
            fetch('https://open.er-api.com/v6/latest/USD', { signal: AbortSignal.timeout(5000) })
        ]);

        let priceUSD = null, ilsRate = 3.7;
        if (goldRes.status === 'fulfilled' && goldRes.value.ok) {
            const d = await goldRes.value.json();
            const meta = d?.chart?.result?.[0]?.meta;
            if (meta?.regularMarketPrice) {
                priceUSD = meta.regularMarketPrice;
                const prev = meta.chartPreviousClose;
                const chg = prev ? ((priceUSD - prev) / prev * 100).toFixed(2) : null;
                if (rateRes.status === 'fulfilled' && rateRes.value.ok) {
                    const rd = await rateRes.value.json();
                    ilsRate = rd.rates?.ILS || 3.7;
                }
                const priceILS = (priceUSD * ilsRate).toFixed(0);
                let r = `🥇 זהב: $${priceUSD.toLocaleString()}`;
                if (chg !== null) r += ` (${chg > 0 ? '+' : ''}${chg}%)`;
                r += `\n₪${Number(priceILS).toLocaleString()} לאונקיה`;
                return r;
            }
        }
        return null;
    } catch { return null; }
}

async function getSilverPrice() {
    try {
        const res = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/SI=F?interval=1d&range=1d', {
            headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        const meta = d?.chart?.result?.[0]?.meta;
        if (!meta?.regularMarketPrice) return null;
        const price = meta.regularMarketPrice;
        const prev = meta.chartPreviousClose;
        const chg = prev ? ((price - prev) / prev * 100).toFixed(2) : null;
        return `🥈 כסף: $${price} לאונקיה${chg !== null ? ` (${chg > 0 ? '+' : ''}${chg}%)` : ''}`;
    } catch { return null; }
}

async function getTASEStock(symbol) {
    try {
        const sym = symbol.toUpperCase().endsWith('.TA') ? symbol.toUpperCase() : symbol.toUpperCase() + '.TA';
        const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${sym}?interval=1d&range=1d`, {
            headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(7000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        const meta = d?.chart?.result?.[0]?.meta;
        if (!meta?.regularMarketPrice) return null;
        const price = meta.regularMarketPrice;
        const prev = meta.chartPreviousClose;
        const chg = prev ? ((price - prev) / prev * 100).toFixed(2) : null;
        let r = `📈 ${sym}: ₪${price}`;
        if (chg !== null) r += ` (${chg > 0 ? '+' : ''}${chg}%)`;
        if (meta.regularMarketDayHigh) r += `\nגבוה: ₪${meta.regularMarketDayHigh} | נמוך: ₪${meta.regularMarketDayLow}`;
        return r;
    } catch { return null; }
}

async function getHistoricalPrice(symbol, period) {
    try {
        const sym = symbol.toUpperCase();
        const rangeMap = { '1w': '5d', '1m': '1mo', '3m': '3mo', '1y': '1y', '5y': '5y' };
        const range = rangeMap[period] || '1mo';
        const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${sym}?interval=1d&range=${range}`, {
            headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(8000)
        });
        if (!res.ok) return null;
        const d = await res.json();
        const result = d?.chart?.result?.[0];
        if (!result) return null;
        const closes = result.indicators?.quote?.[0]?.close?.filter(c => c !== null);
        if (!closes || closes.length < 2) return null;
        const first = closes[0];
        const last = closes[closes.length - 1];
        const chg = ((last - first) / first * 100).toFixed(2);
        const meta = result.meta;
        const periodHe = { '1w': 'שבוע', '1m': 'חודש', '3m': '3 חודשים', '1y': 'שנה', '5y': '5 שנים' };
        return `${sym} — ${periodHe[period] || period}:\nמחיר: ${last} ${meta.currency || 'USD'}\nשינוי: ${chg > 0 ? '+' : ''}${chg}%\n52w גבוה: ${meta.fiftyTwoWeekHigh || 'N/A'} | נמוך: ${meta.fiftyTwoWeekLow || 'N/A'}`;
    } catch { return null; }
}

function mortgageCalc(args) {
    const { principal, rate, years } = args;
    if (!principal || !rate || !years) return 'חסרים פרמטרים: principal (קרן), rate (ריבית שנתית %), years (שנים)';
    const p = Number(principal), r = Number(rate), y = Number(years);
    if (isNaN(p) || isNaN(r) || isNaN(y)) return 'ערכים לא תקינים';
    const monthlyRate = (r / 100) / 12;
    const n = y * 12;
    const monthly = monthlyRate === 0
        ? p / n
        : p * (monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1);
    const total = monthly * n;
    const interest = total - p;
    return `💰 משכנתא:\nקרן: ₪${p.toLocaleString()}\nריבית: ${r}% לשנה\nתקופה: ${y} שנים\n\nתשלום חודשי: ₪${Math.round(monthly).toLocaleString()}\nסה"כ תשלום: ₪${Math.round(total).toLocaleString()}\nסה"כ ריבית: ₪${Math.round(interest).toLocaleString()}`;
}

function netSalaryCalc(gross) {
    const g = Number(gross);
    if (isNaN(g) || g <= 0) return 'שכר לא תקין';

    // ביטוח לאומי ובריאות (עובד) - 2024
    const blMax = 7522;
    const bl = g <= blMax ? g * 0.035 : blMax * 0.035 + (g - blMax) * 0.07;
    const health = g <= blMax ? g * 0.031 : blMax * 0.031 + (g - blMax) * 0.05;

    // מס הכנסה — מדרגות 2024 (חודשי)
    const brackets = [
        { up: 8060, rate: 0.10 },
        { up: 11560, rate: 0.14 },
        { up: 20140, rate: 0.20 },
        { up: 43370, rate: 0.31 },
        { up: 56060, rate: 0.35 },
        { up: Infinity, rate: 0.47 }
    ];
    let taxable = g;
    let incomeTax = 0;
    let prev = 0;
    for (const b of brackets) {
        if (taxable <= prev) break;
        incomeTax += (Math.min(taxable, b.up) - prev) * b.rate;
        prev = b.up;
    }
    incomeTax = Math.max(0, incomeTax - 218); // נקודת זיכוי

    const total = bl + health + incomeTax;
    const net = g - total;
    return `💼 שכר נטו:\nברוטו: ₪${g.toLocaleString()}\n\nניכויים:\n  מס הכנסה: ₪${Math.round(incomeTax).toLocaleString()}\n  ביטוח לאומי: ₪${Math.round(bl).toLocaleString()}\n  ביטוח בריאות: ₪${Math.round(health).toLocaleString()}\n  סה"כ ניכויים: ₪${Math.round(total).toLocaleString()}\n\n✅ נטו: ₪${Math.round(net).toLocaleString()}`;
}

function vatCalc(amount, direction) {
    const a = Number(amount);
    if (isNaN(a)) return 'סכום לא תקין';
    if (direction === 'remove') {
        const base = a / 1.17;
        return `${a} כולל מע"מ:\nלפני מע"מ: ₪${base.toFixed(2)}\nמע"מ (17%): ₪${(a - base).toFixed(2)}`;
    }
    return `${a} + מע"מ 17% = ₪${(a * 1.17).toFixed(2)}\nמע"מ: ₪${(a * 0.17).toFixed(2)}`;
}

module.exports = { getForex, getGoldPrice, getSilverPrice, getTASEStock, getHistoricalPrice, mortgageCalc, netSalaryCalc, vatCalc };
