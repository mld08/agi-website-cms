// Copy email address: instant, language-neutral feedback; clipboard API with fallback
(function () {
  const btn = document.getElementById('copyMail');
  if (!btn) return;
  const ADDR = 'contact@africagovernanceinstitute.org';
  function fallbackCopy() {
    const ta = document.createElement('textarea');
    ta.value = ADDR;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    ta.remove();
  }
  btn.addEventListener('click', () => {
    btn.classList.add('copied');
    setTimeout(() => btn.classList.remove('copied'), 1600);
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(ADDR).catch(fallbackCopy);
      } else {
        fallbackCopy();
      }
    } catch (e) { fallbackCopy(); }
  });
})();

// Click-to-load OpenStreetMap (privacy: no request until the user asks for it)
document.querySelectorAll('.map-load').forEach(function(b){
  b.addEventListener('click', function(){
    var f = document.createElement('iframe');
    f.src = b.dataset.src; f.title = b.dataset.title; f.loading = 'lazy';
    var wrap = b.closest('[data-map]');
    wrap.innerHTML = ''; wrap.appendChild(f);
  });
});
