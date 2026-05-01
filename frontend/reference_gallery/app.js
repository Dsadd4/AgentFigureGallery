const state = {
  sessions: [],
  session: null,
  filter: "all",
  query: "",
  source: "all",
};

const el = {
  sessionSelect: document.getElementById("sessionSelect"),
  reloadSessions: document.getElementById("reloadSessions"),
  plotType: document.getElementById("plotType"),
  candidateLimit: document.getElementById("candidateLimit"),
  strategySelect: document.getElementById("strategySelect"),
  taskInput: document.getElementById("taskInput"),
  generateSession: document.getElementById("generateSession"),
  exportBundle: document.getElementById("exportBundle"),
  clearRejected: document.getElementById("clearRejected"),
  message: document.getElementById("message"),
  sessionTitle: document.getElementById("sessionTitle"),
  sessionMeta: document.getElementById("sessionMeta"),
  gallery: document.getElementById("gallery"),
  searchInput: document.getElementById("searchInput"),
  sourceFilter: document.getElementById("sourceFilter"),
  filters: document.querySelectorAll(".filter"),
  countAll: document.getElementById("countAll"),
  countCandidate: document.getElementById("countCandidate"),
  countLiked: document.getElementById("countLiked"),
  countGlobalLiked: document.getElementById("countGlobalLiked"),
  countSelected: document.getElementById("countSelected"),
  countRejected: document.getElementById("countRejected"),
};

function setMessage(text) {
  el.message.textContent = text || "";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok || payload.error) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }
  return payload;
}

function activeSessionValue() {
  return el.sessionSelect.value || (state.session && state.session.session_json) || "";
}

async function loadSessions(preferred) {
  const payload = await api("/api/sessions");
  state.sessions = payload.sessions || [];
  el.sessionSelect.innerHTML = "";
  for (const session of state.sessions) {
    const option = document.createElement("option");
    option.value = session.session_json;
    option.textContent = `${session.session_id} (${session.plot_type || "unknown"}, ${session.candidate_count})`;
    el.sessionSelect.appendChild(option);
  }
  if (preferred) {
    const match = state.sessions.find((session) => session.session_json === preferred || session.session_id === preferred);
    if (match) el.sessionSelect.value = match.session_json;
  }
  if (!el.sessionSelect.value && state.sessions[0]) {
    el.sessionSelect.value = state.sessions[0].session_json;
  }
  if (el.sessionSelect.value) {
    await loadSession(el.sessionSelect.value);
  }
}

async function loadSession(sessionPath) {
  state.session = await api(`/api/session?session=${encodeURIComponent(sessionPath)}`);
  el.sessionSelect.value = state.session.session_json;
  const resolved = state.session.resolved || {};
  const globalCounts = state.session.global_status_counts || {};
  el.sessionTitle.textContent = `${state.session.session_id || "Reference session"}`;
  el.sessionMeta.textContent = `${resolved.plot_type || "unknown"} | ${state.session.candidates.length} candidates | global liked ${globalCounts.global_liked || 0}, global rejected ${globalCounts.global_rejected || 0} | ${state.session.session_json}`;
  populateSourceFilter();
  render();
}

function populateSourceFilter() {
  const current = el.sourceFilter.value || "all";
  const sources = new Set();
  for (const candidate of state.session.candidates || []) {
    if (candidate.source_repo) sources.add(candidate.source_repo);
  }
  el.sourceFilter.innerHTML = '<option value="all">All sources</option>';
  for (const source of Array.from(sources).sort()) {
    const option = document.createElement("option");
    option.value = source;
    option.textContent = source;
    el.sourceFilter.appendChild(option);
  }
  el.sourceFilter.value = Array.from(sources).includes(current) ? current : "all";
  state.source = el.sourceFilter.value;
}

