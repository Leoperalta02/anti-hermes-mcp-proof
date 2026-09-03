/* Apex Luxury AI — staged discovery front door.
   Collects a local brief. Never claims deploy, MLS, voice, or a portal URL. */

const STAGES = [
  "welcome",
  "profile",
  "needs",
  "tools",
  "assets",
  "workflow",
  "review",
];

const STORAGE_KEY = "apex-realtor-brief-draft-v1";
const RECEIVER_URL = "http://127.0.0.1:8787/briefs";
const SECRET_PATTERN =
  /(password|passwd|api[_-]?key|secret|token|bearer|authorization|connection string|private[_-]?key)/i;

const state = {
  stageIndex: 0,
  values: {},
};

function $(id) {
  return document.getElementById(id);
}

function stageFieldsets() {
  return Array.from(document.querySelectorAll("#discovery-form .stage"));
}

function collectStage(fieldset) {
  const data = {};
  fieldset.querySelectorAll("input, select, textarea").forEach((el) => {
    if (!el.name) return;
    if (el.type === "checkbox") {
      if (el.name === "needs") {
        data.needs = data.needs || [];
        if (el.checked) data.needs.push(el.value);
      } else {
        data[el.name] = el.checked;
      }
    } else {
      data[el.name] = el.value.trim();
    }
  });
  return data;
}

function applyStage(fieldset, values) {
  fieldset.querySelectorAll("input, select, textarea").forEach((el) => {
    if (!el.name || !(el.name in values)) return;
    if (el.type === "checkbox") {
      if (el.name === "needs") {
        el.checked = Array.isArray(values.needs) && values.needs.includes(el.value);
      } else {
        el.checked = Boolean(values[el.name]);
      }
    } else if (values[el.name] != null) {
      el.value = values[el.name];
    }
  });
}

function persist() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        stageIndex: state.stageIndex,
        values: state.values,
        savedAt: new Date().toISOString(),
      })
    );
  } catch (_err) {
    /* private mode */
  }
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (_err) {
    return null;
  }
}

function clearDraft() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (_err) {
    /* ignore */
  }
}

function looksLikeSecret(values) {
  return JSON.stringify(values).search(SECRET_PATTERN) !== -1;
}

function displayValue(value) {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "skipped";
  if (typeof value === "boolean") return value ? "yes" : "no";
  if (value == null || String(value).trim() === "") return "skipped / unknown";
  return String(value);
}

function askedSummary(values) {
  const needs = values.needs || [];
  const named = [];
  if (values.full_name) named.push(values.full_name);
  if (values.brokerage) named.push(values.brokerage);
  if (values.market) named.push(values.market);
  const who = named.length ? named.join(" · ") : "A Realtor (name not given)";
  const focus = needs.length
    ? needs.join(", ")
    : values.needs_other || "needs not specified";
  return `${who}. Focus: ${focus}.`;
}

function classify(values) {
  const canStage = [
    "A local onboarding brief (this form).",
    "A proposed Harbor follow-up queue once a tenant is approved.",
    "Draft copy and consult packets after review.",
  ];
  const needsVerification = [];
  const optional = [];

  if (values.crm_name) {
    needsVerification.push(`CRM named “${values.crm_name}” — connection not attempted.`);
  } else {
    optional.push("CRM name can be added later.");
  }
  if (values.calendar_name) {
    needsVerification.push(`Calendar named “${values.calendar_name}” — no sync from this page.`);
  }
  if (values.mls_name) {
    needsVerification.push(`MLS/listing source “${values.mls_name}” — no feed, IDX, or ShowingTime claim.`);
  }
  if ((values.needs || []).includes("copy")) {
    canStage.push("Quill listing/social copy drafts after Hermes review.");
  }
  if ((values.needs || []).includes("dates")) {
    canStage.push("Keystone date reminders as drafts, not contract advice.");
  }
  optional.push("Voice and reputation modules remain optional and off.");
  optional.push("A future Rosy private workspace would be a separate authenticated surface.");

  return { canStage, needsVerification, optional };
}

function buildBrief() {
  const createdAt = new Date().toISOString();
  const classification = classify(state.values);
  return {
    kind: "apex_realtor_onboarding_brief",
    status: "staged",
    created_at: createdAt,
    surface: "public-front-door",
    claims: {
      agent_deployed: false,
      portal_created: false,
      mls_connected: false,
      voice_enabled: false,
      calendar_synced: false,
    },
    asked: askedSummary(state.values),
    answers: state.values,
    can_stage: classification.canStage,
    needs_verification: classification.needsVerification,
    optional: classification.optional,
  };
}

function renderProgress() {
  const list = $("form-progress");
  if (!list) return;
  list.innerHTML = STAGES.map((name, i) => {
    const cls = i === state.stageIndex ? "current" : i < state.stageIndex ? "done" : "";
    return `<li class="${cls}">${name}</li>`;
  }).join("");
}

