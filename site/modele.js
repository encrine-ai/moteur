/* Le modèle du site : tout ce que les gabarits affichent, calculé ici.
 *
 * Le moteur calcule, le thème dessine. GS.modele() rassemble, depuis
 * classe.js (fabriqué par scripts/classe.py) et commun.js, la classe, ses
 * périodes datées pour sa zone, « nous y sommes » (une période ou des
 * vacances), les vacances, les ponts, le menu groupé, les documents et leurs
 * PDF, les cahiers de chaque période, les données du projet (classe/projet.yml),
 * l'imagier, les corpus, les crédits des images et la signature. Les gabarits
 * (site/gabarits.js, ou ceux du thème : charte/gabarits.js) ne reçoivent que
 * ce modèle : ils ne calculent ni une date, ni un chemin de PDF.
 *
 * Le contrat est décrit dans le skill charte-graphique (« Les gabarits »).
 */
(function () {
  'use strict';

  var C = GS.CLASSE;
  var DAY = 86400000;
  var SIGNATURE = { texte: 'Conçu avec Encrine', lien: 'https://encrine.ai' };
  /* Les mentions légales du pied, une seule entrée (m.mentions), toujours là :
     - une classe servie par Encrine — la classe d'exemple, ou la copie relue
       d'une classe de la galerie (encrine-ai/<id>, https://encrine.ai/<id>/) —
       porte celles d'Encrine, qui l'héberge. La copie garde dans classe.yml le `depot` et le `site` de son auteur :
       c'est l'adresse où la page est servie qui tranche ;
     - une classe qui a ses propres pages légales les nomme dans classe.yml
       (`mentions_legales: https://…`) : le pied pointe dessus ;
     - toute autre classe — le cas ordinaire, le site de l'enseignant — a la
       page que le moteur fabrique depuis classe.yml (#/mentions-legales,
       app.js, prepareMentions). */
  var MENTIONS = { texte: 'Mentions légales', lien: 'https://encrine.ai/mentions-legales/' };
  var MENTIONS_PAGE = '#/mentions-legales';
  function hebergeeParEncrine() {
    var hote = (typeof location !== 'undefined' && location.hostname) || '';
    return /^(www\.)?encrine\.ai$/.test(hote) ||
      /^encrine-ai\//.test(C.depot || '') || /^https:\/\/(www\.)?encrine\.ai\//.test(C.site || '');
  }
  function mentions() {
    if (hebergeeParEncrine()) return { texte: MENTIONS.texte, lien: MENTIONS.lien, source: 'encrine' };
    if (/^https:\/\/\S+$/.test(C.mentions_legales || '')) return { texte: MENTIONS.texte, lien: C.mentions_legales, source: 'classe' };
    return { texte: MENTIONS.texte, lien: MENTIONS_PAGE, source: 'page' };
  }

  /* ——— Outils de rendu, offerts aux gabarits ——— */
  function esc(t) {
    return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function icone(nom, classe) {
    return '<svg class="ic' + (classe ? ' ' + classe : '') + '" aria-hidden="true"><use href="charte/icones.svg#i-' + esc(nom) + '"/></svg>';
  }
  var ROMAINS = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV'];
  function romain(n) { return ROMAINS[n] || String(n); }
  var NOMBRES = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix'];
  function nombre(k) { return NOMBRES[k] || String(k); }
  /* « 1er » pour le premier du mois, comme on l'écrit. */
  function jourLong(date, avecAnnee) {
    var j = date.getUTCDate();
    return GS.fmt(date, { weekday: 'long' }) + ' ' + (j === 1 ? '1er' : j) + ' ' +
      GS.fmt(date, { month: 'long' }) + (avecAnnee ? ' ' + date.getUTCFullYear() : '');
  }
  function jourCourt(date) { return GS.fmtCourt(date); }
  /* Un texte simple de classe.yml ou de projet.yml : *italique* et **gras**,
     échappé ; rien d'autre (pas de lien, pas de HTML). */
  function texte(t) {
    return esc(t).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>');
  }

  /* ——— La date du jour ———
     ?date=AAAA-MM-JJ dans l'adresse la simule (pour vérifier « nous y sommes »
     pendant des vacances, skill site-et-calendrier). */
  function aujourdhui() {
    var m = /[?&]date=(\d{4}-\d{2}-\d{2})/.exec(location.search || '');
    if (m) return GS.d(m[1]);
    var a = new Date();
    return new Date(Date.UTC(a.getFullYear(), a.getMonth(), a.getDate()));
  }

  var VACANCES = [
    ['toussaint', 'Toussaint', 'les vacances de la Toussaint'],
    ['noel', 'Noël', 'les vacances de Noël'],
    ['hiver', 'hiver', 'les vacances d’hiver'],
    ['printemps', 'printemps', 'les vacances de printemps']
  ];

  var USAGES = { entrainement: 'à photocopier', evaluation: 'à photocopier', imagier: 'à découper et plastifier', 'cartes-corpus': 'à découper et plastifier' };

  function pdfCahier(m, n) {
    return { href: m.pdf.replace('{n}', n), nom: C.niveau.code + '-' + (m.fichier || m.nom) + '-periode-' + n + '.pdf' };
  }

  /* Les images déclarées (thème et projet) : chemin, texte de remplacement, crédit. */
  function images() {
    var liste = [];
    (C.images_theme || []).forEach(function (im) { liste.push(Object.assign({ origine: 'theme' }, im)); });
    ((C.donnees_projet || {}).images || []).forEach(function (im) { liste.push(Object.assign({ origine: 'projet' }, im)); });
    liste.forEach(function (im) {
      im.credit = [im.titre, im.auteur, im.date].filter(Boolean).join(', ') +
        (im.institution ? ' · ' + im.institution : '') + ' · ' + licenceLisible(im.licence);
    });
    return liste;
  }
  function licenceLisible(l) {
    return ({ 'PDM': 'domaine public', 'CC0-1.0': 'CC0' })[l] || String(l || '').replace(/^CC-BY-SA-/, 'CC BY-SA ').replace(/^CC-BY-/, 'CC BY ');
  }

  function modele() {
    var auj = aujourdhui();
    var t = auj.getTime();
    var CAL = GS.CAL;
    var ps = GS.periodes();
    var projet = C.donnees_projet || {};
    var projetPeriodes = projet.periodes || {};
    var lesImages = images();
    function image(fichier) {
      if (!fichier) return null;
      if (typeof fichier === 'object' && fichier.imagier) return especeImage(fichier.imagier);
      return lesImages.find(function (im) { return im.fichier === fichier || im.chemin === fichier; }) || null;
    }
    var especes = {};
    Object.keys(C.imagier || {}).forEach(function (n) {
      ['faune', 'flore'].forEach(function (g) {
        (C.imagier[n][g] || []).forEach(function (e) { especes[e.slug] = e; });
      });
    });
    function especeImage(slug) {
      var e = especes[slug];
      return e ? { chemin: e.chemin, alt: e.nom, credit: e.nom + ', photographie de ' + e.auteur + ' · ' + e.licence, origine: 'imagier' } : null;
    }

    /* — Les documents — */
    var documents = C.documents.filter(function (d) { return d.md; }).map(function (d) {
      return {
        id: d.id, titre: d.titre, desc: d.desc || '', icone: d.icone, groupe: d.groupe || '',
        lien: '#/' + d.id, md: d.md, periode: d.fiches || null,
        pdf: { href: 'pdf/' + d.id + '.pdf', nom: GS.PREFIXE + '-' + d.id + '.pdf' },
        extraits: d.par_periode ? ps.map(function (p) {
          return { n: p.n, milieu: GS.THEMES[p.n - 1], href: 'pdf/' + d.id + '-periode-' + p.n + '.pdf',
                   nom: GS.PREFIXE + '-' + d.id + '-periode-' + p.n + '.pdf' };
        }) : []
      };
    });
    var groupes = [];
    documents.forEach(function (d) {
      var g = groupes.find(function (x) { return x.titre === d.groupe; });
      if (!g) groupes.push(g = { titre: d.groupe, documents: [] });
      g.documents.push(d);
    });

    /* — Les vacances, entre deux périodes — */
    var vacances = VACANCES.map(function (v, i) {
      var cal = CAL[v[0]];
      var debut = GS.d(cal.debut), reprise = GS.d(cal.reprise), fin = GS.veille(cal.reprise);
      return { cle: v[0], nom: v[1], libelle: v[2], debut: debut, fin: fin, reprise: reprise,
               avant: i + 1, apres: i + 2, semaines: Math.round(((reprise - debut) / DAY) / 7),
               enCours: t >= debut.getTime() && t <= fin.getTime(),
               dates: 'du ' + jourCourt(debut) + ' au ' + jourCourt(fin) };
    });
    var vacEnCours = vacances.find(function (v) { return v.enCours; }) || null;

    /* — Les périodes — */
    var periodeEnCours = ps.find(function (p) { return t >= p.debut.getTime() && t <= p.fin.getTime(); }) || null;
    var prochaine = periodeEnCours ? null : (ps.find(function (p) { return p.debut.getTime() > t; }) || null);
    var periodes = ps.map(function (p) {
      var cfg = C.periodes[p.n - 1];
      var pp = projetPeriodes[cfg.cle] || {};
      var cahiers = C.materiel.filter(function (m) { return m.periodes.indexOf(p.n) !== -1; }).map(function (m) {
        var f = pdfCahier(m, p.n);
        return { cle: m.cle, titre: m.titre, icone: m.icone, desc: m.desc, href: f.href, nom: f.nom, usage: USAGES[m.cle] || '' };
      });
      var docs = documents.filter(function (d) { return d.periode === p.n; });
      var extraits = documents.filter(function (d) { return d.extraits.length; }).map(function (d) {
        var e = d.extraits[p.n - 1];
        return { doc: d, titre: d.titre, icone: d.icone, lien: d.lien, href: e.href, nom: e.nom };
      });
      var statut = periodeEnCours && periodeEnCours.n === p.n ? 'en-cours'
        : (p.fin.getTime() < t ? 'passee' : 'a-venir');
      var imagier = (C.imagier || {})[p.n] || { faune: [], flore: [] };
      return {
        n: p.n, cle: cfg.cle, milieu: cfg.milieu, icone: cfg.icone, couleur: cfg.couleur,
        romain: romain(p.n), lien: '#/periode/' + cfg.cle,
        debut: p.debut, fin: p.fin, sem: p.sem,
        dates: {
          court: jourCourt(p.debut) + ' → ' + jourCourt(p.fin),
          long: 'du ' + jourLong(p.debut) + ' au ' + jourLong(p.fin, true),
          badge: GS.badgeText(p)
        },
        statut: statut, prochaine: !!(prochaine && prochaine.n === p.n),
        cahiers: cahiers, documents: docs, extraits: extraits,
        projet: pp, embleme: image(pp.embleme),
        imagier: imagier, corpus: (C.corpus || {})[p.n] || null,
        theme: pp.theme || {},
        prete: cahiers.length > 0
      };
    });
    var P = function (n) { return n ? periodes[n - 1] : null; };

    /* — Nous y sommes — */
    var ici;
    if (periodeEnCours) {
      ici = { statut: 'periode', periode: P(periodeEnCours.n), vacances: null, prochaine: P(periodeEnCours.n + 1),
              titre: 'Nous y sommes', texte: 'Période ' + periodeEnCours.n + ' · ' + GS.THEMES[periodeEnCours.n - 1] };
    } else if (vacEnCours) {
      ici = { statut: 'vacances', periode: null, vacances: vacEnCours, prochaine: P(vacEnCours.apres),
              titre: 'Nous y sommes', texte: 'Pendant ' + vacEnCours.libelle + ' · reprise le ' + jourLong(vacEnCours.reprise) };
    } else if (prochaine) {
      ici = { statut: 'avant', periode: null, vacances: null, prochaine: P(prochaine.n),
              titre: 'Bientôt', texte: 'Rentrée le ' + jourLong(prochaine.debut, true) };
    } else {
      ici = { statut: 'apres', periode: null, vacances: null, prochaine: null,
              titre: 'L’année est finie', texte: 'Fin de l’année le ' + jourLong(ps[ps.length - 1].fin, true) };
    }

    /* — Le menu : l'accueil, les groupes de documents, les périodes — */
    var menu = [{ cle: 'accueil', titre: 'Accueil', lien: '#/accueil', entrees: [] }];
    groupes.forEach(function (g, i) {
      menu.push({ cle: 'groupe-' + (i + 1), titre: g.titre, entrees: g.documents.map(function (d) {
        return { id: d.id, titre: d.periode ? d.titre : d.titre, desc: d.desc, lien: d.lien, icone: d.icone, periode: d.periode };
      }) });
    });
    var nomPeriodes = C.periodes_nom || 'périodes';
    menu.push({ cle: 'periodes', titre: 'Les ' + nomPeriodes, entrees: periodes.map(function (p) {
      return { id: 'periode/' + p.cle, titre: p.milieu, desc: p.dates.court + ' · ' + p.sem + ' semaines',
               lien: p.lien, icone: p.icone, periode: p.n };
    }) });

    /* — Les cahiers, par sorte — */
    var sortes = C.materiel.filter(function (m) { return m.periodes.length; }).map(function (m) {
      return { cle: m.cle, titre: m.titre, icone: m.icone, desc: m.desc, periodes: m.periodes, usage: USAGES[m.cle] || '' };
    });

    var ponts = (CAL.ponts || []).map(function (p) {
      var du = GS.d(p.du), au = GS.d(p.au);
      return { nom: p.nom, du: du, au: au,
               texte: p.nom + ' : pas de classe du ' + GS.fmt(du, { weekday: 'long', day: 'numeric' }) +
                 ' au ' + jourLong(au, true) + '.' };
    });
    var total = ps.reduce(function (s, p) { return s + p.sem; }, 0);
    var ens = C.enseignant || {};

    var m = {
      classe: {
        nom: C.nom, projet: C.projet, niveau: C.niveau, annee: C.annee, sous_titre: C.sous_titre,
        accroche: C.accroche, conformite: C.conformite, zone: GS.ZONE, periodes_nom: nomPeriodes,
        origine: C.origine && C.origine.titre ? C.origine : null,
        enseignant: { signature: ens.signature || '', mot: ens.mot || '', ecole: ens.ecole || '', ville: ens.ville || '', contact: ens.contact || '' }
      },
      aujourdhui: auj,
      annee: { semaines: total, debut: ps[0].debut, fin: ps[ps.length - 1].fin,
               texte: total + ' semaines de classe, du ' + jourLong(ps[0].debut, true) + ' au ' + jourLong(ps[ps.length - 1].fin, true) + '.' },
      periodes: periodes, periode: P, ici: ici, vacances: vacances, ponts: ponts,
      menu: menu, documents: documents, groupes: groupes, sortes: sortes,
      materielNote: noteMateriel(sortes, ps.length),
      projet: projet, imagier: C.imagier || {}, corpus: C.corpus || {},
      images: lesImages, image: image,
      signature: SIGNATURE,
      mentions: mentions(),
      pied: {
        conformite: C.conformite,
        calendrier: 'Dates des vacances : calendrier scolaire officiel ' + C.annee + ', zone ' + GS.ZONE + '.',
        credits: '#/credits'
      },
      mouvement: !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches),
      outils: { esc: esc, texte: texte, icone: icone, romain: romain, nombre: nombre,
                jourLong: jourLong, jourCourt: jourCourt, fmt: GS.fmt,
                pastille: function (n) { return '<span class="pastille" data-periode="' + n + '">' + n + '</span>'; } }
    };
    return m;
  }

  /* « Pour chaque période, quatre cahiers en A4 : à photocopier (entraînement,
     évaluation) ou à découper et plastifier (imagier, cartes-corpus). » */
  function noteMateriel(sortes, nb) {
    if (!sortes.length) return '';
    var noms = function (ms) { return ms.map(function (m) { return m.titre.toLowerCase(); }).join(', '); };
    var aPhoto = sortes.filter(function (m) { return m.usage === 'à photocopier'; });
    var aPlast = sortes.filter(function (m) { return m.usage === 'à découper et plastifier'; });
    var usages = [];
    if (aPhoto.length) usages.push('à photocopier (' + noms(aPhoto) + ')');
    if (aPlast.length) usages.push('à découper et plastifier (' + noms(aPlast) + ')');
    var partout = sortes.every(function (m) { return m.periodes.length === nb; });
    var k = sortes.length;
    return (partout ? 'Pour chaque période, ' : 'Pour les périodes prêtes, ') + nombre(k) +
      (k > 1 ? ' cahiers' : ' cahier') + ' en A4 : ' + usages.join(' ou ') + '.';
  }

  GS.modele = modele;
  GS.SIGNATURE = SIGNATURE;
  GS.MENTIONS = MENTIONS;
  GS.MENTIONS_PAGE = MENTIONS_PAGE;
  GS.outils = { esc: esc, texte: texte, icone: icone, romain: romain, nombre: nombre };
})();
