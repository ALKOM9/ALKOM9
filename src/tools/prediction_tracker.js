// prediction_tracker.js — learning system for stock analysis
// Saves predictions, checks outcomes, improves confidence calibration over time

const fs = require('fs');
const path = require('path');

const FILE = path.join(__dirname, '../../data/predictions.json');

function load() {
    try {
        if (!fs.existsSync(FILE)) return { predictions: [], accuracy: {} };
        return JSON.parse(fs.readFileSync(FILE, 'utf8'));
    } catch { return { predictions: [], accuracy: {} }; }
}

function save(data) {
    try {
        fs.mkdirSync(path.dirname(FILE), { recursive: true });
        fs.writeFileSync(FILE, JSON.stringify(data, null, 2));
    } catch (e) { console.warn('PredictionTracker save failed:', e.message); }
}

// Save a prediction after analysis
function savePrediction(sym, signal, confidence, price, horizon = '1m', reasoning = '') {
    const data = load();
    data.predictions.push({
        id: Date.now(),
        sym: sym.toUpperCase(),
        signal,        // 'bullish' | 'bearish' | 'neutral'
        confidence,    // 'high' | 'medium' | 'low'
        price,
        horizon,       // '1w' | '1m' | '3m'
        reasoning,
        ts: new Date().toISOString(),
        resolved: false,
        outcome: null,
    });
    // Keep last 200 predictions
    if (data.predictions.length > 200) data.predictions = data.predictions.slice(-200);
    save(data);
    return `📌 תחזית נשמרה: ${sym.toUpperCase()} ${signal} @ $${price.toFixed(2)} | אופק: ${horizon} | ביטחון: ${confidence}`;
}

// Check outcomes of past predictions and update accuracy stats
async function checkOutcomes(fetchCurrentPrice) {
    const data = load();
    const now = Date.now();
    let checked = 0, correct = 0;

    for (const p of data.predictions) {
        if (p.resolved) continue;
        const horizonDays = p.horizon === '1w' ? 7 : p.horizon === '3m' ? 90 : 30;
        const predDate = new Date(p.ts).getTime();
        if (now - predDate < horizonDays * 24 * 60 * 60 * 1000) continue; // too early

        try {
            const currPrice = await fetchCurrentPrice(p.sym);
            if (!currPrice) continue;
            const pctChange = (currPrice - p.price) / p.price * 100;
            const actualSignal = pctChange > 2 ? 'bullish' : pctChange < -2 ? 'bearish' : 'neutral';
            const wasCorrect = actualSignal === p.signal;

            p.resolved = true;
            p.outcome = { currPrice, pctChange: pctChange.toFixed(2), actualSignal, correct: wasCorrect };
            checked++;
            if (wasCorrect) correct++;

            // Update accuracy per signal type + confidence
            const key = `${p.signal}_${p.confidence}`;
            if (!data.accuracy[key]) data.accuracy[key] = { total: 0, correct: 0 };
            data.accuracy[key].total++;
            if (wasCorrect) data.accuracy[key].correct++;
        } catch { /* skip */ }
    }

    save(data);
    if (checked === 0) return 'אין תחזיות שהגיע זמנן לבדיקה';
    const rate = (correct / checked * 100).toFixed(0);
    return `בדקתי ${checked} תחזיות: ${correct} נכונות (${rate}% דיוק)`;
}

// Get accuracy summary
function getAccuracySummary() {
    const data = load();
    const preds = data.predictions;
    const resolved = preds.filter(p => p.resolved);
    if (resolved.length === 0) return 'אין עדיין תחזיות שנסגרו';

    const correct = resolved.filter(p => p.outcome?.correct).length;
    const rate = (correct / resolved.length * 100).toFixed(0);

    let out = `📊 דיוק תחזיות\nסה"כ נסגרו: ${resolved.length} | נכונות: ${correct} (${rate}%)\n\n`;

    // By signal type
    const bySignal = {};
    resolved.forEach(p => {
        if (!bySignal[p.signal]) bySignal[p.signal] = { total: 0, correct: 0 };
        bySignal[p.signal].total++;
        if (p.outcome?.correct) bySignal[p.signal].correct++;
    });
    Object.entries(bySignal).forEach(([sig, d]) => {
        out += `${sig}: ${d.correct}/${d.total} (${(d.correct/d.total*100).toFixed(0)}%)\n`;
    });

    // Best/worst predictions
    const withOutcome = resolved.filter(p => p.outcome?.pctChange != null);
    if (withOutcome.length > 0) {
        const best = withOutcome.reduce((a, b) => Math.abs(parseFloat(b.outcome.pctChange)) > Math.abs(parseFloat(a.outcome.pctChange)) ? b : a);
        out += `\nהתחזית הכי מדויקת: ${best.sym} ${best.signal} → ${best.outcome.pctChange}%`;
    }

    return out;
}

// Get calibration factor — how much to adjust confidence based on past accuracy
function getCalibration(signal, confidence) {
    const data = load();
    const key = `${signal}_${confidence}`;
    const acc = data.accuracy[key];
    if (!acc || acc.total < 5) return 1.0; // not enough data
    const rate = acc.correct / acc.total;
    // calibration: if accuracy is 70%+, full confidence. if 40-70%, reduce. if <40%, flag.
    if (rate >= 0.7) return 1.0;
    if (rate >= 0.5) return 0.85;
    if (rate >= 0.4) return 0.7;
    return 0.5;
}

// Get recent predictions for a symbol
function getSymbolHistory(sym) {
    const data = load();
    const symPreds = data.predictions.filter(p => p.sym === sym.toUpperCase()).slice(-10);
    if (symPreds.length === 0) return `אין תחזיות שמורות עבור ${sym.toUpperCase()}`;
    const lines = symPreds.map(p => {
        const date = new Date(p.ts).toLocaleDateString('he-IL');
        const outcome = p.resolved ? (p.outcome?.correct ? '✅' : '❌') + ` (${p.outcome?.pctChange}%)` : '⏳ ממתין';
        return `${date}: ${p.signal} @ $${p.price.toFixed(2)} [${p.confidence}] ${outcome}`;
    });
    return `היסטוריית תחזיות — ${sym.toUpperCase()}\n${lines.join('\n')}`;
}

module.exports = { savePrediction, checkOutcomes, getAccuracySummary, getCalibration, getSymbolHistory };
