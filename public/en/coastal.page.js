// TOC active state on scroll
(function () {
  const tocLinks = document.querySelectorAll('.toc-list a');
  const headings = [...document.querySelectorAll('.prose h2, .prose [id]')].filter(el => el.id);
  if (!tocLinks.length) return;
  const onScroll = () => {
    const sy = window.scrollY + 200;
    let current = headings[0]?.id;
    for (const h of headings) { if (h.offsetTop <= sy) current = h.id; }
    tocLinks.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + current));
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// Share buttons
(function () {
  const url = 'https://africagovernanceinstitute.org/en/coastal-futures.html';
  const title = document.title;
  const x = document.getElementById('shareX');
  const li = document.getElementById('shareLi');
  const cp = document.getElementById('shareCopy');
  if (x) x.href = 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(title);
  if (li) li.href = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url);
  if (cp) cp.addEventListener('click', (e) => {
    e.preventDefault();
    const done = () => {
      cp.style.borderColor = 'var(--agi-olive)';
      cp.style.color = 'var(--agi-olive)';
      setTimeout(() => { cp.style.borderColor = ''; cp.style.color = ''; }, 1200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done).catch(done);
    } else { done(); }
  });
})();

// Click-to-load YouTube (privacy-friendly: nothing is requested until the user presses play)
(function () {
  document.querySelectorAll('.video-facade').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = b.dataset.embed;
      f.title = b.getAttribute('aria-label');
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      f.allowFullscreen = true;
      b.parentNode.replaceChild(f, b);
    });
  });
})();

// Image lightbox — accessible modal: focus moves in, is trapped, and is restored on close
(function () {
  const imgs = document.querySelectorAll('.art-figure img, .gallery-grid img, .ahd-photo img');
  if (!imgs.length) return;
  const lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Image viewer');
  lb.innerHTML = '<button class="lb-close" type="button" aria-label="Close"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button><img alt="">';
  document.body.appendChild(lb);
  const lbImg = lb.querySelector('img');
  const closeBtn = lb.querySelector('.lb-close');
  const bg = [...document.body.children].filter(el => el !== lb);
  let lastFocus = null;
  const open = (src, alt) => {
    lastFocus = document.activeElement;
    lbImg.src = src; lbImg.alt = alt || '';
    lb.classList.add('open'); document.body.style.overflow = 'hidden';
    bg.forEach(el => el.setAttribute('inert', ''));
    closeBtn.focus();
  };
  const close = () => {
    lb.classList.remove('open'); document.body.style.overflow = '';
    bg.forEach(el => el.removeAttribute('inert'));
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  };
  imgs.forEach(im => { im.addEventListener('click', () => open(im.currentSrc || im.src, im.alt)); });
  lb.addEventListener('click', (e) => { if (e.target === lb || e.target.closest('.lb-close')) close(); });
  document.addEventListener('keydown', (e) => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') { close(); }
    else if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); }
  });
})();
