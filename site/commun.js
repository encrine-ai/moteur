/* Fonctions partagées entre l'application (app.js) et la vue d'impression
 * (imprimer.html). Les données de la classe — calendrier, milieux, documents —
 * viennent de classe.js, fabriqué depuis classe.yml (scripts/classe.py).
 */
var GS = (function () {
  'use strict';

  var C = CLASSE;
  var CAL = C.calendrier;
  var THEMES = C.periodes.map(function (p) { return p.milieu; });
  // Icône de chaque milieu (sprite charte/icones.svg) ; la couleur de la
  // période vient de la charte (--p1 … --p5).
  var ICONES_MILIEU = C.periodes.map(function (p) { return p.icone; });
  var DAY = 86400000;

  var DOCS = C.documents.map(function (doc) {
    return { id: doc.id, titre: doc.titre, ic: doc.icone, md: doc.md, groupe: doc.groupe || null,
             desc: doc.desc, parPeriode: !!doc.par_periode, fiches: doc.fiches };
  });
  // Préfixe des fichiers téléchargés : « GS-2026-2027 ».
  var PREFIXE = C.niveau.code + '-' + C.annee;

  function d(iso) { return new Date(iso + 'T00:00:00Z'); }
  function veille(iso) { return new Date(d(iso).getTime() - DAY); }
  function fmt(date, opts) { return new Intl.DateTimeFormat('fr-FR', Object.assign({ timeZone: 'UTC' }, opts)).format(date); }
  function fmtLong(date) { return fmt(date, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
  function fmtCourt(date) { return fmt(date, { weekday: 'short', day: 'numeric', month: 'short' }); }
  function semaines(a, b) { return Math.round(((b.getTime() - a.getTime()) / DAY + 1) / 7); }

  function periodes(zone) {
    return [
      { n: 1, debut: d(CAL.rentree), fin: veille(CAL.toussaint.debut) },
      { n: 2, debut: d(CAL.toussaint.reprise), fin: veille(CAL.noel.debut) },
      { n: 3, debut: d(CAL.noel.reprise), fin: veille(CAL.hiver[zone].debut) },
      { n: 4, debut: d(CAL.hiver[zone].reprise), fin: veille(CAL.printemps[zone].debut) },
      { n: 5, debut: d(CAL.printemps[zone].reprise), fin: d(CAL.fin) }
    ].map(function (p) { p.sem = semaines(p.debut, p.fin); return p; });
  }

  function badgeText(p, zone) {
    return 'Zone ' + zone + ' : du ' + fmtCourt(p.debut) + ' au ' + fmtCourt(p.fin) + ' ' + fmt(p.fin, { year: 'numeric' }) + ' · ' + p.sem + ' semaines';
  }

  function annoteTitres(racine, zone) {
    var ps = periodes(zone);
    var re = /P[ée]riode\s*([1-5])/i;
    racine.querySelectorAll('h1, h2, h3').forEach(function (h) {
      var m = h.textContent.match(re);
      if (!m) return;
      var p = ps[parseInt(m[1], 10) - 1];
      var badge = h.querySelector('.zone-badge');
      if (!badge) { badge = document.createElement('span'); badge.className = 'zone-badge'; h.appendChild(badge); }
      badge.textContent = badgeText(p, zone);
    });
  }

  function nettoieMarkdown(md) {
    return md
      .replace(/\[([^\]]+)\]\((?:\.\/)?[^)]+\.md\)/g, '$1')
      .replace(/<div id="calendrier-zones">[\s\S]*?<\/div>/g, '')
      .replace(/<p id="zone-hint"[^>]*><\/p>/g, '');
  }

  return {
    CLASSE: C, CAL: CAL, THEMES: THEMES, ICONES_MILIEU: ICONES_MILIEU, DOCS: DOCS, PREFIXE: PREFIXE,
    d: d, veille: veille, fmt: fmt, fmtLong: fmtLong, fmtCourt: fmtCourt,
    periodes: periodes, badgeText: badgeText, annoteTitres: annoteTitres,
    nettoieMarkdown: nettoieMarkdown
  };
})();
