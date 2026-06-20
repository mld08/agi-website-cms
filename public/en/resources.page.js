// Click-to-load YouTube facade (already privacy-friendly: youtube-nocookie, loaded on press)
document.querySelectorAll('.rs-video-facade').forEach(function (b) {
  b.addEventListener('click', function () {
    var frame = document.createElement('div'); frame.className = 'rs-video-frame';
    var f = document.createElement('iframe');
    f.src = b.dataset.embed; f.title = b.getAttribute('aria-label');
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin'); f.allowFullscreen = true;
    frame.appendChild(f); b.parentNode.replaceChild(frame, b);
  });
});

// Image lightbox — accessible modal: focus moves in, is trapped, and is restored on close
(function () {
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.rs-shot img'));
  if (!imgs.length) return;
  var lb = document.createElement('div');
  lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Image viewer');
  lb.innerHTML = '<button class="lb-close" type="button" aria-label="Close"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"></line><line x1="18" y1="6" x2="6" y2="18"></line></svg></button>' +
    '<button class="lb-nav lb-prev" type="button" aria-label="Previous image"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="m15 18-6-6 6-6"></path></svg></button>' +
    '<button class="lb-nav lb-next" type="button" aria-label="Next image"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="m9 18 6-6-6-6"></path></svg></button>' +
    '<img alt="">';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img'); var idx = 0;
  var closeBtn = lb.querySelector('.lb-close');
  var focusable = Array.prototype.slice.call(lb.querySelectorAll('button'));
  var bg = Array.prototype.slice.call(document.body.children).filter(function (el) { return el !== lb; });
  var lastFocus = null;
  function show(i) { idx = (i + imgs.length) % imgs.length; var im = imgs[idx]; lbImg.src = im.currentSrc || im.src; lbImg.alt = im.alt || ''; }
  function open(i) {
    lastFocus = document.activeElement;
    show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden';
    bg.forEach(function (el) { el.setAttribute('inert', ''); });
    closeBtn.focus();
  }
  function close() {
    lb.classList.remove('open'); document.body.style.overflow = '';
    bg.forEach(function (el) { el.removeAttribute('inert'); });
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  imgs.forEach(function (im, i) { var s = im.closest('.rs-shot'); s.addEventListener('click', function () { open(i); }); });
  lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(idx - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(idx + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.closest('.lb-close') || e.target === lbImg) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') { close(); }
    else if (e.key === 'ArrowLeft') { show(idx - 1); }
    else if (e.key === 'ArrowRight') { show(idx + 1); }
    else if (e.key === 'Tab') {
      e.preventDefault();
      var i = focusable.indexOf(document.activeElement);
      var dir = e.shiftKey ? -1 : 1;
      focusable[(i + dir + focusable.length) % focusable.length].focus();
    }
  });
})();
