#!/usr/bin/env node
const express = require('express');
const readline = require('readline');

let openaiClient = null;
if (process.env.OPENAI_API_KEY) {
	try {
		const { Configuration, OpenAIApi } = require('openai');
		const cfg = new Configuration({ apiKey: process.env.OPENAI_API_KEY });
		openaiClient = new OpenAIApi(cfg);
		console.log('OpenAI client initialized (will be used if enabled).');
	} catch (e) {
		// If the `openai` SDK isn't available we provide a lightweight fetch fallback
		console.warn('OpenAI SDK not available, will try HTTP fetch fallback to OpenAI API.');
		openaiClient = { fetchFallback: true, apiKey: process.env.OPENAI_API_KEY };
	}
}

async function callOpenAI(message) {
	if (!openaiClient) throw new Error('OpenAI client not initialized');
	// Preferred: use SDK if present
	if (typeof openaiClient.createChatCompletion === 'function') {
		const resp = await openaiClient.createChatCompletion({
			model: 'gpt-3.5-turbo',
			messages: [{ role: 'user', content: message }],
			max_tokens: 500,
			temperature: 0.7,
		});
		return resp.data.choices[0].message.content.trim();
	}

	// Fallback: direct HTTP call to OpenAI REST API using fetch
	if (openaiClient.fetchFallback) {
		const fetchFn = globalThis.fetch || (await import('node-fetch')).default;
		const res = await fetchFn('https://api.openai.com/v1/chat/completions', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${openaiClient.apiKey}`,
			},
			body: JSON.stringify({
				model: 'gpt-3.5-turbo',
				messages: [{ role: 'user', content: message }],
				max_tokens: 500,
				temperature: 0.7,
			}),
		});
		const data = await res.json();
		if (!res.ok) throw new Error(data.error?.message || JSON.stringify(data));
		return data.choices[0].message.content.trim();
	}

	throw new Error('OpenAI client not available');
}

function localAI(message) {
	const m = String(message || '').trim().toLowerCase();
	if (!m) return "I didn't get any text — say something.";
	if (/^(hi|hello|hey)\b/.test(m)) return 'Hello — I am LightAI, your local assistant.';
	if (m.includes('time')) return `Local server time: ${new Date().toLocaleString()}`;
	if (m.includes('help')) return 'Try asking a question, say "time", or say "tell me a joke".';
	if (m.includes('joke')) return 'Why did the programmer quit his job? Because he didn’t get arrays (a raise).';
	return `You said: "${message}". I can echo, answer simple questions, or route to OpenAI if configured.`;
}

async function getReply(message, options = {}) {
	const envEnabled = ['1', 'true', 'yes'].includes(String(process.env.USE_OPENAI || '').toLowerCase());
	const useOpenAI = Boolean(options.useOpenAI) || (envEnabled && openaiClient);
	if (useOpenAI) {
		try {
			return await callOpenAI(message);
		} catch (e) {
			console.warn('OpenAI call failed, falling back to local AI:', e.message || e);
			return localAI(message);
		}
	}
	return localAI(message);
}

function startServer(port = 3000) {
	const app = express();
	app.use(express.json());

	app.get('/', (req, res) => {
		res.send({
			name: 'LightAI',
			version: '0.1.0',
			openai_available: !!openaiClient,
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
			const reply = await getReply(message, { useOpenAI });
			res.json({ reply, source: useOpenAI ? 'openai' : 'local' });
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

