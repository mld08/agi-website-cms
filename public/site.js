/* Africa Governance Institute, small site interactions */
(function () {
  // Language selector (globe dropdown). The active language is NOT inferred from
  // the folder you are viewing, that polluted detection and forced returning
  // visitors into one language. Only an explicit pick is remembered; the site
  // root then uses that, or falls back to the browser language.
  document.querySelectorAll('[data-lang-select]').forEach(sel => {
    const trigger = sel.querySelector('.lang-trigger');
    if (!trigger) return;
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = sel.classList.toggle('open');
      trigger.setAttribute('aria-expanded', String(open));
    });
  });
  const closeLangMenus = () => document.querySelectorAll('[data-lang-select].open').forEach(s => {
    s.classList.remove('open');
    const t = s.querySelector('.lang-trigger');
    if (t) t.setAttribute('aria-expanded', 'false');
  });
  document.addEventListener('click', closeLangMenus);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLangMenus(); });
  // Remember an explicit language choice (used by the root redirect).
  document.addEventListener('click', (e) => {
    const a = e.target.closest('.lang-menu a, .nav-lang a');
    if (a && a.dataset.l) { try { localStorage.setItem('agi-locale', a.dataset.l); } catch (err) {} }
  }, true);

  // Newsletter form. No backend yet: until the subscription endpoint is wired,
  // submitting opens the visitor's mail client with a pre-filled request. This
  // is honest (it actually sends) and trivial for the backend team to replace.
  // An aria-live region announces the outcome to assistive technology; the
  // backend team should keep setStatus(form, msg, isError) and swap the mailto
  // body for `fetch(endpoint, { email, locale })`, calling setStatus on resolve/reject.
  const FR = (document.documentElement.lang || 'en').slice(0, 2) === 'fr';
  const NL_MSG = FR ? {
    ok: 'Ouverture de votre messagerie pour finaliser l’inscription.',
    bad: 'Veuillez saisir une adresse e-mail valide.'
  } : {
    ok: 'Opening your email app to finish subscribing.',
    bad: 'Please enter a valid email address.'
  };
  function nlStatus(form) {
    let s = form.querySelector('.nl-status');
    if (!s) {
      s = document.createElement('p');
      s.className = 'nl-status';
      s.setAttribute('role', 'status');
      s.setAttribute('aria-live', 'polite');
      s.style.cssText = 'margin:10px 0 0;font-size:13px;line-height:1.5;min-height:1em';
      form.appendChild(s);
    }
    return s;
  }
  function setStatus(form, msg, isError) {
    const s = nlStatus(form);
    s.textContent = msg;
    s.style.opacity = isError ? '1' : '0.85';
    s.style.color = isError ? '#ffd2c2' : '';
  }
  document.querySelectorAll('#newsletter, .newsletter-form').forEach(form => {
    nlStatus(form); // present from the start so SR users discover the live region
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = form.querySelector('input[type=email]');
      const email = input && input.value ? input.value.trim() : '';
      if (!email || (input && !input.checkValidity())) { setStatus(form, NL_MSG.bad, true); if (input) input.focus(); return; }
      const subject = encodeURIComponent('Newsletter subscription / Inscription newsletter');
      const body = encodeURIComponent('Please add this address to the AGI newsletter: ' + email);
      window.location.href = 'mailto:contact@africagovernanceinstitute.org?subject=' + subject + '&body=' + body;
      input.value = '';
      setStatus(form, NL_MSG.ok, false);
    });
  });

  // Language toggle is handled by simple cross-links between /en/ and /fr/.

  // Fade-in on scroll
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.fade-in').forEach(el => io.observe(el));

  // Active nav highlighting based on file
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-primary a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path) a.classList.add('active');
    if (path === 'programs.html' && href === 'programs.html') a.classList.add('active');
    if (path === 'news.html' && href === 'news.html') a.classList.add('active');
  });

  // Mobile / tablet nav dropdown
  const navToggle = document.querySelector('.nav-toggle');
  const navPrimary = document.getElementById('primary-nav');
  if (navToggle && navPrimary) {
    // On small screens the bar CTA is hidden (CSS); repeat it inside the menu.
    const barCta = document.querySelector('.header-cta .btn-primary');
    if (barCta && !navPrimary.querySelector('.nav-cta')) {
      const menuCta = barCta.cloneNode(true);
      menuCta.className = 'nav-cta';
      navPrimary.appendChild(menuCta);
    }
    // Repeat the language choices inside the menu, for screens where the
    // utility bar (which holds the globe selector) is hidden.
    if (!navPrimary.querySelector('.nav-lang')) {
      const langLinks = document.querySelectorAll('[data-lang-select] .lang-menu a');
      if (langLinks.length) {
        const wrap = document.createElement('div');
        wrap.className = 'nav-lang';
        langLinks.forEach(a => wrap.appendChild(a.cloneNode(true)));
        navPrimary.appendChild(wrap);
      }
    }
    const close = () => {
      navPrimary.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    };
    navToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = navPrimary.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    navPrimary.querySelectorAll('a').forEach(a => a.addEventListener('click', close));
    document.addEventListener('click', (e) => {
      if (!navPrimary.contains(e.target) && !navToggle.contains(e.target)) close();
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    window.addEventListener('resize', () => { if (window.innerWidth > 1080) close(); });
  }

  // Team-card full-pose photo swap, touch + keyboard parity.
  // Desktop hover (and keyboard focus on linked cards) already reveals the
  // alternate photo via CSS. On touch devices there is no hover, so the swap
  // was invisible. Here we add a visible tap affordance plus a tap gesture:
  // on a linked card the first tap reveals the photo and the second follows the
  // link; the non-linked support-staff cards simply toggle.
  (function () {
    const canHover = window.matchMedia('(hover: hover)').matches;
    document.querySelectorAll('.tm-card').forEach(card => {
      if (!card.querySelector('.tm-photo img.alt')) return;
      card.classList.add('has-alt');
      const photo = card.querySelector('.tm-photo');
      if (photo && !photo.querySelector('.tm-flip-hint')) {
        const hint = document.createElement('span');
        hint.className = 'tm-flip-hint';
        hint.setAttribute('aria-hidden', 'true');
        hint.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h13l-3-3"/><path d="M21 17H8l3 3"/></svg>';
        photo.appendChild(hint);
      }
      if (canHover) return;
      const isLink = card.tagName === 'A';
      card.addEventListener('click', (e) => {
        if (isLink) {
          if (!card.classList.contains('show-alt')) { e.preventDefault(); card.classList.add('show-alt'); }
        } else {
          card.classList.toggle('show-alt');
        }
      });
    });
  })();
})();
