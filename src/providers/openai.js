// OpenAI Provider — GPT-5 primary model
// Supports tool calling, vision, streaming (disabled for simplicity)

const BASE_URL = 'https://api.openai.com/v1/chat/completions';
const TIMEOUT_MS = 30000;

const PRIMARY_MODEL   = 'gpt-5';
const FALLBACK_MODEL  = 'gpt-4o'; // if gpt-5 not yet on account

class OpenAIProvider {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
        };
        this._gpt5Available = true; // optimistically assume gpt-5 exists
    }

    get activeModel() {
        return this._gpt5Available ? PRIMARY_MODEL : FALLBACK_MODEL;
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

            // gpt-5 not yet available on this account → fall back to gpt-4o silently
            // OpenAI returns 404 or 400 for unknown/inaccessible models
            const modelNotFound = (res.status === 404 || res.status === 400) && model === PRIMARY_MODEL
                && (errText.includes('model') || errText.includes('does not exist') || errText.includes('invalid'));
            if (modelNotFound) {
                this._gpt5Available = false;
                console.warn(`  OpenAI: ${PRIMARY_MODEL} not available (${res.status}), falling back to ${FALLBACK_MODEL}`);
                return this.call(messages, tools, { ...opts, model: FALLBACK_MODEL });
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
