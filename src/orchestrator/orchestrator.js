// Orchestrator — multi-model execution patterns
// Patterns: Single | Planner→Executor→Critic | Draft→Review→Improve | Parallel+Vote

const OpenRouterProvider = require('../providers/openrouter');
const router = require('../router/router');

// Pattern selection thresholds — Single is almost always used
const SINGLE_CONF_THRESHOLD = 0.0;   // always try single first
const PARALLEL_CONF_THRESHOLD = 0.0; // parallel disabled (causes crashes on free tier)

class Orchestrator {
    constructor() {
        this.openrouter = null; // Injected after init
    }

    setProvider(openrouterProvider) {
        this.openrouter = openrouterProvider;
    }

    // Main entry point
    // routing: output from router.select()
    // Returns: { response, modelsUsed, pattern, latencyMs }
    async execute(routing, messages, tools, maxTokens) {
        const { taskType, complexity, confidence } = routing;
        const start = Date.now();

        let result;

        // Choose execution pattern
        if (!this.openrouter) {
            throw new Error('Orchestrator: provider not set');
        }

        // Always try Single first — fast and reliable on free-tier models
        // Only use multi-step patterns for high-complexity tasks
        try {
            if (complexity === 'high' && taskType === 'reasoning' && confidence > 0.3) {
                result = await this._plannerExecutorCritic(routing, messages, tools, maxTokens);
            } else if (taskType === 'creative' && complexity === 'high' && confidence > 0.3) {
                result = await this._draftReviewImprove(routing, messages, tools, maxTokens);
            } else {
                result = await this._single(routing, messages, tools, maxTokens);
            }
        } catch (err) {
            // Only retry without tools if the error is specifically about tool support.
            // For all other errors (model not found, rate limit, etc.), rethrow so
            // agent.js can try the next model in the list without wasting another API call.
            const isToolSupportError = err.message?.includes('tool use') || err.message?.includes('tool_use');
            if (!isToolSupportError) throw err;
            console.warn(`  Orchestrator: ${routing.model.split('/')[1]} no tool support, retrying without tools...`);
            result = await this._single(routing, messages, [], maxTokens);
        }

        return { ...result, latencyMs: Date.now() - start };
    }

    // Pattern 1: Single model (fast, most common)
    async _single(routing, messages, tools, maxTokens) {
        const resp = await this.openrouter.call(messages, tools, {
            model: routing.model, maxTokens
        });
        const response = resp.choices[0]?.message?.content || '';
        console.log(`  🎯 Single [${routing.model.split('/')[1]}]: ${response.length} chars`);
        return { response, modelsUsed: [routing.model], pattern: 'single', rawResp: resp };
    }

    // Pattern 2: Planner → Executor → Critic (for high-complexity reasoning)
    async _plannerExecutorCritic(routing, messages, tools, maxTokens) {
        const [plannerModel, executorModel, criticModel] = this._pickThree(routing, 'reasoning');

        // Step 1: Planner — create a step-by-step plan
        const plannerMessages = [
            ...messages,
            { role: 'system', content: 'First, create a clear step-by-step plan to answer this. Output ONLY the plan, numbered steps.' }
        ];
        const planResp = await this.openrouter.call(plannerMessages, [], { model: plannerModel, maxTokens: 512 });
        const plan = planResp.choices[0]?.message?.content || '';

        // Step 2: Executor — execute the plan
        const execMessages = [
            ...messages,
            { role: 'assistant', content: `My plan:\n${plan}` },
            { role: 'user', content: 'Now execute this plan and provide the full answer.' }
        ];
        const execResp = await this.openrouter.call(execMessages, tools, { model: executorModel, maxTokens });
        const execution = execResp.choices[0]?.message?.content || '';

        // Step 3: Critic — review and improve
        const criticMessages = [
            { role: 'user', content: messages.slice(-1)[0]?.content || '' },
            { role: 'assistant', content: execution },
            { role: 'user', content: 'Review your answer. If there are any errors or gaps, provide a corrected final version. If it\'s correct, just confirm and output the answer.' }
        ];
        const criticResp = await this.openrouter.call(criticMessages, [], { model: criticModel, maxTokens });
        const response = criticResp.choices[0]?.message?.content || execution;

        console.log(`  🔗 P→E→C [${plannerModel.split('/')[1]}→${executorModel.split('/')[1]}→${criticModel.split('/')[1]}]`);
        return { response, modelsUsed: [plannerModel, executorModel, criticModel], pattern: 'planner-executor-critic', rawResp: criticResp };
    }

    // Pattern 3: Draft → Review → Improve (for creative tasks)
    async _draftReviewImprove(routing, messages, tools, maxTokens) {
        const [draftModel, reviewModel] = this._pickTwo(routing, 'creative');

        // Step 1: Draft
        const draftResp = await this.openrouter.call(messages, tools, { model: draftModel, maxTokens });
        const draft = draftResp.choices[0]?.message?.content || '';

        // Step 2: Review + Improve
        const reviewMessages = [
            { role: 'user', content: messages.slice(-1)[0]?.content || '' },
            { role: 'assistant', content: draft },
            { role: 'user', content: 'Improve this response — make it more engaging, creative, and natural. Output only the improved version.' }
        ];
        const finalResp = await this.openrouter.call(reviewMessages, [], { model: reviewModel, maxTokens });
        const response = finalResp.choices[0]?.message?.content || draft;

        console.log(`  ✍️  Draft→Improve [${draftModel.split('/')[1]}→${reviewModel.split('/')[1]}]`);
        return { response, modelsUsed: [draftModel, reviewModel], pattern: 'draft-review-improve', rawResp: finalResp };
    }

    // Pattern 4: Parallel + Vote (when confidence is low)
    async _parallel(routing, messages, tools, maxTokens) {
        const candidates = [routing.model, ...(routing.alternatives || [])].slice(0, 2);

        const calls = candidates.map(model =>
            this.openrouter.call(messages, tools, { model, maxTokens: Math.min(maxTokens, 800) })
                .then(r => ({ model, text: r.choices[0]?.message?.content || '', ok: true }))
                .catch(e => ({ model, text: '', ok: false, error: e.message }))
        );

        const results = await Promise.all(calls);
        const valid = results.filter(r => r.ok && r.text.length > 20);

        if (valid.length === 0) throw new Error('All parallel models failed');

        // Pick longest valid response (simple heuristic for completeness)
        const best = valid.sort((a, b) => b.text.length - a.text.length)[0];
        const response = best.text;

        console.log(`  ⚡ Parallel [${candidates.map(m => m.split('/')[1]).join('+')}] → winner: ${best.model.split('/')[1]}`);
        return { response, modelsUsed: candidates, pattern: 'parallel-vote', rawResp: null };
    }

    // Pick 3 models for Planner→Executor→Critic
    _pickThree(routing, taskType) {
        const all = [routing.model, ...(routing.alternatives || [])];
        while (all.length < 3) {
            const fallbacks = [
                'meta-llama/llama-3.3-70b-instruct:free',
                'qwen/qwen-2.5-72b-instruct:free',
                'google/gemma-3-27b-it:free',
            ];
            for (const f of fallbacks) {
                if (!all.includes(f)) { all.push(f); break; }
            }
        }
        return all.slice(0, 3);
    }

    // Pick 2 models for Draft→Review
    _pickTwo(routing, taskType) {
        const all = [routing.model, ...(routing.alternatives || [])];
        if (all.length < 2) all.push('meta-llama/llama-3.3-70b-instruct:free');
        return all.slice(0, 2);
    }
}

module.exports = new Orchestrator(); // Singleton
