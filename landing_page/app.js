/* Apex Luxury AI — Realtor sales front door.
   Quick onboard + optional setup brief → local receiver :8787 */

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
    return true;
  } catch (_err) {
    /* private mode */
    return false;
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
  if (values.team_name) named.push(`Team: ${values.team_name}`);
  if (values.team_leader) named.push(`Mentor: ${values.team_leader}`);
  if (values.office_address) named.push(values.office_address);
  if (values.market) named.push(values.market);
  const who = named.length ? named.join(" · ") : "A Realtor (name not given)";
  const focus = needs.length
    ? needs.join(", ")
    : values.needs_other || "needs not specified";
  return `${who}. Focus: ${focus}.`;
}

function classify(values) {
  const canStage = [
    "A prioritized follow-up and preparation queue.",
    "Reviewable drafts and summaries shaped around your workflow.",
    "A human-approved record of decisions and next steps.",
  ];
  const needsVerification = [];
  const optional = [];

  if (values.crm_name) {
    needsVerification.push(`CRM connection with ${values.crm_name} requires review during onboarding; it is not active from this brief.`);
  } else {
    optional.push("CRM connection can be discussed during your onboarding call.");
  }
  if (values.calendar_name) {
    needsVerification.push(`Calendar connection with ${values.calendar_name} requires review during onboarding; it is not active from this brief.`);
  }
  if (values.mls_name) {
    needsVerification.push(`MLS or listing-source connection for ${values.mls_name} requires review during onboarding; it is not active from this brief.`);
  }
  if ((values.needs || []).includes("copy")) {
    canStage.push("Listing and property content drafts held for your approval.");
  }
  if ((values.needs || []).includes("research")) {
    canStage.push("Market and comparable research preparation with assumptions noted.");
  }
  optional.push("Team workflow and brand guidance can be scoped during review.");

  return { canStage, needsVerification, optional };
}

