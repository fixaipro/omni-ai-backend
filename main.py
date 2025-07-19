<script>
const form = document.getElementById('aiForm');
const output = document.getElementById('output');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const query = document.getElementById('query').value;
  output.innerHTML = '<p>⏳ Thinking...</p>';
  try {
    const res = await fetch('https://omni-ai-backend.onrender.com/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
      mode: 'cors'
    });
    const data = await res.json();
    output.innerHTML = `
      <div class="response-block"><div class="ai-label"><span>🧠</span>GPT (OpenAI)</div><p>${data.gpt}</p></div>
      <div class="response-block"><div class="ai-label"><span>🔮</span>Gemini (Google)</div><p>${data.gemini}</p></div>
      <div class="response-block"><div class="ai-label"><span>🤖</span>Claude (Anthropic)</div><p>${data.claude}</p></div>
      <div class="response-block summary"><div class="ai-label"><span>🧾</span><strong>Summary</strong></div><p><strong>${data.summary}</strong></p></div>
    `;
  } catch (err) {
    output.innerHTML = '<p style="color:red;">❌ Error: ' + err.message + '</p>';
    console.error(err);
  }
});
</script>
