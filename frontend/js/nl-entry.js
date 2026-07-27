function toLocalInputValue(isoString) {
  const d = new Date(isoString);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function renderNlEntry() {
  const container = document.getElementById("nl-entry-container");
  container.classList.remove("hidden");
  container.innerHTML = `
    <h2>Quick add (natural language)</h2>
    <div class="row">
      <input type="text" id="nl-text" placeholder="e.g. remind me to call mom Sunday evening" style="flex:1" />
      <button id="nl-parse-btn" type="button">Parse</button>
    </div>
    <p id="nl-error" class="banner hidden"></p>
    <div id="nl-proposal" class="hidden">
      <div class="row">
        <label>Title <input type="text" id="nl-title" /></label>
        <label>Due <input type="datetime-local" id="nl-due" /></label>
        <label>Priority
          <select id="nl-priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
      </div>
      <div class="row">
        <label>Tags <input type="text" id="nl-tags" placeholder="comma,separated" /></label>
        <label>Category <input type="text" id="nl-category" placeholder="optional" /></label>
      </div>
      <button id="nl-save-btn" type="button">Save Task</button>
    </div>
  `;

  const errorEl = document.getElementById("nl-error");

  document.getElementById("nl-parse-btn").addEventListener("click", async () => {
    const text = document.getElementById("nl-text").value.trim();
    if (!text) return;
    errorEl.classList.add("hidden");
    try {
      const proposal = await api.parseTask(text);
      document.getElementById("nl-title").value = proposal.title || "";
      document.getElementById("nl-due").value = proposal.due_datetime
        ? toLocalInputValue(proposal.due_datetime)
        : "";
      document.getElementById("nl-priority").value = proposal.priority || "medium";
      document.getElementById("nl-tags").value = (proposal.tags || []).join(", ");
      document.getElementById("nl-category").value = proposal.category || "";
      document.getElementById("nl-proposal").classList.remove("hidden");
    } catch (err) {
      errorEl.textContent = `Couldn't parse (${err.message}). Use the manual form below instead.`;
      errorEl.classList.remove("hidden");
    }
  });

  document.getElementById("nl-save-btn").addEventListener("click", async () => {
    const title = document.getElementById("nl-title").value.trim();
    if (!title) return;
    const due = document.getElementById("nl-due").value;
    const priority = document.getElementById("nl-priority").value;
    const tags = document
      .getElementById("nl-tags")
      .value.split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    const categoryName = document.getElementById("nl-category").value.trim();

    let categoryId = null;
    if (categoryName) {
      const match = categories.find((c) => c.name.toLowerCase() === categoryName.toLowerCase());
      categoryId = match ? match.id : null;
    }

    await api.createTask({
      title,
      due_datetime: due ? new Date(due).toISOString() : null,
      priority,
      category_id: categoryId,
      tags,
    });

    document.getElementById("nl-text").value = "";
    document.getElementById("nl-proposal").classList.add("hidden");
    await refreshTasks();
  });
}