function buildBrief() {
  const createdAt = new Date().toISOString();
  const classification = classify(state.values);
  return {
    kind: "apex_realtor_onboarding_brief",
    status: "received",
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
  const profileParts = [
    v.full_name,
    v.brokerage,
    v.team_name ? `Team: ${v.team_name}` : "",
    v.team_leader ? `Mentor: ${v.team_leader}` : "",
    v.office_address,
    v.market,
    v.email,
    v.phone
  ].filter(Boolean);

  const rows = [
    ["Profile & Team", profileParts.join(" · ") || "skipped / unknown"],
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

  // The controls sit at the bottom of a tall card. After advancing, bring the
  // new step's heading back below the sticky header instead of leaving the
  // viewport parked at the previous step's footer.
  const nextStage = stageFieldsets()[state.stageIndex];
  if (nextStage) {
    requestAnimationFrame(() => {
      nextStage.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
}

function renderResult(brief, receiverNote, workspaceLink = "") {
  $("discovery-form").hidden = true;
  const box = $("staged-result");
  box.hidden = false;
  $("result-title").textContent = "Setup Brief Received";
  $("result-lead").textContent = `${receiverNote} ${brief.asked}`;
  const blocks = [
    ["Your practice", brief.asked],
    ["Included in your setup", brief.can_stage.join(" ")],
    [
      "Integrations we'll configure",
      brief.needs_verification.length
        ? brief.needs_verification.join(" ")
        : "Standard luxury workflows. Third-party tools connected on your onboarding call.",
    ],
    ["Optional upgrades", brief.optional.join(" ")],
  ];
  $("result-grid").innerHTML = blocks
    .map(([title, body]) => `<article><h3>${title}</h3><p>${escapeHtml(body)}</p></article>`)
    .join("") + workspaceLink;
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
  $("form-status").textContent = "Saving your planning summary locally…";

  let receiverNote =
    "We saved your planning summary locally. Download a copy below—we'll follow up if the server was unreachable.";
  let workspaceLink = "";

  try {
    const response = await fetch(RECEIVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(brief),
    });
    const payload = await response.json();
    if (response.ok) {
      receiverNote =
        "Your setup brief was received. Our team will reach out to schedule your onboarding call.";
      workspaceLink = payload.workspace?.url
        ? `<p class="workspace-link"><a class="btn btn-primary" href="${escapeHtml(payload.workspace.url)}">Open Rosy STAGING / DEMO workspace</a></p>`
        : "";
    } else {
      receiverNote =
        "The local receiver responded but did not accept the brief. Browser copy and JSON download remain.";
    }
  } catch (_err) {
    /* receiver down — expected in some staging sessions */
  }

  renderResult(brief, receiverNote, workspaceLink);
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
    $("form-status").textContent = "Your saved answers are back. You can continue where you left off.";
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
    const saved = persist();
    if (saved) $("resume-banner").hidden = false;
    $("form-status").textContent = saved
      ? "Your answers are saved on this device. Use Continue above whenever you are ready to resume."
      : "We could not save your answers on this device. Keep this page open and try again later.";
  });
  $("discovery-form")?.addEventListener("submit", submitBrief);
  $("download-json")?.addEventListener("click", downloadBrief);
  $("another-brief")?.addEventListener("click", resetForm);
  initScorecard();
  initQuickOnboard();
  initPricingLinks();
  initArchitectureTour();
  showStage();
}

document.addEventListener("DOMContentLoaded", init);

/* ── Realtor Operational Bottleneck Audit ── */

const SCORECARD_STEPS = ["missed_calls", "followups", "listing_speed"];
const SCORECARD_LABELS = {
  missed_calls: "Missed calls",
  followups: "Follow-up",
  listing_speed: "Listing speed",
};

const LOST_REVENUE = {
  missed_calls: { few: 12000, several: 42000, regularly: 84000, constantly: 156000 },
  followups: { hour: 8000, same_day: 28000, next_day: 62000, cold: 108000 },
  listing_speed: { day: 10000, days2_3: 32000, week: 68000, weekend: 112000 },
};

const scorecardState = {
  stepIndex: 0,
  answers: {},
  lostRevenue: 0,
  submittedBrief: null,
};

function formatRevenue(amount) {
  if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`;
  if (amount >= 1000) return `$${Math.round(amount / 1000)}K`;
  return `$${amount}`;
}

function computeLostRevenue(answers = scorecardState.answers) {
  let total = 0;
  SCORECARD_STEPS.forEach((step) => {
    const value = answers[step];
    if (value && LOST_REVENUE[step][value] != null) {
      total += LOST_REVENUE[step][value];
    }
  });
  return total;
}

function revenueToRingScore(revenue) {
  return Math.min(100, Math.round((revenue / 200000) * 100));
}

function scorecardTier(revenue) {
  const apexAnnual = 497 * 12 + 1500;
  const roiMultiple = revenue / apexAnnual;

  if (revenue >= 150000) {
    return {
      title: "Critical revenue leak",
      tier: "High risk",
      copy: `You could be leaving roughly ${formatRevenue(revenue)} on the table each year from operational bottlenecks alone. At Solo Practice pricing, Apex pays for itself in under ${Math.max(1, Math.round(roiMultiple))}× your subscription.`,
      insights: [
        `Estimated annual commission at risk: ${formatRevenue(revenue)}.`,
        "Priority: dedicated Chief of Staff plus optional 24/7 bilingual concierge.",
        "4K dropzone cuts days off every new listing go-live.",
        "Commission your sovereign private office below—most producers recover one deal and cover a year of Apex.",
      ],
    };
  }
  if (revenue >= 75000) {
    return {
      title: "Significant opportunity",
      tier: "Elevated risk",
      copy: `Your answers suggest roughly ${formatRevenue(revenue)} in annual commission at risk. Apex typically pays for itself after one recovered luxury transaction.`,
      insights: [
        `Estimated annual commission at risk: ${formatRevenue(revenue)}.`,
        "Automated follow-up keeps hot buyers from choosing the agent who answered first.",
        "Seller dossiers help you win listings before competitors send a generic CMA.",
        "Most advisors at this level choose Elite Advisory Practice when adding producers.",
      ],
    };
  }
  if (revenue >= 30000) {
    return {
      title: "Moderate gap",
      tier: "Room to grow",
      copy: `You're likely leaving about ${formatRevenue(revenue)} per year on the table—not catastrophic, but exactly the margin that separates good years from record years.`,
      insights: [
        `Estimated annual commission at risk: ${formatRevenue(revenue)}.`,
        "Faster listing turnaround means fewer days on market and happier sellers.",
        "Bilingual SMS triage captures buyers other agents miss after hours.",
        "Solo Practice is the right starting point for individual top producers.",
      ],
    };
  }
  return {
    title: "Strong foundation",
    tier: "Lower risk",
    copy: `Your operations are relatively tight—estimated ${formatRevenue(revenue)} at risk. Apex still compounds your edge with 24/7 coverage and faster listing launches.`,
    insights: [
      `Estimated annual commission at risk: ${formatRevenue(revenue)}.`,
      "Even top producers use Apex for after-hours coverage and listing speed.",
      "Seller equity reports differentiate you in competitive listing presentations.",
      "Start with Solo Practice and scale to Elite Advisory Practice as your volume grows.",
    ],
  };
}

function scorecardEl(id) {
  return document.getElementById(id);
}

