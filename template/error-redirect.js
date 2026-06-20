// Error-page language router. EXTERNAL on purpose: the site CSP
// (script-src 'self' …, no 'unsafe-inline') blocks inline scripts, so this must
// live in a file to run in production. Routes the visitor to their language's
// version of the same error page. A remembered choice wins; otherwise the
// browser language decides. French is primary.
(function () {
  function detect() {
    var langs;
    try {
      langs = (navigator.languages && navigator.languages.length)
        ? navigator.languages : [navigator.language || navigator.userLanguage || ''];
    } catch (e) { langs = []; }
    for (var i = 0; i < langs.length; i++) {
      var c = String(langs[i] || '').toLowerCase();
      if (c.indexOf('fr') === 0) return 'fr';
      if (c.indexOf('en') === 0) return 'en';
    }
    return 'fr';
  }
  var saved = null;
  try { saved = localStorage.getItem('agi-locale'); } catch (e) {}
  var lang = (saved === 'en' || saved === 'fr') ? saved : detect();
  var file = location.pathname.split('/').pop() || '404.html';
  if (!/^(403|404|500)\.html$/.test(file)) file = '404.html';
  location.replace('/' + lang + '/' + file);
})();
