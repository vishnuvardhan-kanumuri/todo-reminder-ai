const API_BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(`${res.status}: ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  health: () => fetch("/health").then((r) => r.json()),

  listTasks: (status) =>
    request(`/tasks${status ? `?status=${encodeURIComponent(status)}` : ""}`),
  createTask: (data) =>
    request("/tasks", { method: "POST", body: JSON.stringify(data) }),
  updateTask: (id, data) =>
    request(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteTask: (id) => request(`/tasks/${id}`, { method: "DELETE" }),
  completeTask: (id) => request(`/tasks/${id}/complete`, { method: "POST" }),
  snoozeTask: (id, until) =>
    request(`/tasks/${id}/snooze`, {
      method: "POST",
      body: JSON.stringify({ until }),
    }),

  listCategories: () => request("/categories"),
  createCategory: (data) =>
    request("/categories", { method: "POST", body: JSON.stringify(data) }),
  deleteCategory: (id) => request(`/categories/${id}`, { method: "DELETE" }),
};
