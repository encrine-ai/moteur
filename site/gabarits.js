/* Les gabarits par défaut : la forme sobre du site, quand le thème de la
 * classe n'en fournit pas (le thème neutre « demo », par exemple).
 *
 * Un gabarit est une fonction (modèle, page) → HTML. Le modèle vient de
 * GS.modele() (modele.js) ; la page dit ce qu'on affiche :
 *   { type: 'accueil' }
 *   { type: 'document', doc, periode?, titre, corps, html, sections }
 *   { type: 'periode', periode }
 *   { type: 'credits', doc, titre, corps, sections }   (rendu par `document`)
 *   { type: 'mentions', doc, titre, corps, sections }  (rendu par `document`)
 *   { type: 'introuvable' }
 * Les gabarits attendus : entete, accueil, document, periode, pied ;
 * facultatifs : introuvable, monter (après chaque rendu : le mouvement, s'il
 * respecte m.mouvement, c'est-à-dire prefers-reduced-motion).
 *
 * Un thème remplace tout ou partie de ces fonctions dans son propre
 * gabarits.js (site/charte/themes/<thème>/gabarits.js) :
 *     GS.theme({ entete: function (m, page) { … }, … });
 * Le menu s'anime par des accroches que app.js connaît (data-sous-menu,
 * data-menu-ouvrir, data-menu-panneau, data-menu-fermer) ; le pied reçoit de
 * toute façon la signature « Conçu avec Encrine », le lien des crédits et
 * « Mentions légales » (m.mentions : celles d'Encrine pour une classe qu'elle
 * sert, sinon la page #/mentions-legales fabriquée par le moteur, ou les
 * pages de la classe, `mentions_legales` dans classe.yml).
 * Skill charte-graphique, « Les gabarits ».
 */
