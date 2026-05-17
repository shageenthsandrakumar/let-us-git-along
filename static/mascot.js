/* FounderFit Mascot — Fitz the purple bot */
(function () {
  const PAGE_HINTS = {
    '/': [
      "Hi! I'm Fitz 👋 I help founders find their perfect co-founder match.",
      "FounderFit analyzes 10 dimensions of compatibility — from execution style to GTM orientation.",
      "Click 'Start Free Assessment' to discover your founder archetype!",
    ],
    '/index.html': [
      "Hi! I'm Fitz 👋 I help founders find their perfect co-founder match.",
      "FounderFit analyzes 10 dimensions of compatibility — from execution style to GTM orientation.",
      "Click 'Start Free Assessment' to discover your founder archetype!",
    ],
    '/onboarding.html': [
      "Let's build your founder profile! Takes about 2 minutes.",
      "Be honest — FounderFit works best with authentic answers, not ideal ones.",
      "After this, I'll take you to your full compatibility assessment.",
    ],
    '/assessment.html': [
      "10 questions, one per compatibility dimension.",
      "There are no wrong answers — only honest ones.",
      "Your profile powers the AI compatibility engine. Make it real!",
    ],
    '/dashboard.html': [
      "Enter both founders' profiles and I'll run a full multi-agent analysis.",
      "The AI engine scores 10 dimensions and predicts friction points before they happen.",
      "Results include GTM archetype, strengths, and preventive agreements.",
    ],
    '/portfolio.html': [
      "Meet the 5 AI agents working behind the scenes.",
      "Each agent has a specialized role — from compatibility scoring to GTM strategy.",
      "They coordinate to give you a complete founder intelligence report.",
    ],
  };

  function getHints() {
    const path = window.location.pathname;
    return PAGE_HINTS[path] || PAGE_HINTS['/'];
  }

  function createMascot() {
    const style = document.createElement('style');
    style.textContent = `
      #fitz-mascot {
        position: fixed;
        bottom: 28px;
        right: 28px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 12px;
        font-family: 'Inter', -apple-system, sans-serif;
      }
      #fitz-bubble {
        background: #13131a;
        border: 1px solid #2a2a3a;
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        max-width: 240px;
        font-size: 13px;
        color: #e0e0f0;
        line-height: 1.55;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(139,92,246,0.12);
        opacity: 0;
        transform: translateY(8px) scale(0.96);
        transition: opacity 0.3s ease, transform 0.3s ease;
        pointer-events: none;
        position: relative;
      }
      #fitz-bubble.visible {
        opacity: 1;
        transform: translateY(0) scale(1);
        pointer-events: auto;
      }
      #fitz-bubble-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 10px;
        gap: 8px;
      }
      #fitz-bubble-nav button {
        background: none;
        border: 1px solid #2a2a3a;
        border-radius: 6px;
        color: #8a8a9a;
        font-size: 11px;
        padding: 4px 10px;
        cursor: pointer;
        transition: border-color 0.2s, color 0.2s;
        font-family: inherit;
      }
      #fitz-bubble-nav button:hover {
        border-color: #8b5cf6;
        color: #e0e0f0;
      }
      #fitz-hint-counter {
        font-size: 10px;
        color: #4a4a5a;
        font-variant-numeric: tabular-nums;
      }
      #fitz-btn {
        width: 64px;
        height: 64px;
        cursor: pointer;
        animation: fitzFloat 3s ease-in-out infinite;
        filter: drop-shadow(0 0 18px rgba(139,92,246,0.5));
        transition: filter 0.3s;
        flex-shrink: 0;
      }
      #fitz-btn:hover {
        filter: drop-shadow(0 0 26px rgba(139,92,246,0.8));
      }
      @keyframes fitzFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
      }
      .fitz-eye {
        animation: fitzBlink 4s ease-in-out infinite;
      }
      @keyframes fitzBlink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
      }
      #fitz-chest-glow {
        animation: fitzPulse 2s ease-in-out infinite;
      }
      @keyframes fitzPulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; filter: drop-shadow(0 0 6px #a855f7); }
      }
      .fitz-sparkle {
        animation: fitzSpark var(--dur, 3s) ease-in-out infinite var(--delay, 0s);
      }
      @keyframes fitzSpark {
        0%, 100% { opacity: 0.3; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
      }
    `;
    document.head.appendChild(style);

    const hints = getHints();
    let hintIdx = 0;
    let bubbleOpen = false;

    const wrapper = document.createElement('div');
    wrapper.id = 'fitz-mascot';

    const bubble = document.createElement('div');
    bubble.id = 'fitz-bubble';
    bubble.innerHTML = `
      <span id="fitz-hint-text">${hints[0]}</span>
      <div id="fitz-bubble-nav">
        <span id="fitz-hint-counter">1 / ${hints.length}</span>
        <div style="display:flex;gap:6px;">
          <button id="fitz-prev">&#8592;</button>
          <button id="fitz-next">&#8594;</button>
        </div>
      </div>
    `;

    // SVG mascot
    const svg = `<svg id="fitz-btn" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
      <!-- sparkles -->
      <circle class="fitz-sparkle" style="--dur:2.8s;--delay:0s" cx="10" cy="30" r="2.5" fill="#818cf8" opacity="0.7"/>
      <circle class="fitz-sparkle" style="--dur:3.5s;--delay:0.4s" cx="88" cy="22" r="2" fill="#a5b4fc" opacity="0.6"/>
      <circle class="fitz-sparkle" style="--dur:2.4s;--delay:0.8s" cx="92" cy="55" r="1.8" fill="#c084fc" opacity="0.5"/>
      <circle class="fitz-sparkle" style="--dur:3.2s;--delay:1.2s" cx="6" cy="62" r="2" fill="#818cf8" opacity="0.5"/>
      <circle class="fitz-sparkle" style="--dur:2.6s;--delay:0.6s" cx="78" cy="8" r="1.5" fill="#a5b4fc" opacity="0.7"/>
      <circle class="fitz-sparkle" style="--dur:3.8s;--delay:1.6s" cx="20" cy="12" r="1.8" fill="#c084fc" opacity="0.5"/>

      <!-- neck -->
      <rect x="43" y="58" width="14" height="8" rx="3" fill="#1e1e2e"/>

      <!-- body -->
      <rect x="28" y="64" width="44" height="38" rx="12" fill="#1a1a2e"/>
      <rect x="30" y="66" width="40" height="34" rx="10" fill="#1e1e30"/>

      <!-- chest glow -->
      <circle id="fitz-chest-glow" cx="50" cy="83" r="7" fill="#7c3aed" opacity="0.9"/>
      <circle cx="50" cy="83" r="5" fill="#a855f7"/>
      <circle cx="50" cy="83" r="3" fill="#c084fc"/>

      <!-- left arm -->
      <rect x="14" y="67" width="16" height="10" rx="5" fill="#1a1a2e"/>
      <!-- left hand -->
      <circle cx="13" cy="72" r="7" fill="#2a2a3e"/>
      <circle cx="13" cy="72" r="5.5" fill="#374151"/>
      <!-- left thumb up -->
      <ellipse cx="10" cy="67" rx="3" ry="4.5" rx="3" fill="#374151" transform="rotate(-20 10 67)"/>

      <!-- right arm -->
      <rect x="70" y="67" width="16" height="10" rx="5" fill="#1a1a2e"/>
      <!-- right hand -->
      <circle cx="87" cy="72" r="7" fill="#2a2a3e"/>
      <circle cx="87" cy="72" r="5.5" fill="#374151"/>
      <!-- right thumb up -->
      <ellipse cx="90" cy="67" rx="3" ry="4.5" fill="#374151" transform="rotate(20 90 67)"/>

      <!-- left leg -->
      <rect x="34" y="100" width="13" height="14" rx="6" fill="#1a1a2e"/>
      <!-- left foot -->
      <ellipse cx="38" cy="114" rx="8" ry="5" fill="#141428"/>

      <!-- right leg -->
      <rect x="53" y="100" width="13" height="14" rx="6" fill="#1a1a2e"/>
      <!-- right foot -->
      <ellipse cx="59" cy="114" rx="8" ry="5" fill="#141428"/>

      <!-- dome head outer glow -->
      <circle cx="50" cy="36" r="30" fill="url(#domeGradOuter)" opacity="0.25"/>

      <!-- dome head -->
      <circle cx="50" cy="36" r="26" fill="url(#domeGrad)"/>
      <circle cx="50" cy="36" r="26" fill="none" stroke="rgba(139,92,246,0.4)" stroke-width="1.5"/>

      <!-- dome highlight -->
      <ellipse cx="43" cy="25" rx="8" ry="6" fill="white" opacity="0.12" transform="rotate(-20 43 25)"/>

      <!-- eyes -->
      <g class="fitz-eye" style="transform-origin:38px 36px">
        <path d="M33 39 Q38 33 43 39" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
        <circle cx="38" cy="37" r="1.5" fill="white" opacity="0.6"/>
      </g>
      <g class="fitz-eye" style="transform-origin:62px 36px">
        <path d="M57 39 Q62 33 67 39" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
        <circle cx="62" cy="37" r="1.5" fill="white" opacity="0.6"/>
      </g>

      <!-- dome collar ring -->
      <ellipse cx="50" cy="60" rx="16" ry="4" fill="#1e1e2e"/>
      <ellipse cx="50" cy="60" rx="14" ry="3" fill="#252535"/>

      <defs>
        <radialGradient id="domeGrad" cx="40%" cy="35%" r="65%">
          <stop offset="0%" stop-color="#7c3aed"/>
          <stop offset="55%" stop-color="#6d28d9"/>
          <stop offset="100%" stop-color="#3b0764"/>
        </radialGradient>
        <radialGradient id="domeGradOuter" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#8b5cf6"/>
          <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0"/>
        </radialGradient>
      </defs>
    </svg>`;

    const botEl = document.createElement('div');
    botEl.innerHTML = svg;

    wrapper.appendChild(bubble);
    wrapper.appendChild(botEl);
    document.body.appendChild(wrapper);

    function updateBubble() {
      document.getElementById('fitz-hint-text').textContent = hints[hintIdx];
      document.getElementById('fitz-hint-counter').textContent = `${hintIdx + 1} / ${hints.length}`;
    }

    botEl.querySelector('#fitz-btn').addEventListener('click', () => {
      bubbleOpen = !bubbleOpen;
      bubble.classList.toggle('visible', bubbleOpen);
    });

    document.getElementById('fitz-next').addEventListener('click', (e) => {
      e.stopPropagation();
      hintIdx = (hintIdx + 1) % hints.length;
      updateBubble();
    });

    document.getElementById('fitz-prev').addEventListener('click', (e) => {
      e.stopPropagation();
      hintIdx = (hintIdx - 1 + hints.length) % hints.length;
      updateBubble();
    });

    // Auto-open on first visit
    setTimeout(() => {
      bubbleOpen = true;
      bubble.classList.add('visible');
    }, 1200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createMascot);
  } else {
    createMascot();
  }
})();
