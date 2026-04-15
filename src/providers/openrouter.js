// OpenRouter provider — unified interface matching ClaudeProvider
// Returns OpenAI-compatible responses (OpenRouter already speaks OpenAI format)

const ALLOWED_MODELS = new Set([
    'nous/hermes-3-405b',
    'meta-llama/llama-3.2-3b-instruct',
    'meta-llama/llama-3.3-70b-instruct',
    'google/gemma-3-27b',
    'google/gemma-3-12b',
    'google/gemma-3-4b',
    'google/gemma-3n-2b',
    'venice/uncensored',
    'qwen/qwen3-coder-480b',
    'z-ai/glm-4.5-air',
    'openai/gpt-oss-20b',
    'openai/gpt-oss-120b',
    'nvidia/nemotron-nano-9b-v2',
    'qwen/qwen3-next-80b',
    'nvidia/nemotron-nano-12b-vl',
    'nvidia/nemotron-3-nano-30b',
    'lfm/lfm2.5-1.2b-instruct',
    'lfm/lfm2.5-1.2b-thinking',
    'minimax/m2.5',
    'nvidia/nemotron-embed-vl-1b',
    'nvidia/nemotron-3-super',
    'google/gemma-4-31b',
    'google/gemma-4-26b',
    'elephant',
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
