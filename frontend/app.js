const state = {
  apiBase: localStorage.getItem("alte_api_base") || "http://127.0.0.1:8000",
  token: localStorage.getItem("alte_access_token") || "",
  limit: Number(localStorage.getItem("alte_operator_limit") || 20),
  activeView: localStorage.getItem("alte_active_view") || "dashboard",
  pipelines: [],
  refreshTimer: null,
};

const titles = {
  dashboard: ["Dashboard", "CRM backend-ის ცოცხალი overview ოპერატორისთვის."],
  inbox: ["შეტყობინებები", "Website chat-ის საუბრები და handover რიგი."],
  leads: ["ლიდები", "ადმისიების ლიდები, კვალიფიკაცია და წყაროების ფილტრები."],
  pipeline: ["Pipeline", "Stage-ბაზირებული ადმისიების board."],
  tasks: ["დავალებები", "Follow-up დავალებები და ვადაგასული სამუშაო."],
  knowledge: ["ცოდნის ბაზა", "დამტკიცებული წყაროები და snippet-ების მართვა."],
  analytics: ["ანალიტიკა", "ადმისიების performance, SLA, Knowledge coverage და AI ხარისხი."],
  settings: ["პარამეტრები", "ლოკალური workspace-ის პარამეტრები."],
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

function cssEscape(value) {
  return globalThis.CSS?.escape ? globalThis.CSS.escape(String(value)) : String(value).replace(/"/g, '\\"');
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

async function apiPatch(path, payload = {}) {
  const url = new URL(path, state.apiBase);
  const headers = { "Content-Type": "application/json" };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(url, {
    method: "PATCH",
    headers,
    body: JSON.stringify(payload),
  });
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
    ["კლიენტები", data.total_customers],
    ["ლიდები", data.total_leads],
    ["აქტიური ლიდები", data.open_leads],
    ["ჩარიცხულები", data.won_leads],
    ["დაკარგულები", data.lost_leads],
    ["საუბრები", data.total_conversations],
    ["Handover-ები", data.human_handover_count],
    ["ღია დავალებები", data.open_tasks],
    ["ვადაგასული", data.overdue_tasks],
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

function renderTaskTable(tasks, withComplete = false) {
  if (!tasks.length) return listEmpty("დავალებები არ არის.");
  return `
    <table>
      <thead>
        <tr>
          <th>სათაური</th>
          <th>სტატუსი</th>
          <th>პრიორიტეტი</th>
          <th>კლიენტი</th>
          <th>ვადა</th>
          ${withComplete ? "<th></th>" : ""}
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
                ${withComplete && task.status !== "completed" ? `<td><button class="complete-task-btn secondary-action" data-task-id="${escapeHtml(task.task_id || task.id)}" type="button">✓</button></td>` : withComplete ? "<td></td>" : ""}
              </tr>
            `,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

async function completeTask(taskId) {
  await apiPatch(`/tasks/${taskId}/complete`, {});
  setStatus("დავალება დასრულდა.");
  await loadActiveView();
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
  const [data, deadlines] = await Promise.all([
    apiGet("/dashboard/overview"),
    apiGet("/deadlines").catch(() => []),
  ]);
  renderMetricCards(data);
  $("latestConversations").innerHTML = data.latest_conversations?.length
    ? data.latest_conversations.map(renderConversationItem).join("")
    : listEmpty("საუბრები ჯერ არ არის.");
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
    : listEmpty("დავალებები ჯერ არ არის.");
  renderBarList("leadsByStage", data.leads_by_stage);
  renderBarList("leadsByPriority", data.leads_by_priority);
  const deadlineEl = $("dashboardDeadlines");
  if (deadlineEl) {
    deadlineEl.innerHTML = deadlines.length
      ? deadlines.slice(0, 8).map((d) => `
          <article class="list-item">
            <div class="item-title">
              <span>${escapeHtml(d.title)}</span>
              <span>${escapeHtml(formatDate(d.deadline_date))}</span>
            </div>
            <div class="item-meta">${escapeHtml(display(d.program, d.deadline_type))}</div>
            <div class="badge-row">${badge(d.deadline_type)}${d.is_active ? badge("active", "approved") : badge("inactive")}</div>
          </article>
        `).join("")
      : listEmpty("ვადები არ არის.");
  }
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

async function sendOperatorReply(conversationId) {
  const textarea = document.getElementById(`reply-${conversationId}`);
  const text = textarea?.value?.trim();
  if (!text) return;
  await apiPost(`/conversations/${conversationId}/messages`, { sender_type: "operator", text });
  await loadConversationDetail(conversationId);
  setStatus("პასუხი გაიგზავნა.");
}

async function createKnowledgeCandidateFromReply(messageId, conversationId) {
  const data = await apiPost(`/knowledge/operator-reply-candidates/${messageId}`, {
    created_by: "operator-ui",
  });
  setStatus(data.created ? "Knowledge candidate created for review." : "Knowledge candidate already exists.");
  await loadConversationDetail(conversationId);
}

async function findKnowledgeCandidateForReply(messageId) {
  const rows = await apiGet("/knowledge/sources", {
    source_key: `operator_reply:${messageId}`,
    limit: 1,
  });
  return rows[0] || null;
}

function openKnowledgeCandidateReview(sourceTitle = "") {
  switchView("knowledge");
  setTimeout(() => {
    $("knowledgeStatus").value = "";
    $("knowledgeSearch").value = sourceTitle || "Operator answer candidate";
    loadKnowledge().catch((error) => setStatus(error.message, true));
  }, 0);
}

function showOperatorAnswerDrafts() {
  switchView("knowledge");
  setTimeout(() => {
    $("knowledgeStatus").value = "draft";
    $("knowledgeSearch").value = "Operator answer candidate";
    loadKnowledge().catch((error) => setStatus(error.message, true));
  }, 0);
}

async function loadKnowledgeCandidateStatuses() {
  const rows = Array.from($("conversationDetail").querySelectorAll("[data-knowledge-status-message-id]"));
  await Promise.all(
    rows.map(async (node) => {
      const messageId = node.dataset.knowledgeStatusMessageId;
      const candidate = await findKnowledgeCandidateForReply(messageId);
      const action = $("conversationDetail").querySelector(`[data-open-knowledge-message-id="${cssEscape(messageId)}"]`);
      if (!candidate) {
        node.textContent = "No candidate yet";
        node.className = "candidate-status missing";
        if (action) action.style.display = "none";
        return;
      }
      node.textContent = `Candidate: ${candidate.status}${candidate.review_required ? " / review" : ""}`;
      node.className = `candidate-status ${candidate.status}`;
      if (action) {
        action.style.display = "inline-flex";
        action.dataset.sourceTitle = candidate.title || "";
      }
    }),
  );
}

function renderMessageActions(msg) {
  if (msg.sender_type !== "operator") return "";
  return `
    <div class="message-actions">
      <button class="secondary-action knowledge-candidate-btn" data-message-id="${escapeHtml(msg.id)}" type="button">
        Create knowledge candidate
      </button>
      <button class="secondary-action open-knowledge-candidate-btn" data-open-knowledge-message-id="${escapeHtml(msg.id)}" type="button" style="display:none">
        Open review
      </button>
      <span class="candidate-status loading" data-knowledge-status-message-id="${escapeHtml(msg.id)}">Checking candidate...</span>
    </div>
  `;
}

async function loadConversationDetail(conversationId) {
  const data = await apiGet(`/conversations/${conversationId}/detail`);
  const customer = data.customer || {};
  const lead = data.lead || {};
  $("conversationDetail").innerHTML = `
    <div class="detail-section">
      <h3>კლიენტი</h3>
      <div class="field-grid">
        <div class="field"><span>სახელი</span><strong>${escapeHtml(display([customer.first_name, customer.last_name].filter(Boolean).join(" ")))}</strong></div>
        <div class="field"><span>ტელეფონი</span><strong>${escapeHtml(display(customer.phone))}</strong></div>
        <div class="field"><span>ელ-ფოსტა</span><strong>${escapeHtml(display(customer.email))}</strong></div>
        <div class="field"><span>ქვეყანა</span><strong>${escapeHtml(display(customer.country))}</strong></div>
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
        <div class="field"><span>პროგრამა</span><strong>${escapeHtml(display(lead.program))}</strong></div>
        <div class="field"><span>Score</span><strong>${escapeHtml(display(lead.lead_score))}</strong></div>
      </div>
    </div>
    <div class="detail-section">
      <h3>შეტყობინებები</h3>
      <div class="messages">
        ${
          data.messages?.length
            ? data.messages
                .map(
                  (msg) => `
                    <div class="message ${msg.sender_type === "operator" ? "msg-operator" : msg.sender_type === "user" ? "msg-user" : "msg-ai"}">
                      <strong>${msg.sender_type === "user" ? "👤 სტუდენტი" : msg.sender_type === "operator" ? "🎧 ოპერატორი" : "🤖 AI"}</strong>
                      <div>${escapeHtml(msg.text)}</div>
                      <div class="message-meta">${escapeHtml(formatDate(msg.created_at))}</div>
                      ${renderMessageActions(msg)}
                    </div>
                  `,
                )
                .join("")
            : listEmpty("შეტყობინებები არ არის.")
        }
      </div>
    </div>
    <div class="detail-section">
      <h3>პასუხის გაგზავნა</h3>
      <div class="reply-box">
        <textarea id="reply-${escapeHtml(conversationId)}" class="reply-textarea" placeholder="შეიყვანეთ პასუხი..." rows="3"></textarea>
        <button class="primary-action" id="replyBtn" type="button">გაგზავნა</button>
      </div>
    </div>
  `;
  $("replyBtn").addEventListener("click", () => sendOperatorReply(conversationId));
  $("conversationDetail").querySelectorAll(".knowledge-candidate-btn").forEach((button) => {
    button.addEventListener("click", () => createKnowledgeCandidateFromReply(button.dataset.messageId, conversationId));
  });
  $("conversationDetail").querySelectorAll(".open-knowledge-candidate-btn").forEach((button) => {
    button.addEventListener("click", () => openKnowledgeCandidateReview(button.dataset.sourceTitle || ""));
  });
  loadKnowledgeCandidateStatuses().catch((error) => setStatus(error.message, true));
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

async function changeLeadStage(leadId, stageId) {
  await apiPatch(`/leads/${leadId}/stage`, { stage_id: stageId });
  await loadLeadDetail(leadId);
  setStatus("Stage განახლდა.");
}

async function loadLeadDetail(leadId) {
  const [data, allStages] = await Promise.all([
    apiGet(`/leads/${leadId}/detail`),
    apiGet("/pipeline-stages"),
  ]);
  const lead = data.lead || {};
  const customer = data.customer || {};
  const stageOptions = allStages
    .map((s) => `<option value="${escapeHtml(s.id)}" ${s.id === lead.stage_id ? "selected" : ""}>${escapeHtml(s.name)}</option>`)
    .join("");
  $("leadDetail").innerHTML = `
    <div class="detail-section">
      <h3>${escapeHtml(display([customer.first_name, customer.last_name].filter(Boolean).join(" "), "Lead"))}</h3>
      <div class="badge-row">
        ${badge(lead.status)}
        ${badge(lead.priority)}
        ${badge(lead.qualification_status)}
        ${lead.handover_required ? badge("handover required", "handover") : ""}
        ${lead.is_international_priority ? badge("international", "handover") : ""}
        ${lead.medical_track ? badge("medicine", "handover") : ""}
      </div>
    </div>
    <div class="detail-section">
      <div class="field-grid">
        <div class="field"><span>ტელეფონი</span><strong>${escapeHtml(display(customer.phone))}</strong></div>
        <div class="field"><span>ელ-ფოსტა</span><strong>${escapeHtml(display(customer.email))}</strong></div>
        <div class="field"><span>პროგრამა</span><strong>${escapeHtml(display(lead.program))}</strong></div>
        <div class="field"><span>Lead score</span><strong>${escapeHtml(display(lead.lead_score))}</strong></div>
        <div class="field"><span>Intent</span><strong>${escapeHtml(display(lead.qualification_intent))}</strong></div>
        <div class="field"><span>შემდეგი ნაბიჯი</span><strong>${escapeHtml(display(lead.recommended_next_action))}</strong></div>
      </div>
    </div>
    <div class="detail-section">
      <h3>სტატუსი და Stage</h3>
      <div class="action-row" style="margin-bottom:8px">
        <select id="leadStatusSelect">
          <option value="new" ${lead.status === "new" ? "selected" : ""}>New</option>
          <option value="open" ${lead.status === "open" ? "selected" : ""}>Open</option>
          <option value="in_progress" ${lead.status === "in_progress" ? "selected" : ""}>In progress</option>
          <option value="won" ${lead.status === "won" ? "selected" : ""}>Won</option>
          <option value="lost" ${lead.status === "lost" ? "selected" : ""}>Lost</option>
        </select>
        <button class="primary-action" id="leadStatusBtn" type="button">სტ. შეცვლა</button>
      </div>
      <div class="action-row">
        <select id="stageSelect">${stageOptions}</select>
        <button class="primary-action" id="stageChangeBtn" type="button">Stage</button>
      </div>
    </div>
    <div class="detail-section">
      <div class="action-row" style="justify-content:space-between">
        <h3 style="margin:0">დავალებები</h3>
        <button class="secondary-action" id="addTaskToLeadBtn" data-lead-id="${escapeHtml(leadId)}" type="button">+ დავალება</button>
      </div>
      ${renderTaskTable(data.tasks || [], true)}
    </div>
    <div class="detail-section">
      <h3>Stage-ის ისტორია</h3>
      ${
        data.stage_history?.length
          ? data.stage_history
              .map((item) => `<div class="item-meta">${escapeHtml(formatDate(item.changed_at))} — ${escapeHtml(display(item.stage_name || item.to_stage_id, "?"))}</div>`)
              .join("")
          : listEmpty("Stage-ის ცვლილება ჯერ არ მომხდარა.")
      }
    </div>
  `;
  $("leadStatusBtn").addEventListener("click", () => changeLeadStatus(leadId, $("leadStatusSelect").value));
  $("stageChangeBtn").addEventListener("click", () => changeLeadStage(leadId, $("stageSelect").value));
  $("addTaskToLeadBtn").addEventListener("click", () => openTaskModal(leadId));
  $("leadDetail").querySelectorAll(".complete-task-btn").forEach((btn) => {
    btn.addEventListener("click", () => completeTask(btn.dataset.taskId));
  });
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
  if (!pipelineId) { $("pipelineBoard").innerHTML = listEmpty("Pipeline-ი აირჩიეთ."); return; }
  const board = await apiGet(`/pipelines/${pipelineId}/board`, { leads_per_stage: state.limit });
  $("pipelineBoard").innerHTML = board.stages?.length
    ? board.stages.map((stage) => `
        <section class="pipeline-stage">
          <header>
            <span>${escapeHtml(stage.name)}</span>
            <span class="stage-count">${Number(stage.lead_count || 0)}</span>
          </header>
          ${stage.leads?.length
            ? stage.leads.map((lead) => `
                <article class="pipeline-lead" data-lead-id="${escapeHtml(lead.lead_id)}" style="cursor:pointer">
                  <strong>${escapeHtml(lead.customer_name || "უცნობი კლიენტი")}</strong>
                  <div class="item-meta">${escapeHtml(display(lead.program, "პროგრამა მითითებული არ არის"))}</div>
                  <div class="badge-row">${badge(lead.priority)}${lead.is_international_priority ? badge("intl","handover") : ""}${lead.medical_track ? badge("medicine","handover") : ""}</div>
                </article>
              `).join("")
            : `<div class="list-empty">ლიდები არ არის.</div>`}
        </section>
      `).join("")
    : listEmpty("Pipeline-ში stage-ები არ არის.");
  $("pipelineBoard").querySelectorAll("[data-lead-id]").forEach((card) => {
    card.addEventListener("click", () => {
      switchView("leads");
      setTimeout(() => openLeadFromPipeline(card.dataset.leadId), 300);
    });
  });
}

async function openLeadFromPipeline(leadId) {
  const rows = await apiGet("/leads", { limit: 100 });
  const match = rows.find((r) => r.lead_id === leadId);
  if (match) {
    $("leadList").innerHTML = rows.map(renderLeadItem).join("");
    $("leadList").querySelectorAll("[data-lead-id]").forEach((node) => {
      node.addEventListener("click", () => loadLeadDetail(node.dataset.leadId));
    });
  }
  await loadLeadDetail(leadId);
}

async function loadTasks() {
  const rows = await apiGet("/tasks", {
    limit: state.limit,
    status: $("taskStatus").value,
    priority: $("taskPriority").value,
    overdue: $("taskOverdue").value,
  });
  $("taskList").innerHTML = renderTaskTable(rows, true);
  $("taskList").querySelectorAll(".complete-task-btn").forEach((btn) => {
    btn.addEventListener("click", () => completeTask(btn.dataset.taskId));
  });
}

async function toggleSource(sourceId, activate) {
  const field = activate ? "status" : "status";
  await apiPatch(`/knowledge/sources/${sourceId}`, { status: activate ? "approved" : "archived" });
  setStatus(activate ? "წყარო გააქტიურდა." : "წყარო დეაქტიურდა.");
  await loadKnowledge();
}

async function approveKnowledgeSnippet(snippetId) {
  await apiPatch(`/knowledge/snippets/${snippetId}/approve`, {});
  setStatus("Knowledge candidate approved.");
  await loadKnowledge();
}

async function archiveKnowledgeSnippet(snippetId) {
  await apiPatch(`/knowledge/snippets/${snippetId}/archive`, {});
  setStatus("Knowledge candidate archived.");
  await loadKnowledge();
}

async function saveKnowledgeSnippetDraft(snippetId, sourceId) {
  const editor = document.getElementById(`snippet-edit-${snippetId}`);
  const category = document.getElementById(`snippet-category-${snippetId}`)?.value?.trim() || "operator_answer";
  const sensitivity = document.getElementById(`snippet-sensitivity-${snippetId}`)?.value || "medium";
  const language = document.getElementById(`snippet-language-${snippetId}`)?.value || "ka";
  const content = editor?.value?.trim();
  if (!content) {
    setStatus("Knowledge candidate content is required before saving.", true);
    return;
  }
  await apiPatch(`/knowledge/sources/${sourceId}`, {
    category,
    sensitivity,
    language,
    review_required: true,
    status: "draft",
  });
  await apiPatch(`/knowledge/snippets/${snippetId}`, {
    content,
    category,
    sensitivity,
    language,
    review_required: true,
    status: "draft",
  });
  setStatus("Knowledge candidate draft saved.");
  await loadKnowledge();
}

function renderKnowledgeReviewItem(item) {
  return `
    <article class="list-item knowledge-review-item">
      <div class="item-title">
        <span>${escapeHtml(item.snippet.title)}</span>
        <span>${escapeHtml(item.snippet.language || item.source.language || "")}</span>
      </div>
      <div class="item-meta">${escapeHtml((item.snippet.content || "").slice(0, 260))}</div>
      <textarea id="snippet-edit-${escapeHtml(item.snippet.id)}" class="knowledge-edit-textarea" rows="6">${escapeHtml(item.snippet.content || "")}</textarea>
      <div class="knowledge-meta-grid">
        <label>
          Category
          <input id="snippet-category-${escapeHtml(item.snippet.id)}" type="text" value="${escapeHtml(item.snippet.category || item.source.category || "operator_answer")}" />
        </label>
        <label>
          Sensitivity
          <select id="snippet-sensitivity-${escapeHtml(item.snippet.id)}">
            ${["low", "medium", "high"].map((value) => `<option value="${value}" ${value === (item.snippet.sensitivity || item.source.sensitivity || "medium") ? "selected" : ""}>${value}</option>`).join("")}
          </select>
        </label>
        <label>
          Language
          <select id="snippet-language-${escapeHtml(item.snippet.id)}">
            ${["ka", "en"].map((value) => `<option value="${value}" ${value === (item.snippet.language || item.source.language || "ka") ? "selected" : ""}>${value}</option>`).join("")}
          </select>
        </label>
      </div>
      <div class="badge-row">
        ${badge(item.snippet.status)}
        ${badge(item.source.source_type)}
        ${badge(item.snippet.category)}
        ${item.reasons?.map((reason) => badge(reason, "handover")).join("") || ""}
      </div>
      <div class="action-row" style="margin-top:8px">
        <button class="secondary-action save-snippet-draft-btn" data-snippet-id="${escapeHtml(item.snippet.id)}" data-source-id="${escapeHtml(item.source.id)}" type="button">
          Save draft
        </button>
        <button class="primary-action approve-snippet-btn" data-snippet-id="${escapeHtml(item.snippet.id)}" type="button">
          Approve
        </button>
        <button class="secondary-action archive-snippet-btn" data-snippet-id="${escapeHtml(item.snippet.id)}" type="button">
          Archive
        </button>
      </div>
    </article>
  `;
}

async function loadKnowledge() {
  const q = $("knowledgeSearch").value.trim();
  const language = $("knowledgeLanguage").value;
  const status = $("knowledgeStatus").value;
  const operatorDraftMode = q.toLowerCase().includes("operator answer candidate") && status === "draft";
  const sourceParams = { q, language, status, limit: state.limit };
  if (operatorDraftMode) {
    sourceParams.source_type = "faq";
  }
  const [sources, snippets] = await Promise.all([
    apiGet("/knowledge/sources", sourceParams),
    q ? apiGet("/knowledge/snippets/search", { q, language, limit: state.limit }) : Promise.resolve([]),
  ]);
  const reviewItems = operatorDraftMode
    ? (await apiGet("/knowledge/review-queue", { status: "draft", review_required: true, limit: state.limit }))
        .filter((item) => (item.source.source_key || "").startsWith("operator_reply:"))
    : [];
  $("knowledgeSources").innerHTML = sources.length
    ? sources.map((src) => `
        <article class="list-item">
          <div class="item-title">
            <span>${escapeHtml(src.title)}</span>
            <span>${escapeHtml(src.language || "")}</span>
          </div>
          <div class="item-meta">${escapeHtml(display(src.source_url, src.source_type))}</div>
          <div class="badge-row">
            ${badge(src.status)}${badge(src.source_type)}
            ${src.review_required ? badge("review", "handover") : ""}
          </div>
          <div class="action-row" style="margin-top:8px">
            ${src.status !== "approved"
              ? `<button class="source-activate secondary-action" data-source-id="${escapeHtml(src.id)}" type="button">✓ გააქტიუ.</button>`
              : `<button class="source-deactivate secondary-action" data-source-id="${escapeHtml(src.id)}" type="button">✗ დეაქტ.</button>`}
          </div>
        </article>
      `).join("")
    : listEmpty("წყაროები ვერ მოიძებნა.");
  $("knowledgeSources").querySelectorAll(".source-activate").forEach((btn) => {
    btn.addEventListener("click", () => toggleSource(btn.dataset.sourceId, true));
  });
  $("knowledgeSources").querySelectorAll(".source-deactivate").forEach((btn) => {
    btn.addEventListener("click", () => toggleSource(btn.dataset.sourceId, false));
  });
  const snippetHtml = snippets.length
    ? snippets.map((item) => `
        <article class="list-item">
          <div class="item-title">
            <span>${escapeHtml(item.snippet.title)}</span>
            <span class="badge">${Number(item.score || 0)}</span>
          </div>
          <div class="item-meta">${escapeHtml((item.snippet.content || "").slice(0, 180))}</div>
          <div class="badge-row">${badge(item.source_status)}${badge(item.snippet.category)}${item.snippet.program_name ? badge(item.snippet.program_name) : ""}</div>
        </article>
      `).join("")
    : listEmpty("მოსაძებნად ჩაწერეთ საძიებო სიტყვა.");
  $("knowledgeSnippets").innerHTML = operatorDraftMode
    ? reviewItems.length
      ? reviewItems.map(renderKnowledgeReviewItem).join("")
      : listEmpty("No operator answer draft candidates found.")
    : snippetHtml;
  $("knowledgeSnippets").querySelectorAll(".approve-snippet-btn").forEach((btn) => {
    btn.addEventListener("click", () => approveKnowledgeSnippet(btn.dataset.snippetId));
  });
  $("knowledgeSnippets").querySelectorAll(".save-snippet-draft-btn").forEach((btn) => {
    btn.addEventListener("click", () => saveKnowledgeSnippetDraft(btn.dataset.snippetId, btn.dataset.sourceId));
  });
  $("knowledgeSnippets").querySelectorAll(".archive-snippet-btn").forEach((btn) => {
    btn.addEventListener("click", () => archiveKnowledgeSnippet(btn.dataset.snippetId));
  });
  if (operatorDraftMode && !sources.length) {
    setStatus("No operator answer draft candidates found.");
  }
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

async function updateSidebarBadges() {
  try {
    const sla = await apiGet("/analytics/sla");
    const overdue = Number(sla.overdue_tasks || 0);
    const handovers = Number(sla.open_handover_conversations || 0);
    const taskBadge = document.querySelector('[data-view="tasks"] .nav-badge');
    const inboxBadge = document.querySelector('[data-view="inbox"] .nav-badge');
    if (taskBadge) { taskBadge.textContent = overdue > 0 ? overdue : ""; taskBadge.style.display = overdue > 0 ? "inline-flex" : "none"; }
    if (inboxBadge) { inboxBadge.textContent = handovers > 0 ? handovers : ""; inboxBadge.style.display = handovers > 0 ? "inline-flex" : "none"; }
  } catch (_) {}
}

function startAutoRefresh() {
  if (state.refreshTimer) clearInterval(state.refreshTimer);
  state.refreshTimer = setInterval(() => {
    if (state.activeView === "dashboard") loadDashboard().catch(() => {});
    updateSidebarBadges().catch(() => {});
  }, 15000);
}

function switchView(view) {
  state.activeView = view;
  localStorage.setItem("alte_active_view", view);
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

async function changeLeadStatus(leadId, status) {
  await apiPatch(`/leads/${leadId}`, { status });
  setStatus("სტატუსი განახლდა.");
  await loadLeadDetail(leadId);
}

let _taskModalLeadId = null;

function openTaskModal(leadId = null) {
  _taskModalLeadId = leadId;
  ["mTaskTitle", "mTaskDesc"].forEach((id) => { const el = $(id); if (el) el.value = ""; });
  $("mTaskPriority").value = "normal";
  $("mTaskDue").value = "";
  $("taskModalStatus").textContent = "";
  $("taskModal").style.display = "flex";
  $("mTaskTitle").focus();
}

function closeTaskModal() {
  $("taskModal").style.display = "none";
  _taskModalLeadId = null;
}

async function saveNewTask() {
  const title = $("mTaskTitle").value.trim();
  if (!title) { $("taskModalStatus").textContent = "სათაური სავალდებულოა."; return; }
  $("taskModalSave").disabled = true;
  $("taskModalStatus").textContent = "შენახვა...";
  try {
    const due = $("mTaskDue").value;
    await apiPost("/tasks", {
      title,
      priority: $("mTaskPriority").value,
      due_date: due ? new Date(due).toISOString() : undefined,
      description: $("mTaskDesc").value.trim() || undefined,
      lead_id: _taskModalLeadId || undefined,
    });
    closeTaskModal();
    setStatus("დავალება შეიქმნა.");
    if (_taskModalLeadId) {
      await loadLeadDetail(_taskModalLeadId);
    } else {
      await loadActiveView();
    }
  } catch (error) {
    $("taskModalStatus").textContent = error.message;
  } finally {
    $("taskModalSave").disabled = false;
  }
}

function openLeadModal() {
  ["mLeadName","mLeadPhone","mLeadEmail","mLeadProgram","mLeadSource","mLeadNotes"].forEach((id) => { const el = $(id); if (el) el.value = ""; });
  $("mLeadPriority").value = "normal";
  $("leadModalStatus").textContent = "";
  $("leadModal").style.display = "flex";
  $("mLeadName").focus();
}

function closeLeadModal() {
  $("leadModal").style.display = "none";
}

async function saveNewLead() {
  const name = $("mLeadName").value.trim();
  if (!name) { $("leadModalStatus").textContent = "სახელი სავალდებულოა."; return; }
  $("leadModalSave").disabled = true;
  $("leadModalStatus").textContent = "შენახვა...";
  try {
    const parts = name.split(" ");
    const customer = await apiPost("/customers", {
      first_name: parts[0] || "",
      last_name: parts.slice(1).join(" ") || undefined,
      phone: $("mLeadPhone").value.trim() || undefined,
      email: $("mLeadEmail").value.trim() || undefined,
    });
    await apiPost("/leads", {
      customer_id: customer.id,
      program: $("mLeadProgram").value.trim() || undefined,
      priority: $("mLeadPriority").value,
      source_channel: $("mLeadSource").value.trim() || undefined,
    });
    closeLeadModal();
    setStatus("ახალი ლიდი შეიქმნა.");
    await loadLeads();
  } catch (error) {
    $("leadModalStatus").textContent = error.message;
  } finally {
    $("leadModalSave").disabled = false;
  }
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
    node.classList.toggle("active", node.dataset.view === state.activeView);
  });
  document.querySelectorAll(".view").forEach((node) => {
    node.classList.toggle("active", node.id === `view-${state.activeView}`);
  });
  const titleEntry = titles[state.activeView];
  if (titleEntry) { $("viewTitle").textContent = titleEntry[0]; $("viewSubtitle").textContent = titleEntry[1]; }
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
  $("operatorKnowledgeFilterBtn").addEventListener("click", showOperatorAnswerDrafts);
  $("newLeadBtn").addEventListener("click", openLeadModal);
  $("newTaskBtn").addEventListener("click", () => openTaskModal(null));
  $("taskModalClose").addEventListener("click", closeTaskModal);
  $("taskModalCancel").addEventListener("click", closeTaskModal);
  $("taskModalSave").addEventListener("click", saveNewTask);
  $("taskModal").addEventListener("click", (e) => { if (e.target === $("taskModal")) closeTaskModal(); });
  $("leadModalClose").addEventListener("click", closeLeadModal);
  $("leadModalCancel").addEventListener("click", closeLeadModal);
  $("leadModalSave").addEventListener("click", saveNewLead);
  $("leadModal").addEventListener("click", (e) => { if (e.target === $("leadModal")) closeLeadModal(); });
  bindFilters();
  loadActiveView();
  startAutoRefresh();
  updateSidebarBadges();
}

init();
