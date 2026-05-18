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
      const { message } = await request.json();
      if (!message) {
        return new Response(JSON.stringify({ error: 'message required' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }

      const systemPrompt = `You are a blockchain CLI assistant for the Arc Testnet (chain 5042002, native currency USDC).
Parse the user's natural language input and return a JSON object with:
- "action": one of [balance, agent_balance, agent_deposit, agent_withdraw, transfer, gas, block, tx, price, network, help, clear, unknown]
- "params": object with relevant parameters (address, amount, hash, blockNumber, etc.)
- "reply": a short friendly response in the user's language

Example inputs and outputs:
"查余额" -> {"action":"balance","params":{},"reply":"查询你的钱包余额"}
"查一下 0x1234567890123456789012345678901234567890 的余额" -> {"action":"balance","params":{"address":"0x1234567890123456789012345678901234567890"},"reply":"查询该地址余额"}
"存 5 USDC" -> {"action":"agent_deposit","params":{"amount":5},"reply":"存入 5 USDC 到 Agent 钱包"}
"提现 3 个" -> {"action":"agent_withdraw","params":{"amount":3},"reply":"从 Agent 钱包提现 3 USDC"}
"agent 钱包多少钱" -> {"action":"agent_balance","params":{},"reply":"查询 Agent 钱包余额"}
"转账 10 USDC 给 0xabcd..." -> {"action":"transfer","params":{"to":"0xabcd...","amount":10},"reply":"转账 10 USDC"}
"手续费" -> {"action":"gas","params":{},"reply":"查询当前 gas 价格"}
"最新区块" -> {"action":"block","params":{},"reply":"查询最新区块"}
"BTC 价格" -> {"action":"price","params":{},"reply":"查询 BTC 价格"}
"怎么用" -> {"action":"help","params":{},"reply":"显示帮助"}
"你好" -> {"action":"unknown","params":{},"reply":"你好！需要什么帮助？"}

Only return valid JSON. No markdown, no code blocks, no explanation.`;

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
            { role: 'user', content: message },
          ],
          temperature: 0.1,
          max_tokens: 200,
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
      const content = data.choices[0].message.content;

      // Strip markdown code blocks if any
      let json = content.trim();
      json = json.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '');

      let parsed;
      try {
        parsed = JSON.parse(json);
      } catch {
        // Fallback: try to extract JSON from the response
        const match = json.match(/\{[\s\S]*\}/);
        parsed = match ? JSON.parse(match[0]) : { action: 'unknown', params: {}, reply: content };
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
