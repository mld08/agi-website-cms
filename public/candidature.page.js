// Coastal Futures application form: draft persistence + submit UX.
// Submission endpoint: FormSubmit relay to AGI's contact inbox.
// Swap ENDPOINT for the institute's own backend when available.
(function () {
  const form = document.getElementById('cff');
  if (!form) return;
  const KEY = form.dataset.draftKey || 'agi-cf-application-draft';
  const errBox = document.getElementById('cffError');
  const draftNote = document.getElementById('cffDraft');

  // ---- Draft persistence (text-like fields only, not files) ----
  function snapshot() {
    const data = {};
    form.querySelectorAll('input, select, textarea').forEach((el) => {
      if (!el.name || el.type === 'file' || el.name.startsWith('_')) return;
      if (el.type === 'checkbox' || el.type === 'radio') {
        if (el.checked) {
          if (!data[el.name]) data[el.name] = [];
          data[el.name].push(el.value);
        }
      } else if (el.value) {
        data[el.name] = el.value;
      }
    });
    return data;
  }

  function restore() {
    let data;
    try { data = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return; }
    if (!data) return;
    form.querySelectorAll('input, select, textarea').forEach((el) => {
      if (!el.name || el.type === 'file' || !(el.name in data)) return;
      const v = data[el.name];
      if (el.type === 'checkbox' || el.type === 'radio') {
        el.checked = Array.isArray(v) && v.includes(el.value);
      } else {
        el.value = v;
      }
    });
    if (draftNote) draftNote.hidden = false;
  }

  let t;
  form.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(() => {
      try { localStorage.setItem(KEY, JSON.stringify(snapshot())); } catch (e) {}
      if (draftNote) draftNote.hidden = false;
    }, 400);
  });

  restore();

  // ---- Required checkbox groups (data-require-one) ----
  const groups = form.querySelectorAll('[data-require-one]');
  const MSG = document.documentElement.lang === 'fr'
    ? 'Cochez au moins une réponse.'
    : 'Tick at least one answer.';
  function checkGroup(g) {
    const boxes = g.querySelectorAll('input[type="checkbox"]');
    const any = Array.from(boxes).some((b) => b.checked);
    boxes[0].setCustomValidity(any ? '' : MSG);
  }
  groups.forEach((g) => {
    checkGroup(g);
    g.addEventListener('change', () => checkGroup(g));
  });

  // Native validation scrolls the invalid field into view itself;
  // scroll-margin-top in form.css keeps it clear of the sticky header
  // so the browser bubble anchors on the visible field.

  // ---- Highlight every missing field once submit is attempted ----
  // CSS paints .show-missing :invalid controls red; :invalid updates
  // live, so borders clear as soon as each field is filled.
  form.addEventListener('invalid', () => {
    form.classList.add('show-missing');
  }, true);

  // ---- Side nav scroll-spy ----
  const navLinks = document.querySelectorAll('.cff-nav a');
  if (navLinks.length && 'IntersectionObserver' in window) {
    const map = new Map();
    navLinks.forEach((a) => {
      const sec = document.querySelector(a.getAttribute('href'));
      if (sec) map.set(sec, a);
    });
    let current = null;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          if (current) current.classList.remove('active');
          current = map.get(en.target);
          if (current) current.classList.add('active');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    map.forEach((_, sec) => io.observe(sec));
  }

  // ---- Submit ----
  form.addEventListener('submit', () => {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = btn.dataset.busy || btn.textContent;
    }
    if (errBox) errBox.classList.remove('show');
    // Draft is cleared on the confirmation page (only after a real redirect).
  });
})();
