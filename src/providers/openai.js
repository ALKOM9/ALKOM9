// OpenAI Provider — GPT-4.1 primary model
// Supports tool calling, vision, streaming (disabled for simplicity)

const BASE_URL = 'https://api.openai.com/v1/chat/completions';
const TIMEOUT_MS = 30000;

// Model priority: gpt-4.1 → gpt-4.1-mini → gpt-4o
const MODEL_CHAIN = ['gpt-4.1', 'gpt-4.1-mini', 'gpt-4o'];

class OpenAIProvider {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
        };
        this._modelIdx = 0; // start with best model
    }

    get activeModel() {
        return MODEL_CHAIN[this._modelIdx] || MODEL_CHAIN[MODEL_CHAIN.length - 1];
    }

    async call(messages, tools = [], opts = {}) {
        const model = opts.model || this.activeModel;
        const maxTokens = opts.maxTokens || 1024;

        const body = {
            model,
            messages,
            max_tokens: maxTokens,
            temperature: opts.temperature ?? 0.7,
        };

        if (tools && tools.length > 0) {
            body.tools = tools;
            body.tool_choice = 'auto';
        }

        const res = await fetch(BASE_URL, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(body),
            signal: AbortSignal.timeout(TIMEOUT_MS),
        });

        if (!res.ok) {
            const errText = await res.text().catch(() => '');
            const err = new Error(`OpenAI error ${res.status}: ${errText.slice(0, 200)}`);
            err.status = res.status;

            // Model not available → try next in chain
            const isModelError = (res.status === 404 || res.status === 400)
                && (errText.includes('model') || errText.includes('does not exist') || errText.includes('invalid'));
            if (isModelError && !opts.model) {
                // only auto-degrade when using activeModel (not a forced opts.model)
                if (this._modelIdx < MODEL_CHAIN.length - 1) {
                    this._modelIdx++;
                    console.warn(`  OpenAI: ${model} not available (${res.status}), trying ${this.activeModel}`);
                    return this.call(messages, tools, opts);
                }
            }

            throw err;
        }

        const data = await res.json();
        if (!data.choices?.length) {
            throw Object.assign(new Error('Empty response from OpenAI'), { code: 'EMPTY_RESPONSE' });
        }

        return data; // OpenAI format == OpenAI format, compatible with agent.js parsing
    }
}

module.exports = OpenAIProvider;
