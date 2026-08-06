const API_URL = "http://localhost:8001/query";

const form = document.getElementById("query-form");
const questionInput = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const result = document.getElementById("result");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  showStatus("Thinking…");
  askBtn.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }

    const data = await response.json();
    renderAnswer(data);
  } catch (err) {
    showStatus(`Something went wrong: ${err.message}`, true);
  } finally {
    askBtn.disabled = false;
  }
});

function showStatus(message, isError = false) {
  result.classList.remove("hidden");
  sourcesEl.innerHTML = "";
  answerEl.innerHTML = `<p class="status${isError ? " error" : ""}">${escapeHtml(message)}</p>`;
}

function renderAnswer(data) {
  result.classList.remove("hidden");
  answerEl.innerHTML = formatAnswer(data.answer || "");

  const sources = data.sources || [];
  if (sources.length === 0) {
    sourcesEl.innerHTML = "";
    return;
  }

  const items = sources
    .map((src) => `<li><a href="${escapeHtml(src)}" target="_blank" rel="noopener">${escapeHtml(src)}</a></li>`)
    .join("");
  sourcesEl.innerHTML = `<h3>Sources</h3><ul>${items}</ul>`;
}

// Minimal markdown: escape HTML, then apply **bold** so the answer stays readable.
function formatAnswer(text) {
  return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
