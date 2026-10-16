// /cfghana language redirect. External file because the site CSP blocks inline scripts.
// Browser language decides: fr* goes to French, everything else to English.
(function () {
  var langs;
  try { langs = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || '']; } catch (e) { langs = []; }
  var fr = String(langs[0] || '').toLowerCase().indexOf('fr') === 0;
  location.replace((fr ? 'fr/cfghana.html' : 'en/cfghana.html') + location.search + location.hash);
})();
