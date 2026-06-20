// Root language redirect. Kept in an EXTERNAL file on purpose: the site CSP
// (script-src 'self' …, no 'unsafe-inline') blocks inline scripts, so the
// redirect must live here to run in production. A remembered choice wins;
// otherwise the browser language decides. French is primary, so anything that
// is not explicitly English resolves to French.
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
  location.replace(lang + '/index.html');
})();
