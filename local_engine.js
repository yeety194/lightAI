// Simple local conversational engine with light context memory and a helpful persona
const fs = require('fs');
const path = require('path');

module.exports = function createEngine(opts = {}) {
  const persona = opts.persona || 'concise, helpful, friendly assistant';
  const memories = new Map(); // sessionId -> { history: [ {role:'user'|'assistant', text} ] }
  let kb = [];
  try {
    const kbPath = path.join(__dirname, 'kb.json');
    if (fs.existsSync(kbPath)) kb = JSON.parse(fs.readFileSync(kbPath, 'utf8'));
  } catch (e) {
    // ignore KB load errors
  }

  function getMemory(sessionId) {
    if (!memories.has(sessionId)) memories.set(sessionId, { history: [] });
    return memories.get(sessionId);
  }

  function remember(sessionId, role, text) {
    const mem = getMemory(sessionId);
    mem.history.push({ role, text, t: Date.now() });
    if (mem.history.length > 50) mem.history.shift();
  }

  function lastUser(sessionId) {
    const mem = getMemory(sessionId).history.slice().reverse();
    return mem.find(m => m.role === 'user')?.text || null;
  }

  async function reply(message, sessionId = 'default') {
    const raw = String(message || '').trim();
    const m = raw.toLowerCase();
    remember(sessionId, 'user', raw);

    // KB lookup: find best match by token overlap
    const kbAnswer = searchKB(raw);
    if (kbAnswer) {
      remember(sessionId, 'assistant', kbAnswer.answer);
      return kbAnswer.answer;
    }

    // Arithmetic / calculation: phrases like "calculate 2+2", "what is 3*(4+1)" or raw expressions
    const calcMatch = raw.match(/(?:calculate|what is|compute)?\s*([0-9+\-*/(). ^]+)$/i);
    if (calcMatch && calcMatch[1]) {
      try {
        const expr = calcMatch[1].trim();
        const val = evaluateExpression(expr);
        const out = formatAnswer(String(val), `calculation result for ${expr}`);
        remember(sessionId, 'assistant', out);
        return out;
      } catch (e) {
        // fall through to other handlers
      }
    }

    // Linear equation solve: simple single-variable linear forms like "solve 2x+3=7"
    const linMatch = raw.match(/solve\s+([+\-]?\d*\.?\d*)?([a-zA-Z])\s*([+\-]\s*\d+\.?\d*)?\s*=\s*([+\-]?\d+\.?\d*)/i);
    if (linMatch) {
      try {
        const aRaw = linMatch[1];
        const varName = linMatch[2];
        const bRaw = linMatch[3] ? linMatch[3].replace(/\s+/g, '') : '+0';
        const cRaw = linMatch[4];
        const a = aRaw === '' || aRaw === undefined ? 1 : Number(aRaw);
        const b = Number(bRaw);
        const c = Number(cRaw);
        if (Number.isFinite(a) && Number.isFinite(b) && Number.isFinite(c) && a !== 0) {
          const x = (c - b) / a;
          const out = formatAnswer(`${varName} = ${x}`, `solved ${a}${varName}${b>=0?'+':''}${b} = ${c}`);
          remember(sessionId, 'assistant', out);
          return out;
        }
      } catch (e) {
        // ignore
      }
    }

    // Unit conversion: "convert 5 km to m"
    const convMatch = raw.match(/convert\s+([+\-]?\d*\.?\d+)\s*(\w+)\s+to\s+(\w+)/i);
    if (convMatch) {
      const v = Number(convMatch[1]);
      const from = convMatch[2].toLowerCase();
      const to = convMatch[3].toLowerCase();
      const conv = convertUnit(v, from, to);
      if (conv !== null) {
        const out = formatAnswer(String(conv), `${v} ${from} = ${conv} ${to}`);
        remember(sessionId, 'assistant', out);
        return out;
      }
    }

    // Helpful persona intro when user asks 'who are you' or similar
    if (/\b(who (are|r) you|what are you)\b/.test(m)) {
      const out = `I'm LightAI — a ${persona}. I run locally and aim to be concise and helpful.`;
      remember(sessionId, 'assistant', out);
      return out;
    }

    if (/^(hi|hello|hey)\b/.test(m)) {
      const out = 'Hello — I am LightAI, your local assistant.';
      remember(sessionId, 'assistant', out);
      return out;
    }

    if (m.includes('time')) {
      const out = `Local server time: ${new Date().toLocaleString()}`;
      remember(sessionId, 'assistant', out);
      return out;
    }

    if (m.includes('help')) {
      const out = 'I can answer simple questions, echo text, or keep short context across messages. Try: "tell me a joke", "what time is it", or ask me to remember something.';
      remember(sessionId, 'assistant', out);
      return out;
    }

    if (m.includes('joke')) {
      const out = 'Why did the programmer quit his job? Because he didn’t get arrays (a raise).';
      remember(sessionId, 'assistant', out);
      return out;
    }

    if (m.includes('remember')) {
      const match = raw.match(/remember[:\s]+(.+)/i);
      if (match) {
        const note = match[1].trim();
        remember(sessionId, 'user_note', note);
        const out = `Okay, I'll remember: "${note}".`;
        remember(sessionId, 'assistant', out);
        return out;
      }
    }

    // If user references 'that' or 'previous', try to recall last user message
    if (/\b(that|previous|earlier)\b/.test(m)) {
      const last = lastUser(sessionId);
      if (last) {
        const out = `Earlier you said: "${last}". Want to expand on that?`;
        remember(sessionId, 'assistant', out);
        return out;
      }
    }

    // Small Q/A patterns
    if (/\bhow are you\b/.test(m)) {
      const out = "I'm a local assistant — ready to help. Concise and focused.";
      remember(sessionId, 'assistant', out);
      return out;
    }

    // Fallback: echo with an offer to clarify or take an action
    const out = formatAnswer(`You said: "${raw}".`, 'I can clarify, summarize, or try another answer — what would you like me to do?');
    remember(sessionId, 'assistant', out);
    return out;
  }

  function tokenize(s) {
    return String(s || '').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
  }

  function scoreOverlap(a, b) {
    const ta = new Set(tokenize(a));
    const tb = new Set(tokenize(b));
    if (!ta.size || !tb.size) return 0;
    let common = 0;
    for (const t of ta) if (tb.has(t)) common++;
    return common / Math.max(ta.size, tb.size);
  }

  function searchKB(query) {
    if (!kb || !kb.length) return null;
    let best = null;
    for (const item of kb) {
      const s = scoreOverlap(query, item.question || item.id || '');
      if (!best || s > best.score) best = { item, score: s };
    }
    if (best && best.score >= 0.35) return { answer: best.item.answer, score: best.score };
    return null;
  }

  return { reply, getMemory };
};

