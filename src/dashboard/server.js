const express = require('express');
const path = require('path');

function startDashboard(client, agent) {
    const app = express();
    const PORT = parseInt(process.env.DASHBOARD_PORT || '3000');
    const USER = process.env.DASHBOARD_USER || 'admin';
    const PASS = process.env.DASHBOARD_PASS || 'aylin123';

    app.use(express.json());
    app.use(express.static(path.join(__dirname, 'public')));

    // Basic auth middleware
    function auth(req, res, next) {
        const header = req.headers.authorization || '';
        const b64 = header.replace('Basic ', '');
        let ok = false;
        try {
            const [u, p] = Buffer.from(b64, 'base64').toString().split(':');
            ok = u === USER && p === PASS;
        } catch (_) {}
        if (!ok) {
            res.set('WWW-Authenticate', 'Basic realm="Aylin Dashboard"');
            return res.status(401).send('Unauthorized');
        }
        next();
    }

    app.use('/api', auth);

    // GET /api/chats — list all active chats
    app.get('/api/chats', async (req, res) => {
        try {
            const chats = await client.getChats();
            const list = chats
                .filter(c => !c.isGroup)
                .slice(0, 50)
                .map(c => ({
                    id: c.id._serialized,
                    name: c.name || c.id.user,
                    unread: c.unreadCount,
                    lastMessage: c.lastMessage?.body?.slice(0, 80) || '',
                    timestamp: c.lastMessage?.timestamp
                }));
            res.json(list);
        } catch (e) {
            res.status(500).json({ error: e.message });
        }
    });

    // GET /api/chat/:id — messages for a chat
    app.get('/api/chat/:id', async (req, res) => {
        try {
            const chat = await client.getChatById(req.params.id);
            const messages = await chat.fetchMessages({ limit: 50 });
            res.json(messages.map(m => ({
                id: m.id.id,
                from: m.fromMe ? 'bot' : 'user',
                body: m.body,
                timestamp: m.timestamp,
                type: m.type
            })));
        } catch (e) {
            res.status(500).json({ error: e.message });
        }
    });

    // POST /api/send — send a message
    app.post('/api/send', async (req, res) => {
        const { to, text } = req.body;
        if (!to || !text) return res.status(400).json({ error: 'to and text required' });
        try {
            await client.sendMessage(to, text);
            res.json({ ok: true });
        } catch (e) {
            res.status(500).json({ error: e.message });
        }
    });

    // GET /api/stats
    app.get('/api/stats', (req, res) => {
        res.json(agent.getStats());
    });

    app.listen(PORT, () => {
        console.log(`📊 Dashboard: http://localhost:${PORT} (user: ${USER})`);
    });
}

module.exports = { startDashboard };
