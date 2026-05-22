const state = {
  apiBase: localStorage.getItem("alte_api_base") || "http://127.0.0.1:8000",
  token: localStorage.getItem("alte_access_token") || "",
  limit: Number(localStorage.getItem("alte_operator_limit") || 20),
  activeView: "dashboard",
  pipelines: [],
};

const titles = {
  dashboard: ["Dashboard", "Live operator overview from the CRM backend."],
  inbox: ["Inbox", "Website chat conversations and handover queue."],
  leads: ["Leads", "Admissions leads, qualification status and source filters."],
  pipeline: ["Pipeline", "Stage-based admissions board."],
  tasks: ["Tasks", "Follow-up workload and overdue work."],
  knowledge: ["Knowledge", "Approved source and snippet governance."],
  analytics: ["Analytics", "Admissions performance, SLA, source coverage and AI quality."],
  settings: ["Settings", "Local operator workspace settings."],
};

const $ = (id) => document.getElementById(id);

function setStatus(message, isError = false) {
  const bar = $("statusBar");
  bar.textContent = message || "";
  bar.classList.toggle("error", isError);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function display(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return date.toLocaleString("ka-GE", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function badge(value, extra = "") {
  if (!value && value !== 0) return "";
  return `<span class="badge ${escapeHtml(extra || String(value).toLowerCase())}">${escapeHtml(value)}</span>`;
}

async function apiGet(path, params = {}) {
  const url = new URL(path, state.apiBase);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  const headers = {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(url, { headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${text.slice(0, 160)}`);
  }
  return response.json();
}

async function apiPost(path, payload = {}) {
  const url = new URL(path, state.apiBase);
  const headers = { "Content-Type": "application/json" };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${text.slice(0, 160)}`);
  }
  return response.json();
}

function listEmpty(message = "No data yet.") {
  return `<div class="list-empty">${escapeHtml(message)}</div>`;
}

function renderMetricCards(data) {
  const cards = [
    ["Customers", data.total_customers],
    ["Leads", data.total_leads],
    ["Open leads", data.open_leads],
    ["Won leads", data.won_leads],
    ["Lost leads", data.lost_leads],
    ["Conversations", data.total_conversations],
    ["Handovers", data.human_handover_count],
    ["Open tasks", data.open_tasks],
    ["Overdue tasks", data.overdue_tasks],
  ];
  $("overviewCards").innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="metric-card">
          <div class="metric-label">${escapeHtml(label)}</div>
          <div class="metric-value">${Number(value || 0)}</div>
        </article>
      `,
    )
    .join("");
}

function renderConversationItem(item) {
  const title = item.customer_name || item.customer_email || item.customer_phone || "Unknown visitor";
  return `
    <article class="list-item" data-conversation-id="${escapeHtml(item.conversation_id)}">
      <div class="item-title">
        <span>${escapeHtml(title)}</span>
        <span>${escapeHtml(formatDate(item.last_message_at || item.created_at))}</span>
      </div>
      <div class="item-meta">${escapeHtml(display(item.last_message_text, "No messages yet"))}</div>
      <div class="badge-row">
        ${badge(item.channel)}
        ${badge(item.status)}
        ${item.human_handover ? badge("handover", "handover") : ""}
        ${item.lead_priority ? badge(item.lead_priority) : ""}
      </div>
    </article>
  `;
}

function renderTaskTable(tasks) {
  if (!tasks.length) return listEmpty("No tasks match the current filters.");
  return `
    <table>
      <thead>
        <tr>
          <th>Title</th>
          <th>Status</th>
          <th>Priority</th>
          <th>Customer</th>
          <th>Due</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        ${tasks
          .map(
            (task) => `
              <tr>
                <td>${escapeHtml(task.title)}</td>
                <td>${badge(task.status)}</td>
                <td>${badge(task.priority)}</td>
                <td>${escapeHtml(display(task.customer_name))}</td>
                <td>${escapeHtml(formatDate(task.due_date))}</td>
                <td>${escapeHtml(formatDate(task.created_at))}</td>
              </tr>
            `,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function renderBarList(id, items) {
  if (!items?.length) {
    $(id).innerHTML = listEmpty();
    return;
  }
  const max = Math.max(...items.map((item) => item.count || 0), 1);
  $(id).innerHTML = items
    .map((item) => {
      const width = Math.round(((item.count || 0) / max) * 100);
      return `
        <div class="bar-item">
          <span>${escapeHtml(display(item.key, "None"))}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
          <strong>${Number(item.count || 0)}</strong>
        </div>
      `;
    })
    .join("");
}

function countItemsFromObject(data, labels) {
  return labels.map(([key, label]) => ({ key: label, count: Number(data[key] || 0) }));
}

function renderAnalyticsCards(data) {
  const cards = [
    ["Total leads", data.total_leads],
    ["Hot leads", data.hot_leads],
    ["Qualified leads", data.qualified_leads],
    ["Average score", data.average_lead_score],
    ["Conversations", data.total_conversations],
    ["Handovers", data.human_handover_count],
    ["Open tasks", data.open_tasks],
    ["Overdue tasks", data.overdue_tasks],
    ["No source answers", data.knowledge_no_source_count],
    ["Source-backed answers", data.answered_from_source_count],
  ];
  $("analyticsCards").innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="metric-card">
          <div class="metric-label">${escapeHtml(label)}</div>
          <div class="metric-value">${Number(value || 0)}</div>
        </article>
      `,
    )
    .join("");
}

async function loadDashboard() {
  const data = await apiGet("/dashboard/overview");
  renderMetricCards(data);
  $("latestConversations").innerHTML = data.latest_conversations?.length
    ? data.latest_conversations.map(renderConversationItem).join("")
    : listEmpty("No conversations yet.");
  $("latestTasks").innerHTML = data.latest_tasks?.length
    ? data.latest_tasks
        .map(
          (task) => `
            <article class="list-item">
              <div class="item-title">
                <span>${escapeHtml(task.title)}</span>
                <span>${escapeHtml(formatDate(task.due_date))}</span>
              </div>
              <div class="badge-row">${badge(task.status)}${badge(task.priority)}</div>
            </article>
          `,
        )
        .join("")
    : listEmpty("No tasks yet.");
  renderBarList("leadsByStage", data.leads_by_stage);
  renderBarList("leadsByPriority", data.leads_by_priority);
}

async function loadInbox() {
  const rows = await apiGet("/inbox", {
    limit: state.limit,
    q: $("inboxSearch").value.trim(),
    status: $("inboxStatus").value,
    human_handover: $("inboxHandover").value,
  });
  $("inboxList").innerHTML = rows.length ? rows.map(renderConversationItem).join("") : listEmpty("Inbox is empty.");
  $("inboxList").querySelectorAll("[data-conversation-id]").forEach((node) => {
    node.addEventListener("click", () => loadConversationDetail(node.dataset.conversationId));
  });
}

async function loadConversationDetail(conversationId) {
  const data = await apiGet(`/conversations/${conversationId}/detail`);
  const customer = data.customer || {};
  const lead = data.lead || {};
  $("conversationDetail").innerHTML = `
    <div class="detail-section">
      <h3>Customer</h3>
      <div class="field-grid">
        <div class="field"><span>Name</span><strong>${escapeHtml(display([customer.first_name, customer.last_name].filter(Boolean).join(" ")))}</strong></div>
        <div class="field"><span>Phone</span><strong>${escapeHtml(display(customer.phone))}</strong></div>
        <div class="field"><span>Email</span><strong>${escapeHtml(display(customer.email))}</strong></div>
        <div class="field"><span>Country</span><strong>${escapeHtml(display(customer.country))}</strong></div>
      </div>
    </div>
    <div class="detail-section">
      <h3>Lead</h3>
      <div class="badge-row">
        ${badge(lead.status)}
        ${badge(lead.priority)}
        ${lead.is_international_priority ? badge("international", "handover") : ""}
        ${lead.medical_track ? badge("medicine", "handover") : ""}
      </div>
      <div class="field-grid">
        <div class="field"><span>Program</span><strong>${escapeHtml(display(lead.program))}</strong></div>
        <div class="field"><span>Score</span><strong>${escapeHtml(display(lead.lead_score))}</strong></div>
      </div>
    </div>
    <div class="detail-section">
      <h3>Messages</h3>
      <div class="messages">
        ${
          data.messages?.length
            ? data.messages
                .map(
                  (message) => `
                    <div class="message">
                      <strong>${escapeHtml(message.sender_type)}</strong>
                      <div>${escapeHtml(message.text)}</div>
                      <div class="message-meta">${escapeHtml(formatDate(message.created_at))}</div>
                    </div>
                  `,
                )
                .join("")
            : listEmpty("No messages yet.")
        }
      </div>
    </div>
  `;
}

function renderLeadItem(lead) {
  return `
    <article class="list-item" data-lead-id="${escapeHtml(lead.lead_id)}">
      <div class="item-title">
        <span>${escapeHtml(lead.customer_name || "Unknown customer")}</span>
        <span>${escapeHtml(formatDate(lead.created_at))}</span>
      </div>
      <div class="item-meta">${escapeHtml(display(lead.program || lead.interest_area, "No program selected"))}</div>
      <div class="badge-row">
        ${badge(lead.status)}
        ${badge(lead.priority)}
        ${lead.source_domain ? badge(lead.source_domain) : ""}
        ${lead.medical_track ? badge("medicine", "handover") : ""}
      </div>
    </article>
  `;
}

async function loadLeads() {
  const rows = await apiGet("/leads", {
    limit: state.limit,
    q: $("leadSearch").value.trim(),
    status: $("leadStatus").value,
    priority: $("leadPriority").value,
    source_domain: $("leadDomain").value,
  });
  $("leadList").innerHTML = rows.length ? rows.map(renderLeadItem).join("") : listEmpty("No leads match the current filters.");
  $("leadList").querySelectorAll("[data-lead-id]").forEach((node) => {
    node.addEventListener("click", () => loadLeadDetail(node.dataset.leadId));
  });
}

async function loadLeadDetail(leadId) {
  const data = await apiGet(`/leads/${leadId}/detail`);
  const lead = data.lead || {};
  const customer = data.customer || {};
  $("leadDetail").innerHTML = `
    <div class="detail-section">
      <h3>${escapeHtml(display([customer.first_name, customer.last_name].filter(Boolean).join(" "), "Lead"))}</h3>
      <div class="badge-row">
        ${badge(lead.status)}
        ${badge(lead.priority)}
        ${badge(lead.qualification_status)}
        ${lead.handover_required ? badge("handover required", "handover") : ""}
      </div>
    </div>
    <div class="detail-section">
      <div class="field-grid">
        <div class="field"><span>Phone</span><strong>${escapeHtml(display(customer.phone))}</strong></div>
        <div class="field"><span>Email</span><strong>${escapeHtml(display(customer.email))}</strong></div>
        <div class="field"><span>Program</span><strong>${escapeHtml(display(lead.program))}</strong></div>
        <div class="field"><span>Lead score</span><strong>${escapeHtml(display(lead.lead_score))}</strong></div>
        <div class="field"><span>Intent</span><strong>${escapeHtml(display(lead.qualification_intent))}</strong></div>
        <div class="field"><span>Next action</span><strong>${escapeHtml(display(lead.recommended_next_action))}</strong></div>
      </div>
    </div>
    <div class="detail-section">
      <h3>Tasks</h3>
      ${renderTaskTable(data.tasks || [])}
    </div>
    <div class="detail-section">
      <h3>Stage history</h3>
      ${
        data.stage_history?.length
          ? data.stage_history
              .map((item) => `<div class="item-meta">${escapeHtml(formatDate(item.changed_at))} ${escapeHtml(display(item.from_stage_id))} -> ${escapeHtml(display(item.to_stage_id))}</div>`)
              .join("")
          : listEmpty("No stage movement yet.")
      }
    </div>
  `;
}

async function loadPipelines() {
  state.pipelines = await apiGet("/pipelines");
  $("pipelineSelect").innerHTML = `<option value="">Select pipeline</option>${state.pipelines
    .map((pipeline) => `<option value="${escapeHtml(pipeline.id)}">${escapeHtml(pipeline.name)}</option>`)
    .join("")}`;
  if (state.pipelines.length) {
    $("pipelineSelect").value = state.pipelines[0].id;
    await loadPipelineBoard();
  } else {
    $("pipelineBoard").innerHTML = listEmpty("No pipelines have been created yet.");
  }
}

async function loadPipelineBoard() {
  const pipelineId = $("pipelineSelect").value;
  if (!pipelineId) {
    $("pipelineBoard").innerHTML = listEmpty("Select a pipeline.");
    return;
  }
  const board = await apiGet(`/pipelines/${pipelineId}/board`, { leads_per_stage: state.limit });
  $("pipelineBoard").innerHTML = board.stages?.length
    ? board.stages
        .map(
          (stage) => `
            <section class="pipeline-stage">
              <header>
                <span>${escapeHtml(stage.name)}</span>
                <span>${Number(stage.lead_count || 0)}</span>
              </header>
              ${
                stage.leads?.length
                  ? stage.leads
                      .map(
                        (lead) => `
                          <article class="pipeline-lead">
                            <strong>${escapeHtml(lead.customer_name || "Unknown customer")}</strong>
                            <div class="item-meta">${escapeHtml(display(lead.program, "No program"))}</div>
                            <div class="badge-row">${badge(lead.priority)}</div>
                          </article>
                        `,
                      )
                      .join("")
                  : `<div class="list-empty">No leads.</div>`
              }
            </section>
          `,
        )
        .join("")
    : listEmpty("No stages in this pipeline.");
}

async function loadTasks() {
  const rows = await apiGet("/tasks", {
    limit: state.limit,
    status: $("taskStatus").value,
    priority: $("taskPriority").value,
    overdue: $("taskOverdue").value,
  });
  $("taskList").innerHTML = renderTaskTable(rows);
}

async function loadKnowledge() {
  const q = $("knowledgeSearch").value.trim();
  const language = $("knowledgeLanguage").value;
  const status = $("knowledgeStatus").value;
  const [sources, snippets] = await Promise.all([
    apiGet("/knowledge/sources", { q, language, status, limit: state.limit }),
    apiGet("/knowledge/snippets/search", { q, language, limit: state.limit }),
  ]);
  $("knowledgeSources").innerHTML = sources.length
    ? sources
        .map(
          (source) => `
            <article class="list-item">
              <div class="item-title">
                <span>${escapeHtml(source.title)}</span>
                <span>${escapeHtml(source.language)}</span>
              </div>
              <div class="item-meta">${escapeHtml(display(source.source_url, source.source_type))}</div>
              <div class="badge-row">${badge(source.status)}${badge(source.source_type)}</div>
            </article>
          `,
        )
        .join("")
    : listEmpty("No sources match the current filters.");
  $("knowledgeSnippets").innerHTML = snippets.length
    ? snippets
        .map(
          (item) => `
            <article class="list-item">
              <div class="item-title">
                <span>${escapeHtml(item.snippet.title)}</span>
                <span>${Number(item.score || 0)}</span>
              </div>
              <div class="item-meta">${escapeHtml(item.snippet.content)}</div>
              <div class="badge-row">${badge(item.source_status)}${badge(item.snippet.category)}${item.snippet.program_name ? badge(item.snippet.program_name) : ""}</div>
            </article>
          `,
        )
        .join("")
    : listEmpty("No snippets match the current filters.");
}

async function loadAnalytics() {
  const [overview, leads, sla, knowledge, ai] = await Promise.all([
    apiGet("/analytics/overview"),
    apiGet("/analytics/leads"),
    apiGet("/analytics/sla"),
    apiGet("/analytics/knowledge"),
    apiGet("/analytics/ai"),
  ]);
  renderAnalyticsCards(overview);
  renderBarList("analyticsLeadGroups", [
    ...leads.leads_by_status.map((item) => ({ key: `Status: ${display(item.key, "None")}`, count: item.count })),
    ...leads.leads_by_priority.map((item) => ({ key: `Priority: ${display(item.key, "None")}`, count: item.count })),
    ...leads.leads_by_source_domain.map((item) => ({ key: display(item.key, "No domain"), count: item.count })),
    { key: "International priority", count: leads.international_priority_count },
    { key: "Medicine track", count: leads.medical_track_count },
  ]);
  renderBarList(
    "analyticsSlaGroups",
    countItemsFromObject(sla, [
      ["open_tasks", "Open tasks"],
      ["overdue_tasks", "Overdue tasks"],
      ["due_today_tasks", "Due today"],
      ["urgent_open_tasks", "Urgent open"],
      ["open_handover_conversations", "Open handovers"],
    ]),
  );
  renderBarList("analyticsKnowledgeGroups", [
    { key: "Sources", count: knowledge.total_sources },
    { key: "Snippets", count: knowledge.total_snippets },
    { key: "Stale snippets", count: knowledge.stale_snippets },
    { key: "No approved source events", count: knowledge.no_approved_source_events },
    { key: "Source-backed events", count: knowledge.answered_from_source_events },
    ...knowledge.sources_by_status.map((item) => ({ key: `Source: ${display(item.key, "None")}`, count: item.count })),
  ]);
  renderBarList("analyticsAiGroups", [
    { key: "AI replies", count: ai.total_ai_messages },
    { key: "Average confidence x100", count: Math.round(Number(ai.average_confidence || 0) * 100) },
    { key: "Handover recommended", count: ai.handover_recommended_count },
    ...ai.intents.map((item) => ({ key: `Intent: ${display(item.key, "None")}`, count: item.count })),
    ...ai.answer_source_statuses.map((item) => ({ key: `Source: ${display(item.key, "None")}`, count: item.count })),
  ]);
}

async function loadActiveView() {
  setStatus("Loading...");
  try {
    if (state.activeView === "dashboard") await loadDashboard();
    if (state.activeView === "inbox") await loadInbox();
    if (state.activeView === "leads") await loadLeads();
    if (state.activeView === "pipeline") await loadPipelines();
    if (state.activeView === "tasks") await loadTasks();
    if (state.activeView === "knowledge") await loadKnowledge();
    if (state.activeView === "analytics") await loadAnalytics();
    if (state.activeView === "settings") syncSettings();
    setStatus(`Updated ${new Date().toLocaleTimeString("ka-GE")}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function switchView(view) {
  state.activeView = view;
  document.querySelectorAll(".nav-item").forEach((node) => node.classList.toggle("active", node.dataset.view === view));
  document.querySelectorAll(".view").forEach((node) => node.classList.toggle("active", node.id === `view-${view}`));
  $("viewTitle").textContent = titles[view][0];
  $("viewSubtitle").textContent = titles[view][1];
  loadActiveView();
}

function syncSettings() {
  $("settingsApiBase").value = state.apiBase;
  $("settingsLimit").value = state.limit;
  $("authStatus").textContent = state.token ? "Token stored for authenticated API calls." : "No token stored.";
}

async function loginOperator() {
  setStatus("Signing in...");
  try {
    const result = await apiPost("/auth/login", {
      email: $("loginEmail").value.trim(),
      password: $("loginPassword").value,
    });
    state.token = result.access_token;
    localStorage.setItem("alte_access_token", state.token);
    $("loginPassword").value = "";
    syncSettings();
    setStatus(`Signed in as ${result.user.email}`);
  } catch (error) {
    setStatus(error.message, true);
  }
}

function logoutOperator() {
  state.token = "";
  localStorage.removeItem("alte_access_token");
  syncSettings();
  setStatus("Stored token cleared.");
}

function bindFilters() {
  [
    "inboxSearch",
    "inboxStatus",
    "inboxHandover",
    "leadSearch",
    "leadStatus",
    "leadPriority",
    "leadDomain",
    "taskStatus",
    "taskPriority",
    "taskOverdue",
    "knowledgeSearch",
    "knowledgeLanguage",
    "knowledgeStatus",
  ].forEach((id) => {
    const node = $(id);
    if (node) node.addEventListener("input", () => loadActiveView());
  });
  $("pipelineSelect").addEventListener("change", loadPipelineBoard);
}

function init() {
  $("apiBase").value = state.apiBase;
  $("settingsApiBase").value = state.apiBase;
  $("settingsLimit").value = state.limit;

  document.querySelectorAll(".nav-item").forEach((node) => {
    node.addEventListener("click", () => switchView(node.dataset.view));
  });
  $("refreshBtn").addEventListener("click", () => {
    state.apiBase = $("apiBase").value.trim().replace(/\/$/, "");
    localStorage.setItem("alte_api_base", state.apiBase);
    loadActiveView();
  });
  $("settingsApiBase").addEventListener("change", () => {
    state.apiBase = $("settingsApiBase").value.trim().replace(/\/$/, "");
    $("apiBase").value = state.apiBase;
    localStorage.setItem("alte_api_base", state.apiBase);
  });
  $("settingsLimit").addEventListener("change", () => {
    state.limit = Math.max(5, Math.min(100, Number($("settingsLimit").value || 20)));
    localStorage.setItem("alte_operator_limit", String(state.limit));
  });
  $("loginBtn").addEventListener("click", loginOperator);
  $("logoutBtn").addEventListener("click", logoutOperator);
  bindFilters();
  loadActiveView();
}

init();