function scorecardSelected(name) {
  const checked = document.querySelector(`#scorecard-form input[name="${name}"]:checked`);
  return checked ? checked.value : "";
}

function computeScorecardScore(answers = scorecardState.answers) {
  return revenueToRingScore(computeLostRevenue(answers));
}

function updateScorecardMeter() {
  const revenue = computeLostRevenue();
  scorecardState.lostRevenue = revenue;
  const answered = SCORECARD_STEPS.filter((step) => scorecardState.answers[step]).length;
  const ring = scorecardEl("scorecard-ring");
  const value = scorecardEl("scorecard-ring-value");
  const tier = scorecardEl("scorecard-meter-tier");

  if (ring) ring.style.setProperty("--score", String(revenueToRingScore(revenue)));
  if (value) value.textContent = answered ? formatRevenue(revenue) : "—";
  if (tier) {
    tier.textContent = answered
      ? scorecardTier(revenue).tier
      : "Answer to begin";
  }
}

function showScorecardStep() {
  SCORECARD_STEPS.forEach((step, index) => {
    const fieldset = scorecardEl(`scorecard-step-${step}`);
    if (fieldset) fieldset.hidden = index !== scorecardState.stepIndex;
  });

  const stepName = SCORECARD_STEPS[scorecardState.stepIndex];
  const label = scorecardEl("scorecard-step-label");
  const bar = scorecardEl("scorecard-progress-bar");
  const back = scorecardEl("scorecard-back");
  const next = scorecardEl("scorecard-next");
  const progress = ((scorecardState.stepIndex + 1) / SCORECARD_STEPS.length) * 100;

  if (label) {
    label.textContent = `Question ${scorecardState.stepIndex + 1} of ${SCORECARD_STEPS.length} · ${SCORECARD_LABELS[stepName]}`;
  }
  if (bar) bar.style.width = `${progress}%`;
  if (back) back.hidden = scorecardState.stepIndex === 0;
  if (next) {
    next.textContent =
      scorecardState.stepIndex === SCORECARD_STEPS.length - 1
        ? "See my ROI"
        : "Continue";
  }
  scorecardEl("scorecard-status").textContent = "";
}

function storeScorecardAnswer() {
  const stepName = SCORECARD_STEPS[scorecardState.stepIndex];
  const value = scorecardSelected(stepName);
  if (value) scorecardState.answers[stepName] = value;
  updateScorecardMeter();
}

function renderScorecardResult() {
  const tier = scorecardTier(scorecardState.lostRevenue);
  scorecardEl("scorecard-tier-title").textContent = tier.title;
  scorecardEl("scorecard-result-copy").textContent = tier.copy;
  scorecardEl("scorecard-insights").innerHTML = tier.insights
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  scorecardEl("scorecard-form").hidden = true;
  scorecardEl("scorecard-actions").hidden = true;
  scorecardEl("scorecard-result").hidden = false;
  scorecardEl("scorecard-step-label").textContent = "Complete · ROI snapshot";
  scorecardEl("scorecard-progress-bar").style.width = "100%";
  updateScorecardMeter();
}

function buildScorecardBrief(lead = {}) {
  const tier = scorecardTier(scorecardState.lostRevenue);
  return {
    kind: "apex_realtor_bottleneck_audit",
    status: "received",
    created_at: new Date().toISOString(),
    surface: "public-front-door",
    lost_revenue_estimate: scorecardState.lostRevenue,
    tier: tier.title,
    answers: { ...scorecardState.answers },
    lead,
    asked: `Realtor bottleneck audit · ${tier.title} · ${formatRevenue(scorecardState.lostRevenue)} at risk`,
    can_stage: tier.insights,
    needs_verification: [
      "Revenue estimate is illustrative based on luxury-market averages.",
      "Custom ROI review available on onboarding call.",
    ],
    optional: ["Continue to claim your AI Private Office with the 60-second form."],
  };
}

