/* Application de consultation de la classe.
 * Les données de la classe viennent de classe.yml (via classe.js) ; les
 * fonctions partagées (calendrier, documents) sont dans commun.js (GS).
 * L'apparence suit la charte du thème de la classe (charte/charte.css).
 */
(function () {
  'use strict';

  var etat = { doc: 'accueil' };
  var cacheMd = {};

  /* Un point d'accroche du thème : un élément vide, que le thème de la classe
   * peut remplir d'un motif (skill charte-graphique). */
  function orne(nom) {
    return '<span class="orne" data-orne="' + nom + '" aria-hidden="true"></span>';
  }

  function icone(nom) {
    return '<svg class="ic" aria-hidden="true"><use href="charte/icones.svg#i-' + nom + '"/></svg>';
  }

  function pastille(n) {
    return '<span class="pastille" data-periode="' + n + '">' + n + '</span>';
  }

  /* ——— Navigation ——— */
  function construireMenu() {
    var nav = document.getElementById('sidebar');
    var html = '';
    var groupeCourant;
    GS.DOCS.forEach(function (doc, i) {
      if (i === 0 || doc.groupe !== groupeCourant) {
        if (i > 0) html += '</div>';
        groupeCourant = doc.groupe;
        html += '<div class="menu-groupe">' + (groupeCourant ? '<div class="groupe">' + groupeCourant + '</div>' : '');
      }
      var marque = doc.fiches ? pastille(doc.fiches) : icone(doc.ic);
      var titre = doc.fiches ? GS.THEMES[doc.fiches - 1] : doc.titre;
      html += '<a href="#/' + doc.id + '" data-doc="' + doc.id + '">' + marque + '<span>' + titre + '</span></a>';
    });
    nav.innerHTML = html + '</div>';
  }

  function majMenuActif() {
    document.querySelectorAll('.sidebar a').forEach(function (a) {
      var actif = a.dataset.doc === etat.doc;
      a.classList.toggle('actif', actif);
      if (actif) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }

  /* ——— Rendu des documents ——— */
  function chargeMd(doc) {
    if (cacheMd[doc.md]) return Promise.resolve(cacheMd[doc.md]);
    return fetch(doc.md).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.text();
    }).then(function (t) { cacheMd[doc.md] = t; return t; });
  }

  function rendDocument(doc) {
    var contenu = document.getElementById('contenu');
    contenu.className = 'contenu';
    contenu.dataset.composant = 'document';
    if (doc.fiches) contenu.dataset.periode = doc.fiches; else delete contenu.dataset.periode;
    contenu.innerHTML = '<p class="chargement">Chargement…</p>';
    chargeMd(doc).then(function (md) {
      contenu.innerHTML = marked.parse(GS.nettoieMarkdown(md));
      GS.annoteTitres(contenu);
      window.scrollTo(0, 0);
    }).catch(function () {
      contenu.innerHTML = '<p>Impossible de charger ce document. Vérifiez votre connexion puis rechargez la page.</p>';
    });
  }

  function periodeDuJour(ps) {
    var auj = new Date();
    var t = Date.UTC(auj.getFullYear(), auj.getMonth(), auj.getDate());
    for (var i = 0; i < ps.length; i++) {
      if (t >= ps[i].debut.getTime() && t <= ps[i].fin.getTime()) return ps[i];
    }
    return null;
  }

  function prochainePeriode(ps) {
    var auj = new Date();
    var t = Date.UTC(auj.getFullYear(), auj.getMonth(), auj.getDate());
    for (var i = 0; i < ps.length; i++) if (ps[i].debut.getTime() > t) return ps[i];
    return null;
  }

  /* Le document de la période n (celui qui porte ses fiches), ou l'accueil. */
  function docDe(n) {
    var doc = GS.DOCS.find(function (x) { return x.fiches === n; });
    return doc ? doc.id : 'accueil';
  }

  /* La frise de l'année : cinq bandes, larges de leur nombre de semaines. */
  function frise(ps, pj, prochaine) {
    var total = ps.reduce(function (s, p) { return s + p.sem; }, 0);
    return '<ol class="frise" data-composant="frise" aria-label="Les cinq périodes de l’année, zone ' + GS.ZONE + '">' +
      ps.map(function (p) {
        var enCours = pj && pj.n === p.n;
        var aVenir = !pj && prochaine && prochaine.n === p.n;
        return '<li class="frise-periode' + (enCours || aVenir ? ' en-cours' : '') + '" data-periode="' + p.n + '" style="flex-grow:' + p.sem + '">' +
          '<a href="#/' + docDe(p.n) + '">' +
          '<span class="frise-bande">' + orne('frise') + icone(GS.ICONES_MILIEU[p.n - 1]) + '<span class="frise-num">P' + p.n + '</span></span>' +
          '<span class="frise-milieu">' + GS.THEMES[p.n - 1] + '</span>' +
          '<span class="frise-dates">' + GS.fmtCourt(p.debut) + ' → ' + GS.fmtCourt(p.fin) + '</span>' +
          '<span class="frise-sem">' + p.sem + ' semaines</span>' +
          (enCours ? '<span class="frise-ici">' + icone('map-pin') + 'Nous y sommes</span>' : '') +
          (aVenir ? '<span class="frise-ici">' + icone('map-pin') + 'Reprise le ' + GS.fmtCourt(p.debut) + '</span>' : '') +
          '</a></li>';
      }).join('') + '</ol>' +
      '<p class="frise-total">' + total + ' semaines de classe, du ' + GS.fmtLong(ps[0].debut) + ' au ' + GS.fmtLong(ps[4].fin) + '.</p>';
  }

  /* Les cahiers de la période n, tels que classe.yml les déclare (materiel). */
  function cahiersDe(n) {
    return GS.CLASSE.materiel.filter(function (m) { return m.periodes.indexOf(n) !== -1; });
  }

  function pdfDe(m, n) { return m.pdf.replace('{n}', n); }

  /* Le matériel à imprimer d'une période : ses cahiers. */
  function materiel(n, statut) {
    var cahiers = cahiersDe(n).map(function (m) {
      return [m.icone, m.titre, m.desc, pdfDe(m, n), GS.CLASSE.niveau.code + '-' + (m.fichier || m.nom) + '-periode-' + n + '.pdf'];
    });
    return '<section class="materiel' + (statut ? ' en-cours' : '') + '" data-composant="materiel" data-periode="' + n + '">' +
      '<header class="materiel-tete">' + orne('materiel') + icone(GS.ICONES_MILIEU[n - 1]) +
      '<div><div class="materiel-num">Période ' + n + (statut ? ' · ' + statut : '') + '</div>' +
      '<h3>' + GS.THEMES[n - 1] + '</h3></div></header>' +
      '<ul class="materiel-liste">' + cahiers.map(function (c) {
        return '<li><a href="' + c[3] + '" download="' + c[4] + '">' + icone(c[0]) +
          '<span><strong>' + c[1] + '</strong><small>' + c[2] + '</small></span>' + icone('download') + '</a></li>';
      }).join('') + '</ul></section>';
  }

  var NOMBRES = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix'];
  function nombre(k) { return NOMBRES[k] || String(k); }

  /* « Pour chaque période, quatre cahiers en A4 : à photocopier (entraînement,
   * évaluation) ou à découper et plastifier (imagier, cartes-corpus). » */
  function noteMateriel(sortes, partout) {
    var papier = { entrainement: 'photocopier', evaluation: 'photocopier', imagier: 'plastifier', 'cartes-corpus': 'plastifier' };
    var aPhotocopier = sortes.filter(function (m) { return papier[m.cle] === 'photocopier'; });
    var aPlastifier = sortes.filter(function (m) { return papier[m.cle] === 'plastifier'; });
    var noms = function (ms) { return ms.map(function (m) { return m.titre.toLowerCase(); }).join(', '); };
    var usages = [];
    if (aPhotocopier.length) usages.push('à photocopier (' + noms(aPhotocopier) + ')');
    if (aPlastifier.length) usages.push('à découper et plastifier (' + noms(aPlastifier) + ')');
    var k = sortes.length;
    return (partout ? 'Pour chaque période, ' : 'Pour les périodes prêtes, ') +
      nombre(k) + (k > 1 ? ' cahiers' : ' cahier') + ' en A4 : ' + usages.join(' ou ') + '.';
  }

  function rendAccueil() {
    var contenu = document.getElementById('contenu');
    contenu.className = 'contenu accueil';
    contenu.dataset.composant = 'accueil';
    delete contenu.dataset.periode;
    var ps = GS.periodes();
    var pj = periodeDuJour(ps);
    var C = GS.CLASSE;
    // « Pont de l’Ascension : pas de classe du jeudi 6 au dimanche 9 mai … »
    var ponts = C.calendrier.ponts.map(function (p) {
      return p.nom + ' : pas de classe du ' + GS.fmt(GS.d(p.du), { weekday: 'long', day: 'numeric' }) +
        ' au ' + GS.fmt(GS.d(p.au), { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }) + '. ';
    }).join('');
    var vac = [
      ['Toussaint', GS.CAL.toussaint], ['Noël', GS.CAL.noel],
      ['Hiver', GS.CAL.hiver], ['Printemps', GS.CAL.printemps]
    ].map(function (v) {
      return '<li><strong>' + v[0] + '</strong><span>du ' + GS.fmtCourt(GS.d(v[1].debut)) + ' au ' + GS.fmtCourt(GS.veille(v[1].reprise)) +
        '</span><span class="reprise">reprise le ' + GS.fmtCourt(GS.d(v[1].reprise)) + '</span></li>';
    }).join('');

    // Le matériel commence par la période en cours, ou par la prochaine
    // pendant les vacances.
    var tete = pj || prochainePeriode(ps);
    var ordre = ps.map(function (p) { return p.n; });
    if (tete) ordre = ordre.slice(tete.n - 1).concat(ordre.slice(0, tete.n - 1));
    // Seules les périodes qui ont des cahiers : rien n'est annoncé qui n'existe pas.
    ordre = ordre.filter(function (n) { return cahiersDe(n).length; });
    var sortes = C.materiel.filter(function (m) { return m.periodes.length; });

    var groupes = {};
    GS.DOCS.filter(function (doc) { return doc.md && !doc.fiches; }).forEach(function (doc) {
      (groupes[doc.groupe] = groupes[doc.groupe] || []).push(doc);
    });
    var docs = Object.keys(groupes).map(function (g) {
      return '<div class="docs-groupe" data-composant="documents"><h3>' + g + '</h3><ul class="docs">' + groupes[g].map(function (doc) {
        return '<li><a href="#/' + doc.id + '">' + icone(doc.ic) + '<span><strong>' + doc.titre + '</strong><small>' + doc.desc + '</small></span></a></li>';
      }).join('') + '</ul></div>';
    }).join('');

    contenu.innerHTML =
      '<div class="accueil-tete" data-composant="accueil-tete">' + orne('accueil') +
      '<p class="surtitre">' + C.niveau.libelle + ' · année ' + C.annee + '</p>' +
      '<h1>' + C.projet + '</h1>' +
      '<p class="chapo">' + C.accroche + '</p>' +
      '</div>' +
      '<section class="bloc" data-composant="bloc" data-bloc="annee"><div class="bloc-tete"><h2>L’année en ' + nombre(ps.length) + ' ' + (C.periodes_nom || 'périodes') + '</h2><span class="zone-badge">zone ' + GS.ZONE + '</span></div>' +
      frise(ps, pj, tete) +
      '<ul class="vacances">' + vac + '</ul>' +
      '<p class="note">' + ponts + 'Les dates sont celles de la zone ' + GS.ZONE + ' ; ' +
      'chaque document se télécharge en PDF prêt à imprimer, dates comprises.</p></section>' +
      (ordre.length ? '<section class="bloc" data-composant="bloc" data-bloc="materiel"><div class="bloc-tete"><h2>À imprimer pour la classe</h2></div>' +
      '<p class="note">' + noteMateriel(sortes, sortes.every(function (m) { return m.periodes.length === ps.length; })) + '</p>' +
      '<div class="materiels">' + ordre.map(function (n) { return materiel(n, tete && tete.n === n ? (pj ? 'en cours' : 'à venir') : ''); }).join('') + '</div></section>' : '') +
      '<section class="bloc" data-composant="bloc" data-bloc="documents"><div class="bloc-tete"><h2>Mes documents</h2></div>' + docs + '</section>';
    window.scrollTo(0, 0);
  }

  function rend() {
    var doc = GS.DOCS.find(function (x) { return x.id === etat.doc; }) || GS.DOCS[0];
    etat.doc = doc.id;
    majMenuActif();
    document.getElementById('fil').textContent = doc.groupe ? doc.groupe + ' › ' + doc.titre : '';
    document.querySelector('.toolbar').hidden = !doc.md;

    var btnPdf = document.getElementById('btn-pdf');
    if (doc.md) {
      btnPdf.hidden = false;
      btnPdf.href = 'pdf/' + doc.id + '.pdf';
      btnPdf.setAttribute('download', GS.PREFIXE + '-' + doc.id + '.pdf');
    } else {
      btnPdf.hidden = true;
    }
    // Les cahiers de la période : un bouton par cahier déclaré, aucun pour les autres.
    var boutons = { evaluation: 'btn-fiches', entrainement: 'btn-entrainement', imagier: 'btn-imagier', 'cartes-corpus': 'btn-corpus' };
    var presents = doc.fiches ? cahiersDe(doc.fiches) : [];
    Object.keys(boutons).forEach(function (cle) {
      var el = document.getElementById(boutons[cle]);
      var m = presents.find(function (x) { return x.cle === cle; });
      el.hidden = !m;
      if (m) {
        el.href = pdfDe(m, doc.fiches);
        el.setAttribute('download', GS.PREFIXE + '-' + m.nom + '-periode-' + doc.fiches + '.pdf');
      }
    });

    var pp = document.getElementById('periodes-print');
    if (doc.parPeriode) {
      pp.hidden = false;
      pp.innerHTML = '<span>' + icone('printer') + 'L’extrait d’une période, pour l’afficher en classe :</span> ' +
        GS.THEMES.map(function (_, i) { return i + 1; }).map(function (n) {
          return '<a data-periode="' + n + '" href="pdf/' + doc.id + '-periode-' + n + '.pdf" ' +
            'download="' + GS.PREFIXE + '-' + doc.id + '-periode-' + n + '.pdf">' + pastille(n) + GS.THEMES[n - 1] + '</a>';
        }).join(' ');
    } else {
      pp.hidden = true;
    }

    if (doc.md) rendDocument(doc); else rendAccueil();
    fermeMenu();
  }

  /* ——— Menu sur petit écran ——— */
  function fermeMenu() {
    document.getElementById('sidebar').classList.remove('ouvert');
    document.getElementById('menu-toggle').setAttribute('aria-expanded', 'false');
  }

  /* ——— Démarrage ——— */
  // Les textes de la classe dans l'en-tête, le titre et le pied de page.
  function habilleClasse() {
    var C = GS.CLASSE;
    document.title = C.nom + ' ' + C.annee + ' · ' + C.projet;
    document.querySelector('.marque-titre').textContent = C.nom;
    document.querySelector('.marque-sous').textContent = C.annee + ' · ' + C.sous_titre;
    document.querySelector('.pied').textContent = C.conformite + ' Dates des vacances : calendrier scolaire officiel ' + C.annee + ', zone ' + GS.ZONE + '.';
  }

  document.addEventListener('DOMContentLoaded', function () {
    marked.use({ gfm: true, breaks: false });
    habilleClasse();
    construireMenu();

    document.getElementById('menu-toggle').addEventListener('click', function (e) {
      e.stopPropagation();
      var sb = document.getElementById('sidebar');
      var ouvert = sb.classList.toggle('ouvert');
      this.setAttribute('aria-expanded', String(ouvert));
    });
    document.addEventListener('click', function (e) {
      var sb = document.getElementById('sidebar');
      if (sb.classList.contains('ouvert') && !sb.contains(e.target)) fermeMenu();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') fermeMenu(); });
    window.addEventListener('hashchange', function () {
      etat.doc = (location.hash || '#/accueil').replace('#/', '') || 'accueil';
      rend();
    });

    etat.doc = (location.hash || '#/accueil').replace('#/', '') || 'accueil';
    rend();
  });
})();
