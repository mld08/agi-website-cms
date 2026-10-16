// Searchable country list for the Nationality field (combobox, ARIA 1.2 pattern).
// Country names come from the browser in the page language (Intl.DisplayNames).
(function () {
  const input = document.querySelector('[data-country-combo]');
  if (!input || !window.Intl || !Intl.DisplayNames) return;
  const lang = document.documentElement.lang === 'fr' ? 'fr' : 'en';
  const CODES = 'AF AL DZ AD AO AG AR AM AU AT AZ BS BH BD BB BY BE BZ BJ BT BO BA BW BR BN BG BF BI CV KH CM CA CF TD CL CN CO KM CG CD CR CI HR CU CY CZ DK DJ DM DO EC EG SV GQ ER EE SZ ET FJ FI FR GA GM GE DE GH GR GD GT GN GW GY HT HN HU IS IN ID IR IQ IE IL IT JM JP JO KZ KE KI KW KG LA LV LB LS LR LY LI LT LU MG MW MY MV ML MT MH MR MU MX FM MD MC MN ME MA MZ MM NA NR NP NL NZ NI NE NG KP MK NO OM PK PW PS PA PG PY PE PH PL PT QA RO RU RW KN LC VC WS SM ST SA SN RS SC SL SG SK SI SB SO ZA KR SS ES LK SD SR SE CH SY TW TJ TZ TH TL TG TO TT TN TR TM TV UG UA AE GB US UY UZ VU VA VE VN YE ZM ZW'.split(' ');
  const dn = new Intl.DisplayNames([lang], { type: 'region' });
  const norm = (s) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const all = CODES.map((c) => ({ c, n: dn.of(c) })).sort((a, b) => a.n.localeCompare(b.n, lang));
  const T = lang === 'fr'
    ? { none: 'Aucun pays trouvé. Vous pouvez garder votre saisie.' }
    : { none: 'No country found. You can keep what you typed.' };

  const wrap = document.createElement('div');
  wrap.className = 'cff-combo';
  input.parentNode.insertBefore(wrap, input);
  wrap.appendChild(input);
  const list = document.createElement('ul');
  list.className = 'cff-combo-list';
  list.id = input.id + '-list';
  list.setAttribute('role', 'listbox');
  list.hidden = true;
  wrap.appendChild(list);
  input.setAttribute('role', 'combobox');
  input.setAttribute('aria-autocomplete', 'list');
  input.setAttribute('aria-expanded', 'false');
  input.setAttribute('aria-controls', list.id);
  input.setAttribute('autocomplete', 'off');

  let items = [], active = -1;

  function render() {
    const q = norm(input.value);
    let groups;
    if (!q) groups = [[null, all]];
    else {
      const starts = [], contains = [];
      all.forEach((x) => { const n = norm(x.n); if (n.startsWith(q) || n.split(/[\s-]+/).some((w) => w.startsWith(q))) starts.push(x); else if (n.includes(q)) contains.push(x); });
      groups = [[null, starts.concat(contains)]];
    }
    list.innerHTML = '';
    items = [];
    groups.forEach(([label, arr]) => {
      if (!arr.length) return;
      if (label) { const h = document.createElement('li'); h.className = 'grp'; h.setAttribute('role', 'presentation'); h.textContent = label; list.appendChild(h); }
      arr.forEach((x) => {
        const li = document.createElement('li');
        li.id = list.id + '-' + x.c;
        li.setAttribute('role', 'option');
        li.textContent = x.n;
        li.addEventListener('mousedown', (e) => { e.preventDefault(); choose(x.n); });
        list.appendChild(li);
        items.push(li);
      });
    });
    if (!items.length) { const li = document.createElement('li'); li.className = 'empty'; li.setAttribute('role', 'presentation'); li.textContent = T.none; list.appendChild(li); }
    setActive(q && items.length ? 0 : -1);
  }
  function setActive(i) {
    items.forEach((li, k) => li.setAttribute('aria-selected', k === i ? 'true' : 'false'));
    active = i;
    if (i >= 0) {
      input.setAttribute('aria-activedescendant', items[i].id);
      const li = items[i];
      if (li.offsetTop < list.scrollTop) list.scrollTop = li.offsetTop;
      else if (li.offsetTop + li.offsetHeight > list.scrollTop + list.clientHeight) list.scrollTop = li.offsetTop + li.offsetHeight - list.clientHeight;
    } else input.removeAttribute('aria-activedescendant');
  }
  function open() { if (list.hidden) { render(); list.hidden = false; input.setAttribute('aria-expanded', 'true'); } }
  function close() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); }
  function choose(v) { input.value = v; close(); input.dispatchEvent(new Event('input', { bubbles: true })); }

  input.addEventListener('focus', open);
  input.addEventListener('click', open);
  input.addEventListener('input', (e) => { if (!e.isTrusted) return; if (list.hidden) { list.hidden = false; input.setAttribute('aria-expanded', 'true'); } render(); });
  input.addEventListener('blur', () => {
    close();
    const hit = all.find((x) => norm(x.n) === norm(input.value));
    if (hit && hit.n !== input.value) input.value = hit.n;
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); open(); setActive(Math.min(active + 1, items.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(Math.max(active - 1, 0)); }
    else if (e.key === 'Enter' && !list.hidden && active >= 0) { e.preventDefault(); choose(items[active].textContent); }
    else if (e.key === 'Escape') { close(); }
  });
})();
