# LightAI

Small, local AI chatbot with an optional OpenAI proxy.

Features
- HTTP server: POST `/chat` with JSON `{ "message": "..." }` returns `{ reply, source }`.
- CLI REPL: `node main.js --cli` for interactive chat.
- Optional OpenAI integration: set `OPENAI_API_KEY` and `USE_OPENAI=1` to route queries to OpenAI.

Quick start

1. Install dependencies:

```bash
npm install
```

2. Run the local server:

```bash
npm start
# or
node main.js
```

3. Chat via HTTP:

```bash
curl -s -X POST http://localhost:3000/chat -H 'Content-Type: application/json' -d '{"message":"hello"}'
```

4. Use the REPL:

```bash
npm run cli
# or
node main.js --cli
```

Enable OpenAI (optional)

1. Set your OpenAI API key and enable routing:

```bash
export OPENAI_API_KEY="sk-..."
export USE_OPENAI=1
npm start
```

Notes
- If `openai` SDK isn't installed or `OPENAI_API_KEY` isn't present, the app falls back to a built-in simple rule-based responder.
- This project is a minimal starting point — tell me how you'd like the AI improved (knowledge base, embeddings, more advanced models).