// --- Utilities: expression evaluator, formatting, conversions ---

function formatAnswer(answer, explanation) {
  if (!explanation) return answer;
  return `${answer} — ${explanation}`;
}

// Shunting-yard + RPN evaluator for safe arithmetic expressions
function evaluateExpression(expr) {
  // allow numbers, parentheses, + - * / ^ and spaces
  const ops = {
    '+': { prec: 1, assoc: 'L' },
    '-': { prec: 1, assoc: 'L' },
    '*': { prec: 2, assoc: 'L' },
    '/': { prec: 2, assoc: 'L' },
    '^': { prec: 3, assoc: 'R' },
  };

  const output = [];
  const stack = [];
  const tokens = expr.replace(/\s+/g, '').match(/\d*\.?\d+|[+\-*/^()]/g);
  if (!tokens) throw new Error('invalid expression');
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (/^\d/.test(t)) {
      output.push(Number(t));
    } else if (t in ops) {
      while (stack.length) {
        const top = stack[stack.length - 1];
        if (top in ops && ((ops[t].assoc === 'L' && ops[t].prec <= ops[top].prec) || (ops[t].assoc === 'R' && ops[t].prec < ops[top].prec))) {
          output.push(stack.pop());
          continue;
        }
        break;
      }
      stack.push(t);
    } else if (t === '(') {
      stack.push(t);
    } else if (t === ')') {
      while (stack.length && stack[stack.length - 1] !== '(') output.push(stack.pop());
      if (!stack.length) throw new Error('mismatched parentheses');
      stack.pop();
    } else {
      throw new Error('invalid token');
    }
  }
  while (stack.length) {
    const op = stack.pop();
    if (op === '(' || op === ')') throw new Error('mismatched parentheses');
    output.push(op);
  }
  // evaluate RPN
  const evalStack = [];
  for (const t of output) {
    if (typeof t === 'number') evalStack.push(t);
    else {
      const b = evalStack.pop();
      const a = evalStack.pop();
      switch (t) {
        case '+': evalStack.push(a + b); break;
        case '-': evalStack.push(a - b); break;
        case '*': evalStack.push(a * b); break;
        case '/': evalStack.push(a / b); break;
        case '^': evalStack.push(Math.pow(a, b)); break;
        default: throw new Error('invalid op');
      }
    }
  }
  if (evalStack.length !== 1) throw new Error('invalid evaluation');
  return evalStack[0];
}

function convertUnit(value, from, to) {
  const map = {
    'km': { 'm': v => v * 1000 },
    'm': { 'cm': v => v * 100, 'km': v => v / 1000 },
    'cm': { 'm': v => v / 100 },
    'kg': { 'g': v => v * 1000, 'lb': v => v * 2.20462 },
    'lb': { 'kg': v => v / 2.20462 },
  };
  if (map[from] && map[from][to]) return map[from][to](value);
  return null;
}
