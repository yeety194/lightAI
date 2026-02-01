#!/usr/bin/env node
const readline = require('readline');
const createEngine = require('./local_engine');

const engine = createEngine({ persona: 'concise, helpful, friendly assistant' });

// This project now uses a self-contained local AI engine only.
// No external AI providers are contacted; everything runs locally.

function localAI(message) {
	const m = String(message || '').trim().toLowerCase();
	if (!m) return "I didn't get any text — say something.";
	if (/^(hi|hello|hey)\b/.test(m)) return 'Hello — I am LightAI, your local assistant.';
	if (m.includes('time')) return `Local server time: ${new Date().toLocaleString()}`;
	if (m.includes('help')) return 'Try asking a question, say "time", or say "tell me a joke".';
	if (m.includes('joke')) return 'Why did the programmer quit his job? Because he didn’t get arrays (a raise).';
	// Simple fallback: echo and invite clarification.
	return `You said: "${message}". I can echo, answer simple questions, or try to clarify.`;
}

async function getReply(message, options = {}) {
	const sessionId = options.sessionId || (options.session || 'default');
	return engine.reply(message, sessionId);
}

function startServer(port = 3000) {
	let express;
	try {
		express = require('express');
	} catch (e) {
		console.warn('`express` is not installed. Falling back to CLI REPL. To enable the HTTP server run `npm install`.');
		return startREPL();
	}

	const app = express();
	app.use(express.json());

	app.get('/', (req, res) => {
		res.send({
			name: 'LightAI',
			version: '0.1.0',
			instructions: 'POST /chat { "message": "..." } or run `node main.js --cli` for REPL',
		});
	});

	app.post('/chat', async (req, res) => {
		const message = req.body && (req.body.message || req.body.msg);
		if (!message) return res.status(400).json({ error: 'missing `message` in JSON body' });
		try {
			// allow per-request override via JSON `use_openai`, `useOpenAI`, or header `x-use-openai: 1`
			const headerFlag = String(req.get('x-use-openai') || '').toLowerCase();
			const reqFlag = req.body.use_openai || req.body.useOpenAI || false;
			const useOpenAI = reqFlag || headerFlag === '1' || headerFlag === 'true';
			const reply = await getReply(message);
			res.json({ reply, source: 'local' });
		} catch (e) {
			res.status(500).json({ error: e.message || String(e) });
		}
	});

	app.listen(port, () => {
		console.log(`LightAI server listening on http://localhost:${port}`);
	});
}

function startREPL() {
	const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
	console.log('LightAI REPL. Type a message and press enter. Ctrl+C to exit.');
	rl.setPrompt('You> ');
	rl.prompt();
	rl.on('line', async (line) => {
		const raw = String(line || '');
		const trimmed = raw.trim();
		if (!trimmed) { rl.prompt(); return; }

		// Allow forcing OpenAI per-line with a prefix: `/openai ` or `/o `
		let forceOpenAI = false;
		let messageText = trimmed;
		if (trimmed.startsWith('/openai ')) {
			forceOpenAI = true;
			messageText = trimmed.slice(8).trim();
		} else if (trimmed.startsWith('/o ')) {
			forceOpenAI = true;
			messageText = trimmed.slice(3).trim();
		}

		try {
			const reply = await getReply(messageText, { useOpenAI: forceOpenAI });
			console.log('AI>', reply);
		} catch (e) {
			console.error('Error:', e.message || e);
		}
		rl.prompt();
	});
}

if (require.main === module) {
	if (process.argv.includes('--cli')) return startREPL();
	const portArgIndex = process.argv.indexOf('--port');
	const port = portArgIndex !== -1 ? Number(process.argv[portArgIndex + 1]) || 3000 : (process.env.PORT ? Number(process.env.PORT) : 3000);
	startServer(port);
}

