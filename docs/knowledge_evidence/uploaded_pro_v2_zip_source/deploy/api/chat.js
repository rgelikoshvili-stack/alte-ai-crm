// Vercel serverless function — proxies frontend → Anthropic API.
// The browser calls /api/chat; we forward to api.anthropic.com using
// the secret API key that lives in the ANTHROPIC_API_KEY env var.

export default async function handler(req, res) {
  // CORS (only needed if you host the static HTML on a different domain;
  // for same-origin deploys you can remove this block).
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({
      error: 'ANTHROPIC_API_KEY არ არის გარემოს ცვლადებში დაყენებული. დაამატე Vercel-ის Project Settings → Environment Variables-ში.',
    });
  }

  const { system, messages } = req.body || {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'messages მასივი ცარიელია' });
  }

  // Optional safety: cap conversation length (last 30 turns)
  const trimmed = messages.slice(-30);

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 1024,
        system: system || undefined,
        messages: trimmed,
      }),
    });

    const data = await r.json();
    if (!r.ok) {
      return res.status(r.status).json({
        error: data?.error?.message || 'Anthropic API ცდომილება',
      });
    }
    const text = data.content?.[0]?.text || '';
    return res.status(200).json({ text });
  } catch (e) {
    return res.status(500).json({ error: e.message || String(e) });
  }
}
