const Anthropic = require('@anthropic-ai/sdk');

class ClaudeProvider {
    constructor(apiKey) {
        this.client = new Anthropic({ apiKey });
        this.primaryModel = 'claude-sonnet-4-6';
        this.fastModel = 'claude-haiku-4-5-20251001';
    }

    // Convert OpenAI-style TOOLS to Anthropic format
    toAnthropicTools(tools) {
        return tools.map(t => ({
            name: t.function.name,
            description: t.function.description,
            input_schema: t.function.parameters || { type: 'object', properties: {} }
        }));
    }

    // Extract system prompt and convert messages to Anthropic format
    convertMessages(msgs) {
        let system = '';
        const out = [];

        for (const msg of msgs) {
            if (msg.role === 'system') {
                system = typeof msg.content === 'string' ? msg.content : '';
                continue;
            }

            // Tool results: group into a user message
            if (msg.role === 'tool') {
                const prev = out[out.length - 1];
                const block = { type: 'tool_result', tool_use_id: msg.tool_call_id, content: String(msg.content) };
                if (prev && prev.role === 'user' && Array.isArray(prev.content)) {
                    prev.content.push(block);
                } else {
                    out.push({ role: 'user', content: [block] });
                }
                continue;
            }

            // Assistant message with tool calls
            if (msg.role === 'assistant' && msg.tool_calls?.length) {
                const content = [];
                if (msg.content) content.push({ type: 'text', text: msg.content });
                for (const tc of msg.tool_calls) {
                    let input = {};
                    try { input = JSON.parse(tc.function.arguments || '{}'); } catch (_) {}
                    content.push({ type: 'tool_use', id: tc.id, name: tc.function.name, input });
                }
                out.push({ role: 'assistant', content });
                continue;
            }

            // Multimodal user messages (images)
            if (msg.role === 'user' && Array.isArray(msg.content)) {
                const content = msg.content.map(p => {
                    if (p.type === 'image_url') {
                        const url = p.image_url?.url || '';
                        if (url.startsWith('data:')) {
                            const [hdr, data] = url.split(',');
                            const mediaType = hdr.split(':')[1]?.split(';')[0] || 'image/jpeg';
                            return { type: 'image', source: { type: 'base64', media_type: mediaType, data } };
                        }
                        return { type: 'image', source: { type: 'url', url } };
                    }
                    return p;
                });
                out.push({ role: 'user', content });
                continue;
            }

            if (msg.role === 'user' || msg.role === 'assistant') {
                out.push({ role: msg.role, content: msg.content || '' });
            }
        }

        return { system, messages: this._ensureAlternating(out) };
    }

    _ensureAlternating(msgs) {
        const result = [];
        for (const msg of msgs) {
            const last = result[result.length - 1];
            if (last && last.role === msg.role) {
                // Merge same-role messages
                const toArr = c => Array.isArray(c) ? c : [{ type: 'text', text: String(c) }];
                last.content = [...toArr(last.content), ...toArr(msg.content)];
            } else {
                result.push({ ...msg, content: msg.content ?? '' });
            }
        }
        // Claude requires starting with user
        if (result.length > 0 && result[0].role !== 'user') {
            result.unshift({ role: 'user', content: '...' });
        }
        return result;
    }

    // Standardize Anthropic response → OpenAI-compatible format
    _standardize(resp) {
        let text = '';
        const toolCalls = [];
        for (const block of resp.content || []) {
            if (block.type === 'text') text += block.text;
            if (block.type === 'tool_use') {
                toolCalls.push({
                    id: block.id,
                    type: 'function',
                    function: { name: block.name, arguments: JSON.stringify(block.input || {}) }
                });
            }
        }
        const finishReason = resp.stop_reason === 'tool_use' ? 'tool_calls'
            : resp.stop_reason === 'end_turn' ? 'stop' : resp.stop_reason || 'stop';

        return {
            choices: [{
                finish_reason: finishReason,
                message: {
                    role: 'assistant',
                    content: text || null,
                    tool_calls: toolCalls.length ? toolCalls : undefined
                }
            }]
        };
    }

    async call(messages, tools, { maxTokens = 1024, model, useTools = true } = {}) {
        const activeModel = model || this.primaryModel;
        const { system, messages: anthMessages } = this.convertMessages(messages);

        const params = {
            model: activeModel,
            max_tokens: maxTokens,
            messages: anthMessages,
        };
        if (system) params.system = system;
        if (useTools && tools?.length) params.tools = this.toAnthropicTools(tools);

        const resp = await this.client.messages.create(params);
        return this._standardize(resp);
    }
}

module.exports = ClaudeProvider;
