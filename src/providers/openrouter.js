// OpenRouter provider — unified interface matching ClaudeProvider
// Returns OpenAI-compatible responses (OpenRouter already speaks OpenAI format)

const ALLOWED_MODELS = new Set([
    // OpenRouter built-in free router — auto-picks best available free model,
    // intelligently filters for tool calling support. Use this as primary.
    'openrouter/free',
    // Fast / Small
    'meta-llama/llama-3.2-3b-instruct:free',
    'meta-llama/llama-3.1-8b-instruct:free',
    'google/gemma-3-4b-it:free',
    'google/gemma-3n-e4b-it:free',
    'qwen/qwen3-8b:free',
    // Balanced
    'meta-llama/llama-3.3-70b-instruct:free',
    // Powerful
    'qwen/qwen3-235b-a22b:free',
    'qwen/qwen3-30b-a3b:free',
    'deepseek/deepseek-chat-v3-0324:free',
    'nvidia/llama-3.1-nemotron-70b-instruct:free',
    // Reasoning
    'deepseek/deepseek-r1:free',
    'deepseek/deepseek-r1-0528:free',
    // Coding
    'qwen/qwen-2.5-coder-32b-instruct:free',
    // Vision
    'meta-llama/llama-3.2-11b-vision-instruct:free',
    'qwen/qwen2.5-vl-7b-instruct:free',
]);

const BASE_URL = 'https://openrouter.ai/api/v1/chat/completions';
const TIMEOUT_MS = 30000;

class OpenRouterProvider {
    constructor(apiKey, siteUrl = '', siteName = 'Aylin') {
        if (!apiKey) throw new Error('OPENROUTER_API_KEY required');
        this.apiKey = apiKey;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            'HTTP-Referer': siteUrl,
            'X-Title': siteName,
        };
    }

    // Enforce whitelist — throws if model is not allowed
    _assertModel(model) {
        if (!ALLOWED_MODELS.has(model)) {
            throw Object.assign(
                new Error(`Model "${model}" is not in the allowed list`),
                { code: 'MODEL_NOT_ALLOWED' }
            );
        }
    }

    // Main call — same interface as ClaudeProvider
    // Returns OpenAI-compatible: { choices: [{ finish_reason, message: { content, tool_calls } }] }
    async call(messages, tools = [], { model, maxTokens = 1024 } = {}) {
        const activeModel = model || 'meta-llama/llama-3.3-70b-instruct';
        this._assertModel(activeModel);

        const body = {
            model: activeModel,
            messages,
            max_tokens: maxTokens,
            temperature: 0.7,
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
            const err = new Error(`OpenRouter error ${res.status}: ${errText.slice(0, 200)}`);
            err.status = res.status;
            err.code = res.status === 429 ? 'RATE_LIMITED' : 'SERVER_ERROR';
            throw err;
        }

        const data = await res.json();

        // OpenRouter already returns OpenAI format — pass through directly
        if (!data.choices?.length) {
            throw Object.assign(new Error('Empty response from OpenRouter'), { code: 'EMPTY_RESPONSE' });
        }

        return data;
    }

    // List allowed models (for debugging / router)
    static getAllowedModels() {
        return [...ALLOWED_MODELS];
    }

    static isAllowed(model) {
        return ALLOWED_MODELS.has(model);
    }
}

module.exports = OpenRouterProvider;
