# Blueprint — Vidéo de présentation de site (format « IAG »)

> **À quoi sert ce fichier.** Je (le client) ai un site web terminé et je veux une vidéo
> de présentation verticale dans le même style que celle réalisée pour l'Africa Governance
> Institute. **Joins ce fichier au projet et suis-le pour reconstruire la même structure de
> vidéo, adaptée à mon nouveau site.** Ne réinvente pas le format : il est décrit ici en
> entier. Demande-moi seulement ce que ce document ne précise pas (logo, couleurs, liste de
> services, musique).
>
> **Deux choses changent à chaque site, par conception :**
> 1. **La musique** sera différente à chaque fois. À toi de choisir un nouveau morceau et de
>    **re-caler toute la cinétique dessus** (BPM → `BEAT`, downbeat → `AUDIO_START`, volume,
>    fades) — voir §7. Ne réutilise pas l'ancienne piste par défaut.
> 2. **Le branding** suit **principalement la charte du site conçu** (logo, couleurs, typo,
>    accent). Le fond blanc et la structure restent ; tout le reste s'habille aux couleurs du
>    site. Le « reel Studio Karda » d'intro reste la signature de l'agence.

---

## 1. Le concept en une phrase

Une vidéo verticale **1080×1920, 30 fps, ~27 s**, fond **blanc**, qui ouvre sur un **hook
« machine à sous »** (les services du studio défilent et se verrouillent sur « Développement
Web »), enchaîne sur une **révélation cinétique du logo du site**, fait un **tour des pages
réelles** du site (captures qui défilent dans un cadre navigateur), montre une **scène
responsive + atouts**, et se termine par un **outro logo + URL**. Tout est **calé sur le beat**
de la musique, sans pulsation décorative.

L'intention : prouver en quelques secondes que le site est **réel, soigné, responsive et
bilingue**, avec une entrée qui retient l'attention dans les 2 premières secondes (durée
d'attention avant un swipe).

---

## 2. Architecture technique (3 briques réutilisables)

La vidéo n'est **pas un fichier .mp4** : c'est une **animation React/HTML** rendue image par
image. Trois fichiers, dont deux se réutilisent **tels quels** d'un site à l'autre :

| Fichier | Rôle | Réutilisable ? |
|---|---|---|
| `video/animations.jsx` | Moteur de timeline : `<Stage>` (scaling, scrubber, play/pause, ←/→, persistance), `<Sprite>` (fenêtres temporelles), `TimelineContext`, `Easing`. **Agnostique du contenu.** | **Verbatim** — copie-le sans rien changer. |
| `video/scenes.jsx` | Le contenu : l'objet de timing `T`, la liste `TOUR`, les scènes, le système visuel. | **À adapter** par site. |
| `IAG Presentation Video.html` | La page hôte : charge React/Babel pinned + les 2 JSX, gère la musique (start, volume, fades, boucle), le sélecteur de style. | À adapter (constantes audio + nom). |
| `export/` | Pipeline d'export MP4 (capture parallèle Playwright → ffmpeg). | **Verbatim** — voir §9. |

Charge React 18.3.1 + Babel standalone avec les balises **pinned + integrity** habituelles,
puis `animations.jsx` puis `scenes.jsx` en `type="text/babel"`. Les composants s'exportent sur
`window` (`Movie`, `STYLES`, `T`, `TOUR`, `TimelineContext`) — c'est ce que le harness d'export
consomme. Ne casse pas ces exports.

---

## 3. Le modèle de timeline (tout est calé au beat)

Une seule constante pilote le rythme :

```js
const BEAT = 0.397;   // période du beat = 60 / BPM (ici ~151 BPM)
```

Les bornes de scènes sont exprimées en **multiples de BEAT**, pas en secondes arbitraires :

```js
const T = {
  kardaS: 0,        kardaE: 8 * BEAT,    // reel "machine à sous" : spin lisible ~2s (lock au beat 5) + tenue
  openS: 8 * BEAT,  openE: 19 * BEAT,    // révélation cinétique du logo (étalée sur 11 beats, pas de rush)
  tourS: 19 * BEAT,
};
// le tour calcule start/end par page à partir de leurs durées (voir §6)
T.respS = T.tourE;   T.respE = T.respS + 4.9;   // scène responsive
T.outroS = T.respE;  T.outroE = T.outroS + 3.4; // outro
T.total = T.outroE;
```

