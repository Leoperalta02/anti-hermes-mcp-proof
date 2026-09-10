/**
 * Apex Luxury AI — Sovereign Onboarding Wizard (Chunk 2)
 * 3-step flow: Practice Details → Subdomain Claim → Plan Authorization
 */

(function () {
  const STRIPE_CHECKOUT = {
    solo_sovereign: 'https://buy.stripe.com/test_apex_solo_sovereign',
    elite_sovereign: 'https://buy.stripe.com/test_apex_elite_sovereign',
  };

  const RESERVED_SLUGS = new Set([
    'admin', 'api', 'www', 'app', 'mail', 'support', 'billing', 'stripe',
    'hermes', 'rosie', 'vance', 'toki', 'sofia', 'apex', 'luxury',
  ]);

  const state = {
    step: 1,
    cosName: 'Victoria',
    plan: 'solo_sovereign',
  };

  const els = {};

  function $(id) {
    return document.getElementById(id);
  }

  function slugify(value) {
    return value
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, '')
      .slice(0, 32);
  }

  function deriveDefaultSlug() {
    const name = els.realtorName?.value.trim() || '';
    const first = name.split(/\s+/)[0] || '';
    return slugify(first) || 'yourname';
  }

  function updateProgress() {
    const fillPct = state.step === 1 ? 0 : state.step === 2 ? 50 : 100;
    if (els.progressFill) {
      els.progressFill.style.width = `${fillPct}%`;
    }

    document.querySelectorAll('.progress-step').forEach((node) => {
      const stepNum = Number(node.dataset.step, 10);
      node.classList.toggle('active', stepNum === state.step);
      node.classList.toggle('complete', stepNum < state.step);
      const dot = node.querySelector('.step-dot');
      if (dot && stepNum < state.step) {
        dot.textContent = '✓';
      } else if (dot) {
        dot.textContent = String(stepNum);
      }
    });

    document.querySelectorAll('.step-panel').forEach((panel) => {
      panel.classList.toggle('active', Number(panel.dataset.step, 10) === state.step);
    });
  }

  function goToStep(step) {
    state.step = Math.max(1, Math.min(3, step));
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function validateStep1() {
    const required = [
      { el: els.realtorName, label: 'Realtor Full Name' },
      { el: els.brokerage, label: 'Brokerage' },
      { el: els.market, label: 'Primary Market/City' },
      { el: els.phone, label: 'Direct Phone' },
      { el: els.email, label: 'Email' },
    ];

    let valid = true;
    required.forEach(({ el }) => {
      if (!el) return;
      const ok = el.value.trim().length > 0;
      el.classList.toggle('invalid', !ok);
      if (!ok) valid = false;
    });

    const cos = els.cosName?.value.trim();
    if (!cos) {
      els.cosName?.classList.add('invalid');
      valid = false;
    } else {
      els.cosName?.classList.remove('invalid');
      state.cosName = cos;
    }

    if (!valid) {
      els.formError?.classList.remove('hidden');
    } else {
      els.formError?.classList.add('hidden');
    }

    return valid;
  }

  function validateStep2() {
    const slug = slugify(els.subdomainSlug?.value || '');
    if (!slug || slug.length < 2) {
      els.subdomainSlug?.classList.add('invalid');
      return false;
    }
    els.subdomainSlug?.classList.remove('invalid');
    return true;
  }

  function updateSubdomainPreview() {
    const slug = slugify(els.subdomainSlug?.value || '') || 'yourname';
    const url = `${slug}.apexluxuryai.com`;

    if (els.previewUrl) {
      els.previewUrl.textContent = url;
    }

    const taken = RESERVED_SLUGS.has(slug);
    if (els.previewStatus) {
      els.previewStatus.textContent = taken
        ? 'This slug is reserved — choose another.'
        : 'Available — this sovereign address is ready to claim.';
      els.previewStatus.classList.toggle('taken', taken);
    }
  }

  function selectCosChip(chip) {
    document.querySelectorAll('.name-chip').forEach((c) => c.classList.remove('selected'));
    chip.classList.add('selected');
    const name = chip.dataset.name || chip.textContent.trim();
    if (els.cosName) {
      els.cosName.value = name;
      els.cosName.classList.remove('invalid');
    }
    state.cosName = name;
  }

  function selectPlan(card) {
    document.querySelectorAll('.plan-card').forEach((c) => {
      c.classList.remove('selected');
      c.setAttribute('aria-checked', 'false');
    });
    card.classList.add('selected');
    card.setAttribute('aria-checked', 'true');
    state.plan = card.dataset.plan || 'solo_sovereign';
  }

  function buildCheckoutUrl() {
    const base = STRIPE_CHECKOUT[state.plan] || STRIPE_CHECKOUT.solo_sovereign;
    const email = encodeURIComponent(els.email?.value.trim() || '');
    const name = encodeURIComponent(els.realtorName?.value.trim() || '');
    const slug = slugify(els.subdomainSlug?.value || deriveDefaultSlug());
    const cos = encodeURIComponent(els.cosName?.value.trim() || state.cosName);

    const params = new URLSearchParams();
    if (email) params.set('prefilled_email', decodeURIComponent(email));
    if (name) params.set('client_name', decodeURIComponent(name));
    params.set('subdomain', slug);
    params.set('cos_name', decodeURIComponent(cos));

    const qs = params.toString();
    return qs ? `${base}?${qs}` : base;
  }

  function authorizeAndProvision() {
    if (!validateStep2()) return;

    const slug = slugify(els.subdomainSlug?.value || '');
    if (RESERVED_SLUGS.has(slug)) {
      els.previewStatus?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    const btn = els.authorizeBtn;
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Opening Stripe Checkout…';
    }

    const payload = {
      kind: 'apex_sovereign_onboarding',
      realtor: {
        full_name: els.realtorName?.value.trim(),
        brokerage: els.brokerage?.value.trim(),
        market: els.market?.value.trim(),
        phone: els.phone?.value.trim(),
        email: els.email?.value.trim(),
      },
      cos_name: els.cosName?.value.trim() || state.cosName,
      subdomain: `${slug}.apexluxuryai.com`,
      plan: state.plan,
      timestamp: new Date().toISOString(),
    };

    try {
      sessionStorage.setItem('apex_onboarding_draft', JSON.stringify(payload));
    } catch (_) {
      /* ignore storage failures */
    }

    window.location.href = buildCheckoutUrl();
  }

  function bindEvents() {
    els.step1Next?.addEventListener('click', () => {
      if (validateStep1()) {
        if (!els.subdomainSlug?.value.trim()) {
          els.subdomainSlug.value = deriveDefaultSlug();
        }
        updateSubdomainPreview();
        goToStep(2);
      }
    });

    els.step2Back?.addEventListener('click', () => goToStep(1));
    els.step2Next?.addEventListener('click', () => {
      if (validateStep2()) goToStep(3);
    });

    els.step3Back?.addEventListener('click', () => goToStep(2));
    els.authorizeBtn?.addEventListener('click', authorizeAndProvision);

    els.subdomainSlug?.addEventListener('input', updateSubdomainPreview);

    document.querySelectorAll('.name-chip').forEach((chip) => {
      chip.addEventListener('click', () => selectCosChip(chip));
    });

    els.cosName?.addEventListener('input', () => {
      els.cosName.classList.remove('invalid');
      document.querySelectorAll('.name-chip').forEach((c) => {
        c.classList.toggle(
          'selected',
          c.dataset.name?.toLowerCase() === els.cosName.value.trim().toLowerCase()
        );
      });
    });

    document.querySelectorAll('.plan-card').forEach((card) => {
      card.addEventListener('click', () => selectPlan(card));
    });

    [els.realtorName, els.brokerage, els.market, els.phone, els.email].forEach((input) => {
      input?.addEventListener('input', () => input.classList.remove('invalid'));
    });
  }

  function init() {
    els.progressFill = $('progress-fill');
    els.realtorName = $('realtor-name');
    els.brokerage = $('brokerage');
    els.market = $('market');
    els.phone = $('phone');
    els.email = $('email');
    els.cosName = $('cos-name');
    els.subdomainSlug = $('subdomain-slug');
    els.previewUrl = $('preview-url');
    els.previewStatus = $('preview-status');
    els.formError = $('form-error');
    els.step1Next = $('step-1-next');
    els.step2Back = $('step-2-back');
    els.step2Next = $('step-2-next');
    els.step3Back = $('step-3-back');
    els.authorizeBtn = $('authorize-btn');

    bindEvents();
    updateProgress();
    updateSubdomainPreview();

    const defaultChip = document.querySelector('.name-chip[data-name="Victoria"]');
    if (defaultChip) selectCosChip(defaultChip);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
