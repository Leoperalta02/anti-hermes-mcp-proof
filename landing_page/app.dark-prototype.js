// Apex Luxury AI — Client-Side Application Logic

document.addEventListener('DOMContentLoaded', () => {
  // --------------------------------------------------------------------------
  // 1. Live AI Concierge Chat Simulator
  // --------------------------------------------------------------------------
  const chatForm = document.getElementById('demo-chat-form');
  const chatInput = document.getElementById('demo-chat-input');
  const chatWindow = document.getElementById('demo-chat-window');

  if (chatForm && chatInput && chatWindow) {
    const aiResponses = [
      "Confirmed! I've reserved your private VIP walkthrough for Friday at 3:00 PM. A calendar invite and gate access pass have been dispatched to your phone.",
      "Certainly. The residence includes a 3,000 sq ft wrap-around terrace, bespoke Boffi Italian kitchen, and 24/7 concierge security. Would you like me to send the full private dossier?",
      "Understood. I will also notify the listing agent that you have proof of funds verified. Would you like a private chauffeur coordinated for your arrival?",
      "Absolutely. Our AI concierge operates 24/7 to accommodate international luxury buyers across all time zones. Is there any specific architectural detail you'd like inspected beforehand?"
    ];
    let responseIndex = 0;

    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = chatInput.value.trim();
      if (!text) return;

      // Add Buyer message
      const buyerBubble = document.createElement('div');
      buyerBubble.className = 'chat-bubble buyer';
      buyerBubble.textContent = text;
      chatWindow.appendChild(buyerBubble);
      chatInput.value = '';
      chatWindow.scrollTop = chatWindow.scrollHeight;

      // Simulate typing indicator & response
      setTimeout(() => {
        const aiBubble = document.createElement('div');
        aiBubble.className = 'chat-bubble ai';
        aiBubble.textContent = aiResponses[responseIndex % aiResponses.length];
        responseIndex++;
        chatWindow.appendChild(aiBubble);
        chatWindow.scrollTop = chatWindow.scrollHeight;
      }, 600);
    });
  }

  // --------------------------------------------------------------------------
  // 2. Live AI Voice Waveform Simulator
  // --------------------------------------------------------------------------
  const toggleVoiceBtn = document.getElementById('toggle-voice-btn');
  const voiceBox = document.getElementById('voice-box');
  const voiceStatusText = document.getElementById('voice-status-text');
  const voiceTranscript = document.getElementById('voice-transcript');

  if (toggleVoiceBtn && voiceBox) {
    let isPlaying = false;
    let voiceInterval = null;

    const sampleCalls = [
      "\"Good evening. I have verified your requested showing for the Star Island Waterfront Triplex on Friday at 3:00 PM.\"",
      "\"Hello Mr. Sterling. The listing agent has confirmed proof of funds. The yacht dock is approved for vessels up to 130 feet.\"",
      "\"Good afternoon. I can arrange an after-hours private twilight tour of the Manhattan Glass Spire penthouse today at 7:30 PM.\""
    ];
    let callIdx = 0;

    toggleVoiceBtn.addEventListener('click', () => {
      isPlaying = !isPlaying;
      if (isPlaying) {
        voiceBox.classList.add('playing');
        voiceStatusText.textContent = "Voice AI: Speaking with High-Net-Worth Buyer...";
        toggleVoiceBtn.innerHTML = "<span>⏸️ Pause Voice Call</span>";

        voiceTranscript.textContent = sampleCalls[callIdx % sampleCalls.length];
        callIdx++;

        // Auto-pause after 6 seconds
        setTimeout(() => {
          if (isPlaying) {
            isPlaying = false;
            voiceBox.classList.remove('playing');
            voiceStatusText.textContent = "Voice AI: Tour Booked & Synced to ShowingTime";
            toggleVoiceBtn.innerHTML = "<span>🔊 Play Another Call</span>";
          }
        }, 6000);
      } else {
        voiceBox.classList.remove('playing');
        voiceStatusText.textContent = "Voice AI: Ready to speak with buyer";
        toggleVoiceBtn.innerHTML = "<span>🔊 Play Sample Voice Call</span>";
      }
    });
  }

  // --------------------------------------------------------------------------
  // 3. Interactive ROI & Commission Calculator
  // --------------------------------------------------------------------------
  const priceSlider = document.getElementById('price-slider');
  const inquiriesSlider = document.getElementById('inquiries-slider');
  const priceValDisplay = document.getElementById('price-val-display');
  const inquiriesValDisplay = document.getElementById('inquiries-val-display');
  const roiCommissionDisplay = document.getElementById('roi-commission-display');
  const roiDealsDisplay = document.getElementById('roi-deals-display');

  function updateROI() {
    if (!priceSlider || !inquiriesSlider) return;

    const price = parseInt(priceSlider.value, 10);
    const inquiries = parseInt(inquiriesSlider.value, 10);

    priceValDisplay.textContent = `$${(price / 1000000).toFixed(1)}M`.replace('.0M', 'M');
    inquiriesValDisplay.textContent = `${inquiries} leads`;

    // 2.5% commission rate, conservative extra deals based on after-hours lead conversion (approx 1 extra deal per 12 leads captured)
    const extraDeals = Math.max(1, Math.round(inquiries * 0.08));
    const commissionPerDeal = price * 0.025;
    const totalExtraCommission = extraDeals * commissionPerDeal;

    roiDealsDisplay.textContent = `+${extraDeals} Deals`;
    roiCommissionDisplay.textContent = `+$${totalExtraCommission.toLocaleString()}`;
  }

  if (priceSlider && inquiriesSlider) {
    priceSlider.addEventListener('input', updateROI);
    inquiriesSlider.addEventListener('input', updateROI);
    updateROI();
  }

  // --------------------------------------------------------------------------
  // 4. Instant MLS & IDX Feed Validator
  // --------------------------------------------------------------------------
  const mlsForm = document.getElementById('mls-test-form');
  const mlsResultBox = document.getElementById('mls-result-box');
  const mlsResultDetails = document.getElementById('mls-result-details');
  const validateBtn = document.getElementById('validate-mls-btn');

  if (mlsForm && mlsResultBox) {
    mlsForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const mlsId = document.getElementById('test-mls-id').value.trim() || 'FL-MLS-99482';
      const brokerage = document.getElementById('test-brokerage').value.trim() || 'Vance Luxury Properties';

      validateBtn.innerHTML = '<span>⚡ Validating MLS Feed with Pollen & Fizz...</span>';
      validateBtn.style.opacity = '0.8';

      setTimeout(() => {
        validateBtn.innerHTML = '<span>✓ MLS Feed Validated</span>';
        validateBtn.style.opacity = '1';
        mlsResultDetails.textContent = `Agent ID ${mlsId} active with ${brokerage}. IDX listing synchronization and ShowingTime calendar integration are verified online.`;
        mlsResultBox.classList.add('active');
      }, 800);
    });
  }

  // --------------------------------------------------------------------------
  // 5. 60-Second Realtor Onboarding Wizard
  // --------------------------------------------------------------------------
  const stepContent1 = document.getElementById('step-content-1');
  const stepContent2 = document.getElementById('step-content-2');
  const deploymentSuccess = document.getElementById('deployment-success');
  const stepDot1 = document.getElementById('step-dot-1');
  const stepDot2 = document.getElementById('step-dot-2');
  const stepDot3 = document.getElementById('step-dot-3');

  const goToStep2Btn = document.getElementById('go-to-step-2');
  const backToStep1Btn = document.getElementById('back-to-step-1');
  const onboardingForm = document.getElementById('onboarding-form');
  const resetOnboardingBtn = document.getElementById('reset-onboarding-btn');
  const liveSubdomainLink = document.getElementById('live-subdomain-link');

  // Tier selection
  const tierCards = document.querySelectorAll('.tier-card');
  let selectedTier = 'ULTRA_LUXURY';

  tierCards.forEach((card) => {
    card.addEventListener('click', () => {
      tierCards.forEach((c) => c.classList.remove('selected'));
      card.classList.add('selected');
      selectedTier = card.getAttribute('data-tier');
    });
  });

  if (goToStep2Btn) {
    goToStep2Btn.addEventListener('click', () => {
      const name = document.getElementById('realtor-name').value.trim();
      const phone = document.getElementById('realtor-phone').value.trim();
      const brokerage = document.getElementById('realtor-brokerage').value.trim();

      if (!name || !phone || !brokerage) {
        alert('Please fill in your name, phone number, and brokerage.');
        return;
      }

      stepContent1.style.display = 'none';
      stepContent2.style.display = 'block';
      stepDot1.classList.remove('active');
      stepDot2.classList.add('active');
    });
  }

  if (backToStep1Btn) {
    backToStep1Btn.addEventListener('click', () => {
      stepContent2.style.display = 'none';
      stepContent1.style.display = 'block';
      stepDot2.classList.remove('active');
      stepDot1.classList.add('active');
    });
  }

  if (onboardingForm) {
    onboardingForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const realtorName = document.getElementById('realtor-name').value.trim() || 'Priscilla Vance';
      const cleanSlug = realtorName.toLowerCase().replace(/[^a-z0-9]/g, '');
      const subdomain = `https://${cleanSlug}.apexluxuryai.com`;

      const deployBtn = document.getElementById('deploy-agent-btn');
      deployBtn.innerHTML = '<span>⚡ Provisioning AI Agents (Hermes, Fizz, Honey, Pollen)...</span>';
      deployBtn.disabled = true;

      setTimeout(() => {
        stepContent2.style.display = 'none';
        stepDot2.classList.remove('active');
        stepDot3.classList.add('active');

        liveSubdomainLink.textContent = subdomain;
        liveSubdomainLink.href = subdomain;
        deploymentSuccess.classList.add('active');
      }, 1200);
    });
  }

  if (resetOnboardingBtn) {
    resetOnboardingBtn.addEventListener('click', () => {
      onboardingForm.reset();
      deploymentSuccess.classList.remove('active');
      stepContent1.style.display = 'block';
      stepDot3.classList.remove('active');
      stepDot2.classList.remove('active');
      stepDot1.classList.add('active');

      const deployBtn = document.getElementById('deploy-agent-btn');
      deployBtn.innerHTML = '<span>🚀 Deploy Live AI Concierge</span>';
      deployBtn.disabled = false;
    });
  }

  // --------------------------------------------------------------------------
  // 6. Live Activity Toast Notifications
  // --------------------------------------------------------------------------
  const liveToast = document.getElementById('live-toast');
  const toastTitle = document.getElementById('toast-title');
  const toastDesc = document.getElementById('toast-desc');

  const toastEvents = [
    { title: "VIP Showing Booked via AI", desc: "$16.5M Star Island Estate • Just now" },
    { title: "New Realtor Onboarded", desc: "Elena Rostova (Beverly Hills) • 2 min ago" },
    { title: "Proof of Funds Verified", desc: "Manhattan Glass Spire Penthouse • 5 min ago" },
    { title: "Hermes Automated MLS Ingestion", desc: "18 Luxury Listings Synced • 8 min ago" }
  ];
  let toastIndex = 0;

  function showNextToast() {
    if (!liveToast) return;
    const evt = toastEvents[toastIndex % toastEvents.length];
    toastIndex++;

    toastTitle.textContent = evt.title;
    toastDesc.textContent = evt.desc;
    liveToast.classList.add('show');

    setTimeout(() => {
      liveToast.classList.remove('show');
    }, 4500);
  }

  // Trigger first toast after 3s, then every 10s
  setTimeout(() => {
    showNextToast();
    setInterval(showNextToast, 11000);
  }, 3000);

  // --------------------------------------------------------------------------
  // 7. Smooth Navigation Scrolling
  // --------------------------------------------------------------------------
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
});
