// Evaluator — async response quality scorer using a judge model
// Does NOT block user response (fire-and-forget pattern)
// Judge: Groq llama-3.1-8b (fast, separate quota from OpenRouter — saves OR req/day)

const JUDGE_TIMEOUT = 10000;

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
        this.groq = null;       // Preferred judge (separate quota from OR)
        this.openrouter = null; // Fallback judge
    }

    // Inject providers after construction
    setProvider(openrouterProvider) {
        this.openrouter = openrouterProvider;
    }

    setGroq(groqProvider) {
        this.groq = groqProvider;
    }

    // Score a response asynchronously (returns Promise — caller should not await if non-blocking)
    async scoreAsync(response, originalMessages, task, routing, latencyMs) {
        if (!this.groq && !this.openrouter) return null;
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

        // Try Groq first (doesn't consume OR quota), fall back to OR if Groq unavailable
        const callJudge = async () => {
            if (this.groq) {
                try {
                    const Groq = require('groq-sdk');
                    const completion = await this.groq.chat.completions.create({
                        model: 'llama-3.1-8b-instant',
                        messages: judgeMessages,
                        max_tokens: 100,
                        temperature: 0.1,
                    });
                    return completion.choices[0]?.message?.content?.trim() || '';
                } catch (_) {
                    // Groq failed — try OR fallback
                }
            }
            if (this.openrouter) {
                const result = await this.openrouter.call(judgeMessages, [], {
                    model: 'meta-llama/llama-3.3-70b-instruct:free',
                    maxTokens: 100,
                });
                return result.choices[0]?.message?.content?.trim() || '';
            }
            throw new Error('No judge provider available');
        };

        try {
            const text = await Promise.race([
                callJudge(),
                new Promise((_, rej) => setTimeout(() => rej(new Error('judge timeout')), JUDGE_TIMEOUT)),
            ]);

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