(function () {
  'use strict';

  GS.gabarits = { defaut: {}, theme: {} };
  /* Ce qu'appelle le gabarits.js d'un thème. */
  GS.theme = function (gabarits) { Object.assign(GS.gabarits.theme, gabarits); };
  /* « de Mme Martin », « d’Aurélie » : la signature après « La classe ». */
  GS.de = function (nom) {
    return (/^[AEIOUYÀÂÉÈÊËÎÏÔÛÙÜ]/i.test(nom) ? 'd’' : 'de ') + nom;
  };

  var D = GS.gabarits.defaut;

  function orne(nom) { return '<span class="orne" data-orne="' + nom + '" aria-hidden="true"></span>'; }

  /* ——— L'en-tête : le nom du projet (vers l'accueil) et le menu ———
     Sur ordinateur, un sous-menu par groupe ; sur téléphone, un bouton
     « Menu » ouvre le même menu en plein écran. */
  D.entete = function (m, page) {
    var o = m.outils, esc = o.esc;
    var groupes = m.menu.filter(function (g) { return g.entrees.length; });
    function entree(e) {
      var marque = e.periode ? o.pastille(e.periode) : o.icone(e.icone);
      return '<li><a href="' + e.lien + '">' + marque + '<span><strong>' + esc(e.titre) + '</strong>' +
        (e.desc ? '<small>' + esc(e.desc) + '</small>' : '') + '</span></a></li>';
    }
    var nav = groupes.map(function (g) {
      return '<li class="m-menu-groupe"><button type="button" class="m-menu-bouton" data-sous-menu aria-expanded="false" aria-controls="sm-' + g.cle + '">' +
        esc(g.titre) + o.icone('chevron-down', 'm-chevron') + '</button>' +
        '<ul class="m-sous-menu" id="sm-' + g.cle + '" data-sous-menu-panneau hidden>' + g.entrees.map(entree).join('') + '</ul></li>';
    }).join('');
    var panneau = groupes.map(function (g) {
      return '<section class="m-panneau-groupe"><h2>' + esc(g.titre) + '</h2><ul>' + g.entrees.map(entree).join('') + '</ul></section>';
    }).join('');
    return '<div class="m-entete" data-composant="bandeau">' + orne('bandeau') +
      '<a class="m-marque" href="#/accueil">' + esc(m.classe.projet) + '</a>' +
      '<nav class="m-nav" aria-label="Menu du site"><ul><li><a class="m-menu-lien" href="#/accueil">Accueil</a></li>' + nav + '</ul></nav>' +
      '<button type="button" class="m-menu-ouvrir" data-menu-ouvrir aria-expanded="false" aria-controls="m-panneau">' +
        o.icone('menu') + '<span>Menu</span></button>' +
      '<div class="m-panneau" id="m-panneau" data-menu-panneau role="dialog" aria-modal="true" aria-label="Menu du site" hidden>' +
        '<div class="m-panneau-tete"><a href="#/accueil">' + o.icone('house') + 'Accueil</a>' +
        '<button type="button" class="m-menu-fermer" data-menu-fermer>' + o.icone('x') + '<span>Fermer</span></button></div>' +
        panneau + '</div>' +
      '</div>';
  };

  /* ——— L'accueil : le projet, l'année, le matériel, les documents ——— */
  D.accueil = function (m) {
    var o = m.outils, esc = o.esc, C = m.classe;
    var ens = C.enseignant;
    var frise = '<ol class="frise" data-composant="frise" aria-label="Les ' + esc(C.periodes_nom) + ' de l’année, zone ' + esc(C.zone) + '">' +
      m.periodes.map(function (p) {
        var ici = p.statut === 'en-cours' || p.prochaine;
        return '<li class="frise-periode' + (ici ? ' en-cours' : '') + '" data-periode="' + p.n + '" style="flex-grow:' + p.sem + '">' +
          '<a href="' + p.lien + '"><span class="frise-bande">' + orne('frise') + o.icone(p.icone) + '<span class="frise-num">P' + p.n + '</span></span>' +
          '<span class="frise-milieu">' + esc(p.milieu) + '</span>' +
          '<span class="frise-dates">' + esc(p.dates.court) + '</span>' +
          '<span class="frise-sem">' + p.sem + ' semaines</span>' +
          (p.statut === 'en-cours' ? '<span class="frise-ici">' + o.icone('map-pin') + 'Nous y sommes</span>' : '') +
          (p.prochaine ? '<span class="frise-ici">' + o.icone('map-pin') + 'Reprise le ' + esc(o.jourCourt(p.debut)) + '</span>' : '') +
          '</a></li>';
      }).join('') + '</ol>';
    var vac = m.vacances.map(function (v) {
      return '<li' + (v.enCours ? ' class="en-cours"' : '') + '><strong>' + esc(v.nom.charAt(0).toUpperCase() + v.nom.slice(1)) + '</strong><span>' + esc(v.dates) +
        '</span><span class="reprise">reprise le ' + esc(o.jourCourt(v.reprise)) + '</span>' +
        (v.enCours ? '<span class="frise-ici">' + o.icone('map-pin') + 'Nous y sommes</span>' : '') + '</li>';
    }).join('');
    // le matériel commence par la période en cours, ou par la prochaine
    var tete = m.ici.periode || m.ici.prochaine;
    var ordre = m.periodes.slice();
    if (tete) ordre = ordre.slice(tete.n - 1).concat(ordre.slice(0, tete.n - 1));
    ordre = ordre.filter(function (p) { return p.cahiers.length; });
    var materiel = ordre.map(function (p) {
      var statut = tete && tete.n === p.n ? (m.ici.periode ? 'en cours' : 'à venir') : '';
      return '<section class="materiel' + (statut ? ' en-cours' : '') + '" data-composant="materiel" data-periode="' + p.n + '">' +
        '<header class="materiel-tete">' + orne('materiel') + o.icone(p.icone) +
        '<div><div class="materiel-num">Période ' + p.n + (statut ? ' · ' + statut : '') + '</div>' +
        '<h3><a href="' + p.lien + '">' + esc(p.milieu) + '</a></h3></div></header>' +
        '<ul class="materiel-liste">' + p.cahiers.map(function (c) {
          return '<li><a href="' + c.href + '" download="' + esc(c.nom) + '">' + o.icone(c.icone) +
            '<span><strong>' + esc(c.titre) + '</strong><small>' + esc(c.desc) + '</small></span>' + o.icone('download') + '</a></li>';
        }).join('') + '</ul></section>';
    }).join('');
    var docs = m.groupes.filter(function (g) {
      return g.documents.some(function (d) { return !d.periode; });
    }).map(function (g) {
      return '<div class="docs-groupe" data-composant="documents"><h3>' + esc(g.titre) + '</h3><ul class="docs">' +
        g.documents.filter(function (d) { return !d.periode; }).map(function (d) {
          return '<li><a href="' + d.lien + '">' + o.icone(d.icone) + '<span><strong>' + esc(d.titre) + '</strong><small>' + esc(d.desc) + '</small></span></a></li>';
        }).join('') + '</ul></div>';
    }).join('');
    var ponts = m.ponts.map(function (p) { return esc(p.texte) + ' '; }).join('');
    return '<div class="contenu accueil" data-composant="accueil">' +
      '<div class="accueil-tete" data-composant="accueil-tete">' + orne('accueil') +
        '<p class="surtitre">' + esc(C.niveau.libelle) + ' · année ' + esc(C.annee) + '</p>' +
        '<h1>' + esc(C.projet) + '</h1>' +
        '<p class="chapo">' + o.texte(C.accroche) + '</p>' +
        (ens.signature ? '<p class="m-signature-classe">La classe de ' + esc(ens.signature) + '</p>' : '') +
        (ens.mot ? '<p class="m-mot">' + o.texte(ens.mot) + '</p>' : '') +
      '</div>' +
      '<section class="bloc" data-composant="bloc" data-bloc="annee"><div class="bloc-tete"><h2>L’année en ' + o.nombre(m.periodes.length) + ' ' + esc(C.periodes_nom) + '</h2>' +
        '<span class="zone-badge">zone ' + esc(C.zone) + '</span></div>' + frise +
        '<p class="frise-total">' + esc(m.annee.texte) + '</p>' +
        '<ul class="vacances">' + vac + '</ul>' +
        '<p class="note">' + ponts + 'Les dates sont celles de la zone ' + esc(C.zone) + ' ; chaque document se télécharge en PDF prêt à imprimer, dates comprises.</p></section>' +
      (materiel ? '<section class="bloc" data-composant="bloc" data-bloc="materiel"><div class="bloc-tete"><h2>À imprimer pour la classe</h2></div>' +
        '<p class="note">' + esc(m.materielNote) + '</p><div class="materiels">' + materiel + '</div></section>' : '') +
      '<section class="bloc" data-composant="bloc" data-bloc="documents"><div class="bloc-tete"><h2>Mes documents</h2></div>' + docs + '</section>' +
      '</div>';
  };

  /* Les boutons d'un document : son PDF, les cahiers de sa période, les
     extraits par période. Partagés avec les thèmes : GS.gabarits.defaut.boutons(m, page). */
  D.boutons = function (m, page) {
    var o = m.outils, esc = o.esc, doc = page.doc;
    var html = '';
    if (doc.pdf) {
      html += '<a class="btn btn-principal" href="' + doc.pdf.href + '" download="' + esc(doc.pdf.nom) + '" title="PDF prêt à imprimer, avec les dates des vacances de la classe">' +
        o.icone('download') + 'Télécharger le PDF</a>';
    }
    if (page.periode) {
      html += page.periode.cahiers.map(function (c) {
        return '<a class="btn" href="' + c.href + '" download="' + esc(c.nom) + '" title="' + esc(c.desc) + '">' + o.icone(c.icone) + esc(c.titre) + '</a>';
      }).join('');
    }
    return html;
  };
  D.extraits = function (m, page) {
    var o = m.outils, esc = o.esc;
    if (!page.doc.extraits.length) return '';
    return '<div class="periodes-print"><span>' + o.icone('printer') + 'L’extrait d’une période, pour l’afficher en classe :</span> ' +
      page.doc.extraits.map(function (e) {
        return '<a data-periode="' + e.n + '" href="' + e.href + '" download="' + esc(e.nom) + '">' + o.pastille(e.n) + esc(e.milieu) + '</a>';
      }).join(' ') + '</div>';
  };

  /* ——— Un document : la barre de boutons, puis le texte ——— */
  D.document = function (m, page) {
    var esc = m.outils.esc, doc = page.doc;
    return '<div class="m-page-doc">' +
      '<div class="toolbar" data-composant="barre"><div class="fil">' + (doc.groupe ? esc(doc.groupe) + ' › ' + esc(doc.titre) : '') + '</div>' +
        '<div class="boutons">' + D.boutons(m, page) + '</div></div>' +
      D.extraits(m, page) +
      '<article class="contenu" data-composant="document"' + (page.periode ? ' data-periode="' + page.periode.n + '"' : '') + '>' + page.html + '</article>' +
      '</div>';
  };

  /* ——— Une période : ce qu'on y fait, ses cahiers, ses documents, le projet ——— */
  function liste(titre, items, rendu) {
    if (!items || !items.length) return '';
    return '<div class="m-liste"><h3>' + titre + '</h3><ul>' + items.map(rendu).join('') + '</ul></div>';
  }
  function oeuvre(o) {
    return function (x) {
      if (typeof x === 'string') return '<li>' + o.texte(x) + '</li>';
      return '<li><strong>' + o.texte(x.titre) + '</strong>' +
        ([x.auteur, x.note].filter(Boolean).length ? ' — ' + o.texte([x.auteur, x.note].filter(Boolean).join(' · ')) : '') +
        (x.etude ? ' <span class="m-etoile">★ étude approfondie</span>' : '') + '</li>';
    };
  }
  D.sectionsProjet = function (m, p) {
    var o = m.outils, pr = p.projet || {};
    var f = oeuvre(o);
    return liste('Albums et contes', pr.albums, f) + liste('Documentaires', pr.documentaires, f) +
      liste('Textes appris', pr.textes, f) + liste('Œuvres', pr.oeuvres, f) + liste('Musique', pr.musique, f) +
      liste('Sorties et projets', pr.sorties, f) + liste('Spectacle', pr.spectacle, f);
  };
  D.periode = function (m, page) {
    var o = m.outils, esc = o.esc, p = page.periode, pr = p.projet || {};
    var statut = { 'en-cours': 'Nous y sommes', passee: 'Période passée', 'a-venir': p.prochaine ? 'Prochaine période' : 'À venir' }[p.statut];
    var fil = pr.fil_rouge || pr.mascotte;
    var cahiers = p.cahiers.length ? '<section class="m-section"><h2>Les cahiers à imprimer</h2><ul class="m-cahiers">' +
      p.cahiers.map(function (c) {
        return '<li><a href="' + c.href + '" download="' + esc(c.nom) + '">' + o.icone(c.icone) +
          '<span><strong>' + esc(c.titre) + '</strong><small>' + esc(c.desc) + ' · ' + esc(c.usage) + '</small></span>' + o.icone('download') + '</a></li>';
      }).join('') + '</ul></section>' : '';
    var documents = (p.documents.length || p.extraits.length) ? '<section class="m-section"><h2>Les documents de la période</h2><ul class="m-docs">' +
      p.documents.map(function (d) {
        return '<li><a href="' + d.lien + '">' + o.icone(d.icone) + '<span><strong>' + esc(d.titre) + '</strong><small>' + esc(d.desc) + '</small></span></a></li>';
      }).join('') +
      p.extraits.map(function (e) {
        return '<li><a href="' + e.href + '" download="' + esc(e.nom) + '">' + o.icone(e.icone) + '<span><strong>' + esc(e.titre) + '</strong><small>l’extrait de la période, en PDF</small></span>' + o.icone('download') + '</a></li>';
      }).join('') + '</ul></section>' : '';
    var imagier = ['faune', 'flore'].map(function (g) {
      var es = p.imagier[g] || [];
      if (!es.length) return '';
      return '<h3>' + (g === 'faune' ? 'La faune' : 'La flore') + '</h3><ul class="m-especes">' + es.map(function (e) {
        return '<li><img src="' + esc(e.chemin) + '" alt="" loading="lazy" width="330" height="226"><span class="mot-enfant">' + esc(e.nom) + '</span></li>';
      }).join('') + '</ul>';
    }).join('');
    var corpus = p.corpus ? '<section class="m-section"><h2>Les mots de la période</h2><div class="m-corpus">' +
      p.corpus.corpus.map(function (k) {
        return '<div><h3>' + esc(k.titre) + '</h3><ul>' + k.mots.map(function (w) { return '<li class="mot-enfant">' + esc(w) + '</li>'; }).join('') + '</ul></div>';
      }).join('') + '</div>' +
      (p.corpus.sans_carte.length ? '<p class="note">Et aussi, sans carte : <span class="mot-enfant">' + p.corpus.sans_carte.map(esc).join(', ') + '</span>.</p>' : '') +
      '</section>' : '';
    var projet = D.sectionsProjet(m, p);
    return '<article class="m-periode" data-composant="periode" data-periode="' + p.n + '">' +
      '<header class="m-periode-tete">' + o.pastille(p.n) +
        '<p class="surtitre">Période ' + p.n + ' · ' + esc(statut) + '</p>' +
        '<h1>' + esc(p.milieu) + '</h1>' +
        '<p class="m-dates">' + esc(p.dates.long) + ' · ' + p.sem + ' semaines · zone ' + esc(m.classe.zone) + '</p>' +
        (pr.resume ? '<p class="chapo">' + o.texte(pr.resume) + '</p>' : '') +
      '</header>' +
      (fil ? '<section class="m-section m-fil"><h2>' + esc(fil.nom || 'Le fil rouge') + '</h2>' +
        (p.embleme ? '<img src="' + esc(p.embleme.chemin) + '" alt="' + esc(p.embleme.alt || '') + '" loading="lazy">' : '') +
        '<p>' + o.texte(fil.texte || '') + '</p></section>' : '') +
      cahiers + documents +
      (projet ? '<section class="m-section"><h2>Le projet de la période</h2><div class="m-projet">' + projet + '</div></section>' : '') +
      (imagier ? '<section class="m-section"><h2>L’imagier</h2>' + imagier + '</section>' : '') +
      corpus +
      (!p.prete && !projet ? '<p class="note">Cette période est encore en préparation.</p>' : '') +
      '</article>';
  };

  D.introuvable = function () {
    return '<div class="m-page-doc"><article class="contenu" data-composant="document"><h1>Page introuvable</h1>' +
      '<p>Cette page n’existe pas, ou plus. <a href="#/accueil">Revenir à l’accueil</a>.</p></article></div>';
  };

  /* ——— Le pied ——— */
  D.pied = function (m) {
    var esc = m.outils.esc, C = m.classe;
    return '<div class="pied" data-composant="pied">' +
      (C.enseignant.signature ? '<p class="m-signature-classe">La classe de ' + esc(C.enseignant.signature) + ' · ' + esc(C.projet) + ' · ' + esc(C.annee) + '</p>' : '') +
      '<p>' + esc(m.pied.conformite) + ' ' + esc(m.pied.calendrier) + '</p>' +
      '<p class="pied-liens">' + (m.images.length ? '<a href="' + m.pied.credits + '">Crédits des images</a> · ' : '') +
      '<a class="pied-signature" href="' + m.signature.lien + '">' + esc(m.signature.texte) + '</a>' +
      (m.mentions ? ' · <a class="pied-mentions" href="' + esc(m.mentions.lien) + '">' + esc(m.mentions.texte) + '</a>' : '') + '</p>' +
      '</div>';
  };
})();
