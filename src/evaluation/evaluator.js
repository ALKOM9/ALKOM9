// Evaluator — async response quality scorer using a judge model
// Does NOT block user response (fire-and-forget pattern)
// Judge model: meta-llama/llama-3.3-70b-instruct (fast, reliable, free)

const JUDGE_MODEL = 'meta-llama/llama-3.3-70b-instruct';
const JUDGE_TIMEOUT = 15000;

const RUBRIC_PROMPT = `You are an AI response quality judge. Score the assistant response below on a scale of 0-10 for each criterion.

Criteria:
- accuracy: Is the information correct and factually sound?
- relevance: Does it directly address what was asked?
- completeness: Does it cover the question fully?
- helpfulness: Is it practically useful?

Return ONLY valid JSON, no explanation:
{"accuracy":N,"relevance":N,"completeness":N,"helpfulness":N}`;

class Evaluator {
    constructor() {
        this.openrouter = null; // Injected after init to avoid circular deps
    }

    // Inject provider after construction
    setProvider(openrouterProvider) {
        this.openrouter = openrouterProvider;
    }

    // Score a response asynchronously (returns Promise — caller should not await if non-blocking)
    async scoreAsync(response, originalMessages, task, routing, latencyMs) {
        if (!this.openrouter) return null;
        if (!response || response.length < 10) {
            return { score: 1, breakdown: { accuracy: 1, relevance: 1, completeness: 1, helpfulness: 1 }, failed: true };
        }

        // Build last user message for context
        const lastUser = [...originalMessages].reverse().find(m => m.role === 'user');
        const userText = typeof lastUser?.content === 'string'
            ? lastUser.content.slice(0, 300)
            : '[multimodal]';

        const judgeMessages = [
            { role: 'system', content: RUBRIC_PROMPT },
            { role: 'user', content: `Question: ${userText}\n\nAssistant response:\n${response.slice(0, 800)}` }
        ];

        try {
            const result = await Promise.race([
                this.openrouter.call(judgeMessages, [], { model: JUDGE_MODEL, maxTokens: 100 }),
                new Promise((_, rej) => setTimeout(() => rej(new Error('judge timeout')), JUDGE_TIMEOUT)),
            ]);

            const text = result.choices[0]?.message?.content?.trim() || '';
            const jsonMatch = text.match(/\{[^}]+\}/);
            if (!jsonMatch) return null;

            const breakdown = JSON.parse(jsonMatch[0]);
            const { accuracy = 5, relevance = 5, completeness = 5, helpfulness = 5 } = breakdown;
            const score = parseFloat(((accuracy + relevance + completeness + helpfulness) / 4).toFixed(2));

            return { score, breakdown, latencyMs, model: routing.model, taskType: task.taskType };
        } catch (e) {
            // Evaluation failure is non-critical — log and move on
            console.warn('Evaluator: scoring failed silently —', e.message);
            return null;
        }
    }

    // Detect obviously failed responses without calling judge model (fast path)
    isFailed(response) {
        if (!response || response.trim().length < 5) return true;
        const lower = response.toLowerCase();
        const refusals = ["i can't", "i cannot", "i'm unable", "as an ai", "i don't have access"];
        if (refusals.some(r => lower.includes(r)) && response.length < 150) return true;
        return false;
    }
}

module.exports = new Evaluator(); // Singleton
