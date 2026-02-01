# LightAI

Small, self-contained local AI chatbot.

Features
- HTTP server: POST `/chat` with JSON `{ "message": "..." }` returns `{ reply, source }`.
- CLI REPL: `node main.js --cli` for interactive chat.
No external AI providers are required; this project runs locally with its own simple AI engine.

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

Notes
- This project is intentionally self-contained and does not call external AI services.
- It provides a simple rule-based/local-response engine as a starting point. Tell me how you'd like the AI improved (knowledge base, retrieval, richer conversational skills).
