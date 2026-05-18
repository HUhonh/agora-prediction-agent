export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response('POST only', { status: 405 });
    }

    const DEEPSEEK_KEY = env.DEEPSEEK_API_KEY;
    if (!DEEPSEEK_KEY) {
      return new Response(JSON.stringify({ error: 'API key not configured' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    try {
      const { message, context } = await request.json();
      if (!message) {
        return new Response(JSON.stringify({ error: 'message required' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }

      const ctxStr = context ? `
Current market context:
- BTC price: $${context.btcPrice || 'N/A'}
- 5-min market: ${context.marketSlug || 'N/A'}
- Time remaining in round: ${context.timeRemaining || 'N/A'}
- Current strategy: ${context.strategy || 'N/A'}
` : '';

      const systemPrompt = `You are a professional crypto prediction market analyst specializing in BTC 5-minute binary markets on Polymarket. You help traders make informed decisions.

Your personality: sharp, data-driven, concise. You think in probabilities.

When analyzing, consider:
- Recent BTC price action and volatility
- Remaining time in the 5-minute window (later = more certainty)
- Market microstructure (bid-ask spread, volume)
- Common patterns at specific times (e.g., US market open volatility)
- Risk-reward ratios and Kelly criterion thinking

Respond in the user's language. Return valid JSON only:
{
  "analysis": "Your detailed analysis (2-4 sentences)",
  "direction": "up" | "down" | "neutral",
  "probability": number between 0-1 (your confidence in the direction),
  "confidence": "high" | "medium" | "low",
  "recommendation": "buy_up" | "buy_down" | "wait" | "avoid",
  "priceTarget": number (the max price you'd pay for this bet, 0-1),
  "reasoning": "Bullet points of key factors",
  "risks": "Key risk factors"
}

No markdown, no code blocks. Only the JSON object.`;

      const dsResp = await fetch('https://api.deepseek.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DEEPSEEK_KEY}`,
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: ctxStr + '\nUser question: ' + message },
          ],
          temperature: 0.4,
          max_tokens: 800,
        }),
      });

      if (!dsResp.ok) {
        const err = await dsResp.text();
        return new Response(JSON.stringify({ error: 'LLM error: ' + err.slice(0, 200) }), {
          status: 502,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }

      const data = await dsResp.json();
      const content = data.choices[0].message.content.trim();

      let json = content.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '').trim();

      let parsed;
      try {
        parsed = JSON.parse(json);
      } catch {
        const match = json.match(/\{[\s\S]*\}/);
        parsed = match ? JSON.parse(match[0]) : { analysis: content, direction: 'neutral', probability: 0.5, confidence: 'low', recommendation: 'wait' };
      }

      return new Response(JSON.stringify(parsed), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }
  },
};