**Règle d'or :** la musique démarre sur un **downbeat fort**, et ce downbeat tombe pile sur le
hook (`openS`). Donc on aligne l'audio à la vidéo, pas l'inverse (voir §7).

---

## 4. Séquence des scènes

| # | Scène | Durée | Ce qui se passe |
|---|---|---|---|
| 0 | **Reel Studio Karda** (`OpenerScene` partie reel) | ~2 s | Les ~10 services du studio défilent comme une machine à sous, **lisibles** (flou léger seulement), décélèrent (`easeOutQuart`) et se **verrouillent sur « Développement Web »** au beat 5, validé d'un check. Label « WELCOME BACK ». |
| 1 | **Révélation logo du site** (`OpenerScene`) | ~4 s | « NOUVEAU » / « SITE » claquent sur 2 beats, le logo du site s'impose au beat-slam, puis le titre apparaît ligne par ligne sur les beats suivants. |
| 2 | **Tour des pages** (`TourScene`) | ~12 s | Pour chaque page : une **capture longue** (strip) défile dans un cadre navigateur, avec un index (01…), un label et le chemin d'URL. Coupe nette à chaque page, calée au beat. |
| 3 | **Responsive + atouts** (`ResponsiveScene`) | ~4,9 s | Maquette navigateur + téléphone (mêmes pages en mobile), centrées, et un cluster d'**atouts** avec pastilles d'icônes colorées (Responsive · Haute performance · Bilingue · Newsletter · CMS…). |
| 4 | **Outro** (`OutroScene`) | ~3,4 s | Logo du site + URL (« Visiter le site. ») sur fond blanc. |

L'assemblage dans `Movie` : `Backdrop` (blobs de marque qui dérivent) → `OpenerScene` →
`TourScene` → `ResponsiveScene` → `OutroScene`, le tout sous un `StyleContext.Provider`.

---

## 5. Système visuel