function statusCounts() {
  const candidates = state.session ? state.session.candidates : [];
  const isTypeLiked = (item) => item.status === "liked" || item.status === "selected";
  const isRejected = (item) => item.status === "rejected" || item.global_status === "global_rejected";
  return {
    all: candidates.length,
    candidate: candidates.filter((item) => item.status === "candidate" && item.global_status !== "global_rejected").length,
    liked: candidates.filter(isTypeLiked).length,
    selected: candidates.filter((item) => item.status === "selected").length,
    rejected: candidates.filter(isRejected).length,
    globalLiked: candidates.filter((item) => item.global_status === "global_liked").length,
    globalRejected: candidates.filter((item) => item.global_status === "global_rejected").length,
  };
}

function updateCounts() {
  const counts = statusCounts();
  el.countAll.textContent = counts.all;
  el.countCandidate.textContent = counts.candidate;
  el.countLiked.textContent = counts.liked;
  el.countGlobalLiked.textContent = counts.globalLiked;
  el.countSelected.textContent = counts.selected;
  el.countRejected.textContent = counts.rejected;
}

function candidateText(candidate) {
  return [
    candidate.candidate_id,
    candidate.stable_candidate_id,
    candidate.display_id,
    candidate.session_candidate_id,
    candidate.reference_candidate_id,
    candidate.source_repo,
    candidate.subtype,
    candidate.example_id,
    candidate.why_suggested,
    candidate.script_path,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function visibleCandidates() {
  if (!state.session) return [];
  const query = state.query.trim().toLowerCase();
  return state.session.candidates.filter((candidate) => {
    const typeLiked = candidate.status === "liked" || candidate.status === "selected";
    const globallyRejected = candidate.global_status === "global_rejected";
    if (state.filter === "all" && globallyRejected) return false;
    if (state.filter === "candidate" && (globallyRejected || candidate.status !== "candidate")) return false;
    if (state.filter === "liked" && (!typeLiked || globallyRejected)) return false;
    if (state.filter === "global_liked" && candidate.global_status !== "global_liked") return false;
    if (state.filter === "selected" && (candidate.status !== "selected" || globallyRejected)) return false;
    if (state.filter === "rejected" && candidate.status !== "rejected" && !globallyRejected) return false;
    if (state.source !== "all" && candidate.source_repo !== state.source) return false;
    if (query && !candidateText(candidate).includes(query)) return false;
    return true;
  });
}

function render() {
  updateCounts();
  for (const button of el.filters) {
    button.classList.toggle("active", button.dataset.filter === state.filter);
  }
  const candidates = visibleCandidates();
  el.gallery.innerHTML = "";
  if (!candidates.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No candidates match the current filters.";
    el.gallery.appendChild(empty);
    return;
  }
  const fragment = document.createDocumentFragment();
  for (const candidate of candidates) {
    fragment.appendChild(candidateCard(candidate));
  }
  el.gallery.appendChild(fragment);
}

function candidateCard(candidate) {
  const card = document.createElement("article");
  card.className = `candidate-card ${candidate.status} ${candidate.global_status || ""}`;
  const image = document.createElement("img");
  image.className = "candidate-image";
  image.loading = "lazy";
  image.alt = candidate.display_id || candidate.stable_candidate_id || candidate.candidate_id;
  image.src = candidate.preview_url || `/media?path=${encodeURIComponent(candidate.preview_path)}`;

  const body = document.createElement("div");
  body.className = "candidate-body";

  const head = document.createElement("div");
  head.className = "candidate-head";
  const id = document.createElement("div");
  id.className = "candidate-id";
  id.textContent = candidate.display_id || candidate.stable_candidate_id || candidate.candidate_id;
  if (candidate.session_candidate_id && candidate.session_candidate_id !== id.textContent) {
    const slot = document.createElement("span");
    slot.className = "session-slot";
    slot.textContent = candidate.session_candidate_id;
    id.appendChild(slot);
  }
  const status = document.createElement("span");
  status.className = `status ${candidate.status}`;
  status.textContent = candidate.global_status && candidate.global_status !== "none"
    ? `${candidate.status} · ${candidate.global_status.replace("global_", "global ")}`
    : candidate.status;
  head.append(id, status);

  const repo = document.createElement("div");
  repo.className = "repo";
  const refId = candidate.reference_candidate_id ? ` | ref ${candidate.reference_candidate_id}` : "";
  repo.textContent = `${candidate.source_repo || "unknown"}${candidate.quality_score ? ` | score ${candidate.quality_score}` : ""}${refId}`;

  const summary = document.createElement("div");
  summary.className = "summary";
  summary.textContent = candidate.why_suggested || candidate.source_output_path || candidate.script_path || "";

  const actions = document.createElement("div");
  actions.className = "actions";
  actions.append(
    actionButton("Like", "like", candidate),
    actionButton("Reject", "reject", candidate),
    actionButton("Select", "select", candidate),
    actionButton("Clear", "clear", candidate),
    actionButton("G Like", "global_like", candidate),
    actionButton("G Reject", "global_reject", candidate),
    actionButton("G Clear", "global_clear", candidate)
  );

  body.append(head, repo, summary, actions);
  card.append(image, body);
  return card;
}

function actionButton(label, action, candidate) {
  const button = document.createElement("button");
  button.textContent = label;
  button.className = action;
  if (
    (action === "like" && (candidate.status === "liked" || candidate.status === "selected")) ||
    (action === "reject" && candidate.status === "rejected") ||
    (action === "select" && candidate.status === "selected") ||
    (action === "global_like" && candidate.global_status === "global_liked") ||
    (action === "global_reject" && candidate.global_status === "global_rejected")
  ) {
    button.classList.add("active");
  }
  button.addEventListener("click", async () => {
    try {
      button.disabled = true;
      const candidateId = candidate.candidate_id || candidate.stable_candidate_id || candidate.display_id || candidate.session_candidate_id;
      state.session = await api("/api/preferences", {
        method: "POST",
        body: JSON.stringify({
          session: activeSessionValue(),
          candidate_id: candidateId,
          action,
          updated_at: new Date().toISOString(),
        }),
      });
      populateSourceFilter();
      render();
    } catch (error) {
      setMessage(error.message);
    } finally {
      button.disabled = false;
    }
  });
  return button;
}

el.reloadSessions.addEventListener("click", async () => {
  try {
    await loadSessions(activeSessionValue());
    setMessage("Sessions refreshed.");
  } catch (error) {
    setMessage(error.message);
  }
});

el.sessionSelect.addEventListener("change", async () => {
  try {
    await loadSession(el.sessionSelect.value);
  } catch (error) {
    setMessage(error.message);
  }
});

el.generateSession.addEventListener("click", async () => {
  try {
    setMessage("Generating session...");
    const plotType = el.plotType.value;
    const limit = Number(el.candidateLimit.value || 100);
    const strategy = el.strategySelect.value || "explore";
    const seed = Date.now();
    const sessionId = `gallery_${plotType}_${strategy}_${seed}`;
    const payload = await api("/api/generate", {
      method: "POST",
      body: JSON.stringify({
        plot_type: plotType,
        task: el.taskInput.value,
        limit,
        session_id: sessionId,
        strategy,
        seed,
      }),
    });
    await loadSessions(payload.session_id);
    setMessage(`Generated ${payload.session_id}.`);
  } catch (error) {
    setMessage(error.message);
  }
});

el.exportBundle.addEventListener("click", async () => {
  try {
    setMessage("Exporting bundle...");
    const payload = await api("/api/export", {
      method: "POST",
      body: JSON.stringify({
        session: activeSessionValue(),
        copy_scripts: true,
      }),
    });
    setMessage(`Bundle exported: ${payload.paths.bundle_json}`);
  } catch (error) {
    setMessage(error.message);
  }
});

el.clearRejected.addEventListener("click", async () => {
  try {
    state.session = await api("/api/preferences", {
      method: "POST",
      body: JSON.stringify({
        session: activeSessionValue(),
        action: "clear_rejected",
        updated_at: new Date().toISOString(),
      }),
    });
    render();
  } catch (error) {
    setMessage(error.message);
  }
});

el.searchInput.addEventListener("input", () => {
  state.query = el.searchInput.value;
  render();
});

el.sourceFilter.addEventListener("change", () => {
  state.source = el.sourceFilter.value;
  render();
});

for (const button of el.filters) {
  button.addEventListener("click", () => {
    state.filter = button.dataset.filter;
    render();
  });
}

loadSessions().catch((error) => setMessage(error.message));
