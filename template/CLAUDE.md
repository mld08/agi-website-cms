# Project rules — Suite Site IAG (Africa Governance Institute)

## Copywriting
- **Zero em dashes (—) anywhere in site copy.** Use commas, colons, periods or restructure the sentence. En dashes inside year ranges (2005–2012) are fine.
- No "AI-flavored" copy: no rule-of-three flourishes ("Researchers, builders and advocates"), no poetic section titles ("An internship that became a calling"), no "X, the Y way", no "quiet diplomacy"-style phrases. Titles stay factual and short.
- **No filler lede under a heading.** Never add a descriptive `<p class="lead">` (or equivalent intro paragraph) under an `<h1>`/`<h2>` whose only job is to restate or describe the page/section. If a heading needs no real, substantive supporting text, leave it alone. Only keep an intro paragraph when it carries actual content (a definition, named facts, a concrete summary), never to describe the page.
- The English (`en/`) tree is the editorial source of truth; the French (`fr/`) tree is its hand-maintained translation.

## Translation (two static trees, no runtime engine)
- The site ships TWO fully hand-written language trees: `en/*.html` and `fr/*.html`. There is NO runtime translation: the old `i18n.js` + `fr-dict.js` machinery and the `window.claude.complete` call were removed (they were dead code, loaded by no page).
- **Any content change must be applied to BOTH `en/` and the matching `fr/` page.** Edit the English page, then mirror the change in French.
- Job titles carry gender in French and the team is mostly women (e.g. "Director of Programs" → "Directrice des Programmes" for Maty Ndiaye). Translate roles with the correct gender.
- The language switch is just cross-links between `/en/` and `/fr/`; the chosen locale is remembered in localStorage under `agi-locale` and used by the root `index.html` redirect.

## Team facts
- Maty Ndiaye is DIRECTOR OF PROGRAMS and Head of the Youth & Migration Cluster (a woman).
- Dr. Abdoulie Janneh holds two titles, both shown: Director General AND Chairman of the Board ("Directeur Général et Président du Conseil d'administration").
- Coumba Sambe (Program Analyst and International Relations Specialist / "Analyste de Programme et Spécialiste en Relations Internationales") is displayed as "Coumba Sambe", NOT "Coumba Nara Sambe". The page file/slug stays team-coumba-sambe.html. She is distinct from Ndeye Coumba Diedhiou (Chief, Operations & Resource Management).
- Sirandou Sall (Executive Assistant / "Assistante Administrative") has NO dedicated page; her card on about.html is intentionally non-clickable but DOES swap to her full-pose photo on hover (assets/team/sirandou-sall-full.jpg).
- Ndjibou Cisse (Finance Officer / "Chargée des finances", a woman, card 08) and Abdou Lahat Thiam (Driver / "Chauffeur", a man, card 09) are NO-page support staff: non-clickable tm-static cards on about.html only. Ndjibou has a single photo (no hover); Lahat has a hover swap to assets/team/abdou-lahat-thiam-full.jpg.
- Team photos live in `assets/team/` (optimized ≤200 KB). The raw originals (uploads/Web Choice zip) were deleted on request; ask the user if a re-crop from source is ever needed.

## Structure
- "Who We Are" = `about.html` (linked in navbar site-wide). Member pages: `team-*.html`, sharing `member.css`; each sets `--accent` on `<body>`.

## Presentation video
The presentation video and its MP4 export pipeline were removed from this repo when the site went to hosting (only site files are kept here). The reusable spec to rebuild it lives in `Presentation Video - Blueprint.md`; the full engine (`video/`, `export/`) is in the project backup zip.
