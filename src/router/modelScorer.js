// Model Scorer — dynamic per-model performance tracking
// Persists to data/routing_stats.json
// Score formula: 0.6*quality + 0.3*successRate*10 + 0.1*(10 - latencyNorm)

const fs = require('fs');
const path = require('path');

const STATS_FILE = path.join(process.cwd(), 'data', 'routing_stats.json');
const EMA_ALPHA = 0.2; // Weight of new data vs history (0.2 = 80% old, 20% new)
const MAX_LATENCY_MS = 15000; // Used to normalize latency to 0-10 scale

// Cold-start priors: default scores before any real data
// Based on known model capabilities and typical free-tier performance
const COLD_START_PRIORS = {
    // Fast
    'meta-llama/llama-3.2-3b-instruct:free':           { quality: 6.0, successRate: 0.95, latencyAvg: 800  },
    'meta-llama/llama-3.1-8b-instruct:free':            { quality: 6.5, successRate: 0.95, latencyAvg: 1000 },
    'google/gemma-3-4b-it:free':                        { quality: 6.0, successRate: 0.94, latencyAvg: 900  },
    'google/gemma-3n-e4b-it:free':                      { quality: 5.5, successRate: 0.94, latencyAvg: 700  },
    'qwen/qwen3-8b:free':                               { quality: 6.5, successRate: 0.93, latencyAvg: 1000 },
    // Balanced
    'meta-llama/llama-3.3-70b-instruct:free':           { quality: 8.0, successRate: 0.93, latencyAvg: 3000 },
    'google/gemma-3-12b-it:free':                       { quality: 7.0, successRate: 0.93, latencyAvg: 1800 },
    'google/gemma-3-27b-it:free':                       { quality: 7.5, successRate: 0.92, latencyAvg: 2500 },
    'qwen/qwen3-14b:free':                              { quality: 7.5, successRate: 0.92, latencyAvg: 2000 },
    'qwen/qwen-2.5-72b-instruct:free':                  { quality: 8.0, successRate: 0.92, latencyAvg: 3000 },
    'mistralai/mistral-small-3.2-24b-instruct:free':    { quality: 7.5, successRate: 0.91, latencyAvg: 2500 },
    // Powerful
    'qwen/qwen3-235b-a22b:free':                        { quality: 9.0, successRate: 0.90, latencyAvg: 6000 },
    'qwen/qwen3-30b-a3b:free':                          { quality: 8.0, successRate: 0.91, latencyAvg: 3500 },
    'deepseek/deepseek-chat-v3-0324:free':              { quality: 9.0, successRate: 0.91, latencyAvg: 5000 },
    'nvidia/llama-3.1-nemotron-70b-instruct:free':      { quality: 8.5, successRate: 0.91, latencyAvg: 4000 },
    // Reasoning
    'deepseek/deepseek-r1:free':                        { quality: 9.5, successRate: 0.89, latencyAvg: 8000 },
    'deepseek/deepseek-r1-0528:free':                   { quality: 9.5, successRate: 0.90, latencyAvg: 7000 },
    // Coding
    'qwen/qwen-2.5-coder-32b-instruct:free':            { quality: 9.0, successRate: 0.92, latencyAvg: 4000 },
    // Vision
    'meta-llama/llama-3.2-11b-vision-instruct:free':    { quality: 7.0, successRate: 0.91, latencyAvg: 3000 },
    'qwen/qwen2.5-vl-7b-instruct:free':                 { quality: 7.0, successRate: 0.90, latencyAvg: 2500 },
};

class ModelScorer {
    constructor() {
        this.stats = {}; // { model: { taskType: { qualityAvg, successRate, latencyAvg, callCount } } }
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(STATS_FILE)) {
                this.stats = JSON.parse(fs.readFileSync(STATS_FILE, 'utf8'));
            }
        } catch (e) {
            console.warn('ModelScorer: starting fresh stats (' + e.message + ')');
            this.stats = {};
        }
    }

    save() {
        try {
            const dir = path.dirname(STATS_FILE);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(STATS_FILE, JSON.stringify(this.stats, null, 2));
        } catch (e) {
            console.error('ModelScorer save error:', e.message);
        }
    }

    // Get (or initialize) stats entry for model+taskType
    _getEntry(model, taskType) {
        if (!this.stats[model]) this.stats[model] = {};
        if (!this.stats[model][taskType]) {
            const prior = COLD_START_PRIORS[model] || { quality: 6.0, successRate: 0.90, latencyAvg: 3000 };
            this.stats[model][taskType] = {
                qualityAvg: prior.quality,
                successRate: prior.successRate,
                latencyAvg: prior.latencyAvg,
                callCount: 0, // 0 = cold start, real data increases this
            };
        }
        return this.stats[model][taskType];
    }

    // Compute weighted score for a model on a task type
    // Returns 0-10
    getScore(model, taskType) {
        const e = this._getEntry(model, taskType);
        const latencyNorm = Math.min(e.latencyAvg / MAX_LATENCY_MS, 1) * 10; // 0-10 (higher = slower = worse)
        return (
            0.6 * e.qualityAvg +
            0.3 * e.successRate * 10 +
            0.1 * (10 - latencyNorm)
        );
    }

    // Update model stats with new observation (exponential moving average)
    // quality: 0-10, success: boolean, latency: milliseconds
    updateScore(model, taskType, { quality, success, latency }) {
        const e = this._getEntry(model, taskType);
        const α = EMA_ALPHA;

        e.qualityAvg  = α * quality + (1 - α) * e.qualityAvg;
        e.successRate = α * (success ? 1 : 0) + (1 - α) * e.successRate;
        e.latencyAvg  = α * latency + (1 - α) * e.latencyAvg;
        e.callCount  += 1;
        e.lastUpdated = new Date().toISOString();

        this.save();
    }

    // Apply time decay — reduce effective call count for old data
    // Should be called once per day
    decay(factor = 0.95) {
        for (const model of Object.keys(this.stats)) {
            for (const taskType of Object.keys(this.stats[model])) {
                const e = this.stats[model][taskType];
                if (e.callCount > 0) {
                    e.callCount = Math.floor(e.callCount * factor);
                }
            }
        }
        this.save();
    }

    // Get all scores for a task type (for router)
    getScoresForTask(taskType, models) {
        return models.map(m => ({ model: m, score: this.getScore(m, taskType) }))
                     .sort((a, b) => b.score - a.score);
    }

    // Get call count (0 = cold start)
    getCallCount(model, taskType) {
        return this.stats[model]?.[taskType]?.callCount || 0;
    }
}

module.exports = new ModelScorer(); // Singleton