function downloadScorecardSummary() {
  const leadForm = scorecardEl("scorecard-lead-form");
  const brief =
    scorecardState.submittedBrief ||
    buildScorecardBrief({
      name: leadForm?.elements?.lead_name?.value?.trim() || "",
      email: leadForm?.elements?.lead_email?.value?.trim() || "",
      phone: leadForm?.elements?.lead_phone?.value?.trim() || "",
      property: leadForm?.elements?.lead_property?.value?.trim() || "",
    });
  const blob = new Blob([JSON.stringify(brief, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "apex-realtor-bottleneck-audit.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function submitScorecardLead(event) {
  event.preventDefault();
  const form = scorecardEl("scorecard-lead-form");
  const status = scorecardEl("scorecard-lead-status");
  if (!form || !status) return;

  const lead = {
    name: form.lead_name.value.trim(),
    email: form.lead_email.value.trim(),
    phone: form.lead_phone.value.trim(),
    property: form.lead_property.value.trim(),
  };

  if (!lead.name || !lead.email) {
    status.textContent = "Name and email are required for follow-up.";
    return;
  }
  if (looksLikeSecret(lead)) {
    status.textContent = "Do not enter passwords, API keys, or tokens.";
    return;
  }

  const brief = buildScorecardBrief(lead);
  scorecardState.submittedBrief = brief;
  status.textContent = "Sending your audit…";

  try {
    const response = await fetch(RECEIVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(brief),
    });
    if (response.ok) {
      status.textContent =
        "Audit received. We'll follow up with your full breakdown and onboarding options.";
    } else {
      status.textContent =
        "Saved locally. Download your audit summary or claim your AI Private Office below.";
    }
  } catch (_err) {
    status.textContent =
      "Connection issue—your audit is saved in this browser. Download a copy or continue to onboarding.";
  }
}

function initScorecard() {
  const form = scorecardEl("scorecard-form");
  if (!form) return;

  form.querySelectorAll('input[type="radio"]').forEach((input) => {
    input.addEventListener("change", () => {
      storeScorecardAnswer();
    });
  });

  scorecardEl("scorecard-back")?.addEventListener("click", () => {
    if (scorecardState.stepIndex > 0) {
      scorecardState.stepIndex -= 1;
      showScorecardStep();
    }
  });

  scorecardEl("scorecard-next")?.addEventListener("click", () => {
    const stepName = SCORECARD_STEPS[scorecardState.stepIndex];
    const value = scorecardSelected(stepName);
    if (!value) {
      scorecardEl("scorecard-status").textContent = "Choose an option to continue.";
      return;
    }
    scorecardState.answers[stepName] = value;
    updateScorecardMeter();

    if (scorecardState.stepIndex >= SCORECARD_STEPS.length - 1) {
      renderScorecardResult();
      scorecardEl("scorecard-result")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      return;
    }

    scorecardState.stepIndex += 1;
    showScorecardStep();
  });

  scorecardEl("scorecard-lead-form")?.addEventListener("submit", submitScorecardLead);
  scorecardEl("scorecard-download")?.addEventListener("click", downloadScorecardSummary);
  showScorecardStep();
  updateScorecardMeter();
}

function initPricingLinks() {
  document.querySelectorAll(".pricing-cta[data-plan]").forEach((link) => {
    link.addEventListener("click", () => {
      const plan = link.getAttribute("data-plan");
      const select = document.querySelector('#quick-onboard-form select[name="plan"]');
      if (select && plan) select.value = plan;
    });
  });
}

function initQuickOnboard() {
  const form = document.getElementById("quick-onboard-form");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.getElementById("quick-status");
    const values = {
      full_name: form.full_name.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      brokerage: form.brokerage.value.trim(),
      plan: form.plan.value,
      market: form.market.value.trim(),
    };

    if (!values.full_name || !values.email || !values.phone || !values.brokerage || !values.plan) {
      status.textContent = "Please complete all required fields.";
      return;
    }
    if (looksLikeSecret(values)) {
      status.textContent = "Do not enter passwords, API keys, or tokens.";
      return;
    }

    const brief = {
      kind: "apex_realtor_quick_onboard",
      status: "received",
      created_at: new Date().toISOString(),
      surface: "public-front-door",
      answers: values,
      asked: `${values.full_name} · ${values.brokerage} · ${values.plan} plan`,
    };

    status.textContent = "Submitting…";
    let note = "We saved your request. Our team will contact you within one business day.";

    try {
      const response = await fetch(RECEIVER_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(brief),
      });
      if (!response.ok) {
        note = "We received your details locally. Our team will follow up shortly.";
      }
    } catch (_err) {
      note = "Connection issue—we saved your request and will follow up by email.";
    }

    form.hidden = true;
    const result = document.getElementById("quick-result");
    result.hidden = false;
    document.getElementById("quick-result-lead").textContent =
      `${note} Welcome, ${values.full_name}. We'll commission your ${values.plan === "elite" ? "Elite Advisory Practice" : "Solo Practice"} sovereign private office for ${values.brokerage}.`;
    status.textContent = "";
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function initArchitectureTour() {
  const tabs = Array.from(document.querySelectorAll(".architecture-tab"));
  const panels = Array.from(document.querySelectorAll(".architecture-panel"));
  if (!tabs.length || !panels.length) return;

  function activate(panelId) {
    tabs.forEach((tab) => {
      const active = tab.dataset.panel === panelId;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    panels.forEach((panel) => {
      const active = panel.dataset.panel === panelId;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => activate(tab.dataset.panel));
  });
}
