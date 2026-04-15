// Learner — updates model scores after evaluation, logs all routing decisions
// Anti-overfitting: adds noise when scores get too high
// Failure learning: 2x penalty for failed responses

const fs = require('fs');
const path = require('path');
const modelScorer = require('../router/modelScorer');

const LOGS_FILE = path.join(process.cwd(), 'data', 'routing_logs.json');
const MAX_LOG_ENTRIES = 1000;
const OVERFITTING_THRESHOLD = 9.5; // If score > this → add noise
const FAILURE_PENALTY_MULT = 2.0; // Failed responses penalized harder

class Learner {
    constructor() {
        this.logs = [];
        this._load();
    }

    _load() {
        try {
            if (fs.existsSync(LOGS_FILE)) {
                this.logs = JSON.parse(fs.readFileSync(LOGS_FILE, 'utf8'));
            }
        } catch (_) {
            this.logs = [];
        }
    }

    _save() {
        try {
            const dir = path.dirname(LOGS_FILE);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            // Keep only last MAX_LOG_ENTRIES
            if (this.logs.length > MAX_LOG_ENTRIES) {
                this.logs = this.logs.slice(-MAX_LOG_ENTRIES);
            }
            fs.writeFileSync(LOGS_FILE, JSON.stringify(this.logs, null, 2));
        } catch (e) {
            console.error('Learner save error:', e.message);
        }
    }

    // Called after evaluator returns a score
    // evalResult: { score, breakdown, latencyMs, model, taskType } | null
    update(model, taskType, evalResult, latencyMs) {
        if (!evalResult) return; // Evaluation failed — skip update

        const { score, failed } = evalResult;
        const success = !failed && score >= 4;

        // Apply 2x penalty weight for failures
        const effectiveQuality = failed ? Math.min(score, 2) : score;
        const effectiveSuccess = success;

        // Anti-overfitting: if score is near perfect → add small noise
        const currentScore = modelScorer.getScore(model, taskType);
        const qualityToStore = currentScore > OVERFITTING_THRESHOLD
            ? effectiveQuality + (Math.random() - 0.5) * 1.0
            : effectiveQuality;

        modelScorer.updateScore(model, taskType, {
            quality: Math.max(0, Math.min(10, qualityToStore)),
            success: effectiveSuccess,
            latency: latencyMs || evalResult.latencyMs || 3000,
        });

        // Log the decision
        const entry = {
            ts: new Date().toISOString(),
            model,
            taskType,
            score: parseFloat(score.toFixed(2)),
            success,
            latencyMs,
            ...(evalResult.breakdown || {}),
        };
        this.logs.push(entry);
        this._save();

        if (!success) {
            console.log(`  📉 Learner: penalized ${model.split('/')[1]} on ${taskType} (score=${score.toFixed(1)})`);
        }
    }

    // Get recent performance summary (for debugging/dashboard)
    getSummary(limit = 20) {
        const recent = this.logs.slice(-limit);
        const byModel = {};
        for (const entry of recent) {
            if (!byModel[entry.model]) byModel[entry.model] = { scores: [], count: 0 };
            byModel[entry.model].scores.push(entry.score);
            byModel[entry.model].count++;
        }
        return Object.entries(byModel).map(([model, data]) => ({
            model,
            avgScore: (data.scores.reduce((a, b) => a + b, 0) / data.scores.length).toFixed(2),
            count: data.count,
        })).sort((a, b) => b.avgScore - a.avgScore);
    }
}

module.exports = new Learner(); // Singleton
