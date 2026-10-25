const sessionId = crypto.randomUUID();
const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("message");
const customer = document.getElementById("customer");

function addMessage(text, ...classes) {
  const el = document.createElement("div");
  el.className = ["msg", ...classes].join(" ");
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

function showTyping() {
  const el = document.createElement("div");
  el.className = "msg bot typing";
  el.setAttribute("aria-label", "Assistant is working");
  el.innerHTML = "<span></span><span></span><span></span>";
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

fetch("/customers")
  .then((r) => r.json())
  .then((customers) => {
    for (const c of customers) customer.add(new Option(`${c.name} (#${c.id})`, c.id));
  });

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addMessage(message, "user");
  input.value = "";
  form.querySelector("button").disabled = true;
  const typing = showTyping();
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        customer_id: customer.value ? Number(customer.value) : null,
      }),
    });
    if (!response.ok) throw new Error((await response.json()).detail ?? response.statusText);
    const data = await response.json();
    addMessage(data.reply, "bot", data.blocked ? "blocked" : "");
  } catch (error) {
    addMessage(`Something went wrong: ${error.message}`, "bot", "error");
  } finally {
    typing.remove();
    form.querySelector("button").disabled = false;
    input.focus();
  }
});