- **Style « Blanc »** : `bg #FFFFFF`, encre sombre, point d'accent bleu, + 2 teintes de glow de
  marque pour le backdrop. (Le code garde la structure d'un objet `STYLES` ; un seul style suffit.)
- **Entrées cinétiques** (`kin()`): chaque élément arrive avec **blur → net + scale 1.18 → 1 +
  rise**, easing `easeOutExpo`, parfois un **wipe** (`clipPath inset`). C'est la signature du look.
- **Caméra** (`Scene`): léger **push** continu (zoom lent) + **sortie** rapide (scale-up + fade).
- **Backdrop** : 2 blobs radiaux de couleur de marque qui dérivent en `sin/cos` + grain léger.
- **PAS de pulsation au beat** sur le contenu (pas de zoom/scale rythmique audio-réactif). Le
  rythme se ressent par les **entrées calées sur les beats**, pas par une « respiration ». C'est
  un choix : ça reste premium, pas « boom-boom ».

---

## 6. Conventions d'assets (les « strips » du tour)

Le tour défile des **captures verticales longues** des pages réelles, pas des screenshots
courts. Convention dans `assets-video/` :

```js
const TOUR = [
  { src:'assets-video/strip-home.png',     h:2700, idx:'01', label:'Accueil',    path:'monsite.org',            dur:2.3 },
  { src:'assets-video/strip-programs.png', h:2160, idx:'02', label:'…',           path:'/…',                     dur:2.3 },
  // … une entrée par page
];
```

- **Largeur de capture : 909 px** (c'est la largeur du viewport de prévisualisation desktop).
  Toutes les strips ont cette largeur ; `h` est la hauteur réelle de la strip.
- **Comment capturer une strip** : ouvrir la page, **neutraliser le header sticky**
  (`position:absolute` ou `display:none`), puis capturer la page par **tranches de 540 px** en
  translatant le `<body>` (`transform: translateY(-540px)`, `-1080`, …) — la capture DOM rend
  depuis le haut, donc on décale le contenu, on ne « scrolle » pas. Empiler les tranches en une
  image verticale (canvas) et sauver en `assets-video/strip-<page>.png`.
- **Mobile** : forcer le layout mobile (rejouer les règles du breakpoint ou viewport étroit),
  capturer le hero propre pour la scène responsive.
- **Garder les strips à jour** : si une page change, **recapturer sa strip** (même chemin, même
  format) — la vidéo la reprend automatiquement.

---

## 7. Audio (calage + douceur)

```js
const AUDIO_START = <downbeat> - openS;   // le downbeat tombe sur le hook IAG
const BASE_VOL    = 0.465;                // volume posé (−25% d'un mix brut), ne grince pas
const FADE_IN     = 0.06;                 // quasi nul : juste pour éviter le "pop", pas de rampe audible
const FADE_OUT    = 1.8;                  // fade de fin propre avant la boucle
```

Méthode pour un nouveau morceau :
1. **Analyser la piste** (RMS / onsets) pour trouver le **BPM** → `BEAT = 60/BPM`, et repérer un
   **downbeat fort** dans la section qui sonne le mieux.
2. Poser `AUDIO_START = downbeat − openS` pour que la première grosse frappe tombe sur le hook.
3. Volume bas (~0.45–0.5), fade-in quasi nul, fade-out ~1.8 s.
4. **Pas de couche de percussions ajoutée** par défaut (on a retiré le « sabar ») : musique seule.

---

## 8. Copywriting (règles du projet)

- **Zéro tiret cadratin (—)** dans les textes affichés. Titres courts et factuels.
- Pas de tournures « IA » (rule-of-three, titres poétiques).
- Si le site est **bilingue**, la vidéo suit **une seule langue** (cohérente entre cadre desktop
  et mobile). Labels du tour dans cette langue.

---

## 9. Export MP4 (ne pas réinventer)

Le dossier `export/` rend la vidéo en **MP4 1080×1920 30 fps H.264+AAC**, fond blanc, vraie BO.
Pipeline déterministe (un harness `render.html` expose `window.__renderAt(t)` qui dessine
l'instant exact), **capture parallèle** sur tous les cœurs CPU, reprenable.

```bash
bash export/setup.sh      # une fois : Playwright Chromium + check ffmpeg
bash export/make_mp4.sh   # → export/out/IAG-Presentation-Video.mp4
```

Les constantes audio en haut de `make_mp4.sh` **doivent refléter** celles du HTML (§7).
Détails dans `export/README.md`. **Ne pas réécrire de script de capture.**

---

## 10. Checklist d'adaptation pour un NOUVEAU site

Pour transformer ce format pour mon prochain site, à faire dans cet ordre :

1. **Copier le moteur** : `video/animations.jsx` (verbatim) + `export/` (verbatim).
2. **Logo & marque** : remplacer `assets-video/logo.png` ; régler les couleurs du style `STYLES`
   (accent, glows) sur la charte du site. Garder le fond blanc sauf demande contraire.
3. **Reel d'intro** : remplacer la liste de services par ceux du studio (ou par un autre hook
   pertinent au site) ; choisir le mot sur lequel le reel se verrouille.
4. **Pages du tour** : recapturer une **strip par page** réelle du nouveau site (§6) et remplir
   `TOUR` (src, h, idx, label, path, dur). 4–6 pages, c'est le bon nombre.
5. **Scène responsive** : recapturer le hero mobile ; ajuster la liste d'atouts (Responsive,
   perf, langues, et toute feature réelle : Newsletter, CMS, e-commerce…).
6. **Outro** : URL et logo du site.
7. **Musique** : choisir un morceau, l'analyser, poser `BEAT`, `AUDIO_START`, volume, fades (§7).
8. **Vérifier le calage** : capturer l'intro frame par frame et confirmer que chaque élément
   tombe sur son beat ; ajuster les `delay` (en multiples de `BEAT`) si besoin.
9. **Langue & copy** : appliquer les règles §8.
10. **Exporter** : §9.

Ce qui **ne change pas** d'un site à l'autre : le moteur, le pipeline d'export, le système
d'entrées cinétiques, le modèle « tout en multiples de BEAT », la convention des strips.
