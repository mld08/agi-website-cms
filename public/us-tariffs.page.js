// ---- Tariff data (USTR, April 2025) -------------------------------------
const TARIFFS = [
  { name: 'Lesotho',        lat: -29.6, lng: 28.2, rate: 50 },
  { name: 'Madagascar',     lat: -19.4, lng: 46.9, rate: 47 },
  { name: 'Mauritius',      lat: -20.3, lng: 57.6, rate: 40 },
  { name: 'Botswana',       lat: -22.3, lng: 24.7, rate: 38 },
  { name: 'Angola',         lat: -11.2, lng: 17.9, rate: 32 },
  { name: 'South Africa',   lat: -29.0, lng: 24.7, rate: 31 },
  { name: 'Algeria',        lat: 28.0,  lng: 2.6,  rate: 30 },
  { name: 'Tunisia',        lat: 34.0,  lng: 9.5,  rate: 28 },
  { name: "Côte d'Ivoire",  lat: 7.5,   lng: -5.5, rate: 21 },
  { name: 'Namibia',        lat: -22.6, lng: 17.1, rate: 21 },
  { name: 'Nigeria',        lat: 9.1,   lng: 8.7,  rate: 14 },
  { name: 'Kenya',          lat: 0.2,   lng: 37.9, rate: 10 },
  { name: 'Egypt',          lat: 26.8,  lng: 30.8, rate: 10 },
  { name: 'Ethiopia',       lat: 9.1,   lng: 40.5, rate: 10 }
];
function rateColor(r) {
  if (r >= 40) return '#B22F28';
  if (r >= 30) return '#DD8728';
  if (r >= 20) return '#E8B936';
  return '#5E6B27';
}

// ---- Leaflet proportional-symbol map ------------------------------------
(function initMap() {
  const el = document.getElementById('tariff-map');
  if (!el || !window.L) return;
  const map = L.map(el, {
    center: [3, 19], zoom: 3, minZoom: 2, maxZoom: 6,
    scrollWheelZoom: false, zoomControl: true, attributionControl: true
  });
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd', maxZoom: 19
  }).addTo(map);
  TARIFFS.forEach(c => {
    const col = rateColor(c.rate);
    L.circleMarker([c.lat, c.lng], {
      radius: 5 + c.rate * 0.32,
      color: '#ffffff', weight: 1.5, fillColor: col, fillOpacity: 0.85
    }).addTo(map)
      .bindTooltip(`<strong>${c.name}</strong><br>${c.rate}% tariff`, {
        direction: 'top', offset: [0, -4], className: 'tariff-tip'
      });
  });
  setTimeout(() => map.invalidateSize(), 250);
})();

// ---- Chart.js horizontal bar --------------------------------------------
(function initChart() {
  const ctx = document.getElementById('tariffChart');
  if (!ctx || !window.Chart) return;
  const data = TARIFFS.filter(c => c.rate >= 21).sort((a, b) => b.rate - a.rate);
  const styles = getComputedStyle(document.documentElement);
  const ink = styles.getPropertyValue('--ink-2').trim() || '#3A352A';
  const line = styles.getPropertyValue('--line').trim() || '#E2D9BF';
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(c => c.name),
      datasets: [{
        data: data.map(c => c.rate),
        backgroundColor: data.map(c => rateColor(c.rate)),
        borderRadius: 3, barThickness: 22, maxBarThickness: 26
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (i) => i.parsed.x + '% reciprocal tariff' } }
      },
      scales: {
        x: {
          beginAtZero: true, max: 55,
          ticks: { color: ink, font: { family: 'Poppins', size: 11 }, callback: (v) => v + '%' },
          grid: { color: line }
        },
        y: {
          ticks: { color: ink, font: { family: 'Poppins', size: 13, weight: '600' } },
          grid: { display: false }
        }
      }
    }
  });
})();

// TOC active state on scroll
const tocLinks = document.querySelectorAll('.toc-list a');
const headings = [...document.querySelectorAll('.prose h2, .prose [id]')].filter(el => el.id);
const onScroll = () => {
  const sy = window.scrollY + 200;
  let current = headings[0]?.id;
  for (const h of headings) {
    if (h.offsetTop <= sy) current = h.id;
  }
  tocLinks.forEach(l => {
    l.classList.toggle('active', l.getAttribute('href') === '#' + current);
  });
};
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Share buttons
(function () {
  const url = 'https://africagovernanceinstitute.org/us-tariffs.html';
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
