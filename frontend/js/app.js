let categories = [];
let aiEnabled = false;

function fmt(dt) {
  if (!dt) return "";
  return new Date(dt).toLocaleString();
}

function categoryName(id) {
  const c = categories.find((c) => c.id === id);
  return c ? c.name : "";
}

function categoryColor(id) {
  const c = categories.find((c) => c.id === id);
  return c ? c.color : "#999";
}

async function refreshHealth() {
  const banner = document.getElementById("ai-status-banner");
  try {
    const health = await api.health();
    aiEnabled = health.ai_enabled;
    if (!aiEnabled) {
      banner.textContent =
        "AI features are unavailable (no ANTHROPIC_API_KEY configured). Manual task entry still works fully.";
      banner.classList.remove("hidden");
    } else {
      banner.classList.add("hidden");
      renderNlEntry();
    }
  } catch {
    banner.textContent = "Could not reach the server.";
    banner.classList.remove("hidden");
  }
}

async function refreshCategories() {
  categories = await api.listCategories();

  const select = document.getElementById("task-category");
  select.innerHTML = '<option value="">None</option>';
  for (const c of categories) {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.name;
    select.appendChild(opt);
  }

  const list = document.getElementById("category-list");
  list.innerHTML = "";
  for (const c of categories) {
    const li = document.createElement("li");
    li.className = "category-item";
    li.innerHTML = `
      <span class="color-dot" style="background:${c.color || "#999"}"></span>
      <span>${c.name}</span>
      <button data-id="${c.id}" class="delete-category">Delete</button>
    `;
    list.appendChild(li);
  }

  list.querySelectorAll(".delete-category").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await api.deleteCategory(btn.dataset.id);
      await refreshCategories();
      await refreshTasks();
    });
  });
}

async function refreshTasks() {
  const status = document.getElementById("status-filter").value;
  const tasks = await api.listTasks(status || undefined);

  const list = document.getElementById("task-list");
  list.innerHTML = "";

  for (const t of tasks) {
    const li = document.createElement("li");
    li.className = "task";
    const meta = [
      t.due_datetime ? `Due ${fmt(t.due_datetime)}` : null,
      t.priority,
      t.category_id ? categoryName(t.category_id) : null,
      t.recurrence_rule ? `repeats ${t.recurrence_rule}` : null,
      t.snooze_until ? `snoozed to ${fmt(t.snooze_until)}` : null,
    ]
      .filter(Boolean)
      .join(" · ");

    li.innerHTML = `
      <div class="task-main">
        <span class="task-title ${t.status === "completed" ? "completed" : ""}">${t.title}</span>
        <span class="task-meta">${meta}</span>
      </div>
      <div class="task-actions">
        ${t.status !== "completed" ? `<button class="complete" data-id="${t.id}">Done</button>` : ""}
        ${t.status !== "completed" ? `<button class="snooze" data-id="${t.id}">Snooze</button>` : ""}
        ${aiEnabled && t.status !== "completed" ? `<button class="categorize" data-id="${t.id}">Suggest category</button>` : ""}
        <button class="delete" data-id="${t.id}">Delete</button>
      </div>
    `;
    list.appendChild(li);
  }

  list.querySelectorAll(".complete").forEach((btn) =>
    btn.addEventListener("click", async () => {
      await api.completeTask(btn.dataset.id);
      await refreshTasks();
    })
  );
  list.querySelectorAll(".delete").forEach((btn) =>
    btn.addEventListener("click", async () => {
      await api.deleteTask(btn.dataset.id);
      await refreshTasks();
    })
  );
  list.querySelectorAll(".categorize").forEach((btn) =>
    btn.addEventListener("click", async () => {
      try {
        const suggestion = await api.categorizeTask(btn.dataset.id, true);
        await refreshTasks();
        alert(`Set to "${suggestion.category}" / ${suggestion.priority}${suggestion.reasoning ? `\n${suggestion.reasoning}` : ""}`);
      } catch (err) {
        alert(`Couldn't suggest a category: ${err.message}`);
      }
    })
  );
  list.querySelectorAll(".snooze").forEach((btn) =>
    btn.addEventListener("click", async () => {
      const value = prompt("Snooze until (YYYY-MM-DDTHH:MM):");
      if (!value) return;
      await api.snoozeTask(btn.dataset.id, new Date(value).toISOString());
      await refreshTasks();
    })
  );
}

document.getElementById("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("task-title").value.trim();
  const description = document.getElementById("task-description").value.trim();
  const due = document.getElementById("task-due").value;
  const priority = document.getElementById("task-priority").value;
  const categoryId = document.getElementById("task-category").value;
  const tags = document.getElementById("task-tags").value
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);
  const recurrence = document.getElementById("task-recurrence").value;

  await api.createTask({
    title,
    description: description || null,
    due_datetime: due ? new Date(due).toISOString() : null,
    priority,
    category_id: categoryId ? Number(categoryId) : null,
    tags,
    recurrence_rule: recurrence || null,
  });

  e.target.reset();
  await refreshTasks();
});

document.getElementById("category-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("category-name").value.trim();
  const color = document.getElementById("category-color").value;
  await api.createCategory({ name, color });
  e.target.reset();
  await refreshCategories();
});

document.getElementById("status-filter").addEventListener("change", refreshTasks);

(async function init() {
  await refreshHealth();
  await refreshCategories();
  await refreshTasks();
})();
