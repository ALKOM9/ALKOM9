// Router — probabilistic model selection with epsilon-greedy exploration
// Input:  { taskType, complexity, requiresTools, isImage }
// Output: { model, confidence, reason, alternatives }

const OpenRouterProvider = require('../providers/openrouter');
const modelScorer = require('./modelScorer');

const EPSILON = 0.1; // 10% exploration rate
const DIVERSITY_THRESHOLD = 0.70; // Force rotation if one model used >70% of recent calls

// Task-type → candidate models mapping
const CANDIDATES = {
    simple: [
        'meta-llama/llama-3.3-70b-instruct:free',
        'google/gemma-3-27b-it:free',
        'google/gemma-3-12b-it:free',
        'qwen/qwen3-14b:free',
        'mistralai/mistral-small-3.2-24b-instruct:free',
        'meta-llama/llama-3.1-8b-instruct:free',
        'meta-llama/llama-3.2-3b-instruct:free',
    ],
    reasoning: [
        'deepseek/deepseek-r1-0528:free',
        'deepseek/deepseek-r1:free',
        'qwen/qwen3-235b-a22b:free',
        'qwen/qwen3-30b-a3b:free',
        'nvidia/llama-3.1-nemotron-70b-instruct:free',
        'meta-llama/llama-3.3-70b-instruct:free',
    ],
    coding: [
        'qwen/qwen-2.5-coder-32b-instruct:free',
        'qwen/qwen3-235b-a22b:free',
        'deepseek/deepseek-chat-v3-0324:free',
        'meta-llama/llama-3.3-70b-instruct:free',
        'qwen/qwen3-30b-a3b:free',
    ],
    creative: [
        'qwen/qwen3-235b-a22b:free',
        'deepseek/deepseek-chat-v3-0324:free',
        'mistralai/mistral-small-3.2-24b-instruct:free',
        'meta-llama/llama-3.3-70b-instruct:free',
        'google/gemma-3-27b-it:free',
    ],
    analysis: [
        'deepseek/deepseek-chat-v3-0324:free',
        'qwen/qwen3-235b-a22b:free',
        'nvidia/llama-3.1-nemotron-70b-instruct:free',
        'meta-llama/llama-3.3-70b-instruct:free',
        'mistralai/mistral-small-3.2-24b-instruct:free',
    ],
    vision: [
        'meta-llama/llama-3.2-11b-vision-instruct:free',
        'qwen/qwen2.5-vl-7b-instruct:free',
    ],
};

// Complexity modifiers
const HIGH_COMPLEXITY_BOOST = new Set([
    'deepseek/deepseek-r1-0528:free', 'deepseek/deepseek-r1:free',
    'qwen/qwen3-235b-a22b:free', 'deepseek/deepseek-chat-v3-0324:free',
    'nvidia/llama-3.1-nemotron-70b-instruct:free', 'qwen/qwen-2.5-coder-32b-instruct:free',
]);
const LOW_COMPLEXITY_PREFER = new Set([
    'meta-llama/llama-3.2-3b-instruct:free', 'meta-llama/llama-3.1-8b-instruct:free',
    'google/gemma-3-4b-it:free', 'google/gemma-3n-e4b-it:free', 'qwen/qwen3-8b:free',
]);

// Recent selection tracking for anti-overfitting (last 20 calls)
const recentSelections = [];
const RECENT_WINDOW = 20;

// Softmax over scores → probability distribution
function softmax(scores, temperature = 2.0) {
    const maxScore = Math.max(...scores);
    const exps = scores.map(s => Math.exp((s - maxScore) / temperature));
    const sum = exps.reduce((a, b) => a + b, 0);
    return exps.map(e => e / sum);
}

// Weighted random sample
function weightedSample(items, weights) {
    const r = Math.random();
    let cumulative = 0;
    for (let i = 0; i < items.length; i++) {
        cumulative += weights[i];
        if (r <= cumulative) return items[i];
    }
    return items[items.length - 1];
}

// Check if a model is being overused recently
function isOverused(model) {
    if (recentSelections.length < 5) return false;
    const count = recentSelections.filter(m => m === model).length;
    return count / recentSelections.length > DIVERSITY_THRESHOLD;
}

function recordSelection(model) {
    recentSelections.push(model);
    if (recentSelections.length > RECENT_WINDOW) recentSelections.shift();
}

function select(task) {
    const { taskType = 'simple', complexity = 'medium', isImage = false } = task;

    // Get candidates for this task type (filter to whitelist)
    let candidates = (CANDIDATES[taskType] || CANDIDATES.simple)
        .filter(m => OpenRouterProvider.isAllowed(m));

    if (candidates.length === 0) candidates = CANDIDATES.simple;

    // Apply complexity filter for low complexity (prefer fast/small models)
    if (complexity === 'low' && candidates.length > 2) {
        const fast = candidates.filter(m => LOW_COMPLEXITY_PREFER.has(m));
        const general = candidates.filter(m => !HIGH_COMPLEXITY_BOOST.has(m));
        candidates = (general.length >= 2 ? general : candidates).slice(0, 5);
    }
    // For high complexity, boost large models
    if (complexity === 'high') {
        candidates.sort((a, b) => {
            const aBoost = HIGH_COMPLEXITY_BOOST.has(a) ? 2 : 0;
            const bBoost = HIGH_COMPLEXITY_BOOST.has(b) ? 2 : 0;
            return bBoost - aBoost;
        });
    }

    // Get scores from ModelScorer
    const scored = modelScorer.getScoresForTask(taskType, candidates);
    const scores = scored.map(s => s.score);
    const models = scored.map(s => s.model);

    // Filter out overused models (anti-overfitting)
    const available = models.filter(m => !isOverused(m));
    const filteredModels = available.length >= 2 ? available : models;
    const filteredScores = filteredModels.map(m => scores[models.indexOf(m)]);

    // Epsilon-greedy: 10% random exploration, 90% probabilistic exploitation
    let selectedModel;
    let reason;

    if (Math.random() < EPSILON) {
        // Exploration: pick a random candidate (weighted toward lower-used models)
        const coldModels = filteredModels.filter(m => modelScorer.getCallCount(m, taskType) < 5);
        selectedModel = coldModels.length > 0
            ? coldModels[Math.floor(Math.random() * coldModels.length)]
            : filteredModels[Math.floor(Math.random() * filteredModels.length)];
        reason = `exploration (ε-greedy, cold=${coldModels.length > 0})`;
    } else {
        // Exploitation: softmax sampling from top models
        const probs = softmax(filteredScores);
        selectedModel = weightedSample(filteredModels, probs);
        reason = `exploitation (score=${modelScorer.getScore(selectedModel, taskType).toFixed(2)})`;
    }

    // Confidence: normalized gap between top-1 and top-2 scores
    const topScore = filteredScores[0] || 5;
    const secondScore = filteredScores[1] || topScore - 1;
    const confidence = Math.min(1, Math.max(0, (topScore - secondScore) / 3));

    // Record for anti-overfitting tracking
    recordSelection(selectedModel);

    return {
        model: selectedModel,
        confidence: parseFloat(confidence.toFixed(2)),
        reason,
        alternatives: filteredModels.filter(m => m !== selectedModel).slice(0, 2),
        taskType,
        complexity,
    };
}

module.exports = { select, CANDIDATES };