function renderReview() {
  const panel = $("review-panel");
  if (!panel) return;
  const v = state.values;
  const rows = [
    ["Profile", [v.full_name, v.brokerage, v.market, v.email, v.phone].filter(Boolean).join(" · ") || "skipped / unknown"],
    ["Needs", displayValue(v.needs) + (v.needs_other ? ` — ${v.needs_other}` : "")],
    ["Tools", [v.crm_name, v.calendar_name, v.mls_name, v.website].filter(Boolean).join(" · ") || "skipped / unknown"],
    ["Assets", [v.listing_range, v.photography, v.brand_notes].filter(Boolean).join(" · ") || "skipped / unknown"],
    ["Workflow", [v.cadence, v.approver, v.coverage_hours].filter(Boolean).join(" · ") || "skipped / unknown"],
  ];
  panel.innerHTML = rows
    .map(
      ([title, body]) =>
        `<article><h3>${title}</h3><p>${escapeHtml(body)}</p></article>`
    )
    .join("");
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showStage() {
  const fields = stageFieldsets();
  fields.forEach((fs, i) => {
    fs.hidden = i !== state.stageIndex;
    if (i === state.stageIndex) applyStage(fs, state.values);
  });
  const last = state.stageIndex === STAGES.length - 1;
  $("back-btn").hidden = state.stageIndex === 0;
  $("next-btn").hidden = last;
  $("submit-btn").hidden = !last;
  $("skip-btn").hidden = last || state.stageIndex === 0;
  if (last) renderReview();
  renderProgress();
}

function storeCurrentStage() {
  const current = stageFieldsets()[state.stageIndex];
  if (current) {
    Object.assign(state.values, collectStage(current));
  }
}

function go(delta) {
  storeCurrentStage();
  state.stageIndex = Math.max(0, Math.min(STAGES.length - 1, state.stageIndex + delta));
  persist();
  showStage();
  $("form-status").textContent = "";
}

function renderResult(brief, receiverNote) {
  $("discovery-form").hidden = true;
  const box = $("staged-result");
  box.hidden = false;
  $("result-title").textContent = "Staged brief received. No agent was deployed.";
  $("result-lead").textContent = `${receiverNote} ${brief.asked}`;
  const blocks = [
    ["What she asked", brief.asked],
    ["What can be staged", brief.can_stage.join(" ")],
    [
      "What needs verification",
      brief.needs_verification.length
        ? brief.needs_verification.join(" ")
        : "No third-party system was named. Connections remain unattempted.",
    ],
    ["Optional", brief.optional.join(" ")],
  ];
  $("result-grid").innerHTML = blocks
    .map(([title, body]) => `<article><h3>${title}</h3><p>${escapeHtml(body)}</p></article>`)
    .join("");
  box.dataset.brief = JSON.stringify(brief, null, 2);
  box.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function submitBrief(event) {
  event.preventDefault();
  storeCurrentStage();
  if (looksLikeSecret(state.values)) {
    $("form-status").textContent =
      "This form does not accept passwords, API keys, or tokens. Remove them and try again.";
    return;
  }

  const brief = buildBrief();
  persist();
  $("form-status").textContent = "Saving staged brief locally…";

  let receiverNote =
    "The local receiver was not reached. The brief is saved in this browser and available as a JSON download.";

  try {
    const response = await fetch(RECEIVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(brief),
    });
    if (response.ok) {
      receiverNote =
        "Local receiver accepted the staged brief. JSON and Markdown were written to the onboarding-briefs folder on this machine.";
    } else {
      receiverNote =
        "The local receiver responded but did not accept the brief. Browser copy and JSON download remain.";
    }
  } catch (_err) {
    /* receiver down — expected in some staging sessions */
  }

  renderResult(brief, receiverNote);
  $("form-status").textContent = "";
}

function downloadBrief() {
  const box = $("staged-result");
  const text = box.dataset.brief || JSON.stringify(buildBrief(), null, 2);
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "apex-realtor-staged-brief.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function resetForm() {
  state.stageIndex = 0;
  state.values = {};
  clearDraft();
  document.getElementById("discovery-form").reset();
  $("discovery-form").hidden = false;
  $("staged-result").hidden = true;
  $("resume-banner").hidden = true;
  showStage();
}

function initNav() {
  const toggle = $("nav-toggle");
  const nav = $("primary-nav");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

function init() {
  initNav();
  const draft = loadDraft();
  if (draft && draft.values) {
    $("resume-banner").hidden = false;
  }

  $("resume-btn")?.addEventListener("click", () => {
    const saved = loadDraft();
    if (!saved) return;
    state.values = saved.values || {};
    state.stageIndex = Math.min(STAGES.length - 1, saved.stageIndex || 0);
    $("resume-banner").hidden = true;
    showStage();
  });
  $("discard-draft-btn")?.addEventListener("click", () => {
    clearDraft();
    $("resume-banner").hidden = true;
  });
  $("back-btn")?.addEventListener("click", () => go(-1));
  $("next-btn")?.addEventListener("click", () => go(1));
  $("skip-btn")?.addEventListener("click", () => go(1));
  $("save-btn")?.addEventListener("click", () => {
    storeCurrentStage();
    persist();
    $("form-status").textContent = "Draft saved in this browser. You can close the tab and resume later.";
  });
  $("discovery-form")?.addEventListener("submit", submitBrief);
  $("download-json")?.addEventListener("click", downloadBrief);
  $("another-brief")?.addEventListener("click", resetForm);
  showStage();
}

document.addEventListener("DOMContentLoaded", init);
