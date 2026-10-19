/* L'application de la classe : le routage, la lecture des documents, le
 * comportement du menu — la logique, qui reste au moteur.
 *
 * La forme, elle, est au thème : chaque page est rendue par un GABARIT
 * (site/gabarits.js par défaut, ou charte/gabarits.js, fabriqué depuis le
 * thème de la classe par scripts/classe.py). Un gabarit reçoit le modèle
 * (GS.modele(), site/modele.js) et la page, et rend du HTML ; il ne lit
 * rien, ne calcule rien, ne réécrit pas cette logique. Skill
 * charte-graphique, « Les gabarits ».
 *
 * Routes : #/accueil, #/<document>, #/periode/<clé>, #/credits.
 */
(function () {
  'use strict';

  var cacheMd = {};
  var modele;
  var premiere = true;

  /* Le gabarit `nom` : celui du thème s'il en a un, sinon celui du moteur. */
  function gabarit(nom) {
    var t = GS.gabarits.theme[nom];
    return { fn: t || GS.gabarits.defaut[nom], source: t ? 'theme' : 'defaut' };
  }

  /* ——— Les pages ——— */
  function route() {
    var h = (location.hash || '').replace(/^#\/?/, '');
    if (!h || h === 'accueil') return { type: 'accueil' };
    if (h === 'credits') return { type: 'credits' };
    var m = /^periode\/([\w-]+)$/.exec(h);
    if (m) {
      var p = modele.periodes.find(function (x) { return x.cle === m[1]; });
      return p ? { type: 'periode', periode: p } : { type: 'introuvable' };
    }
    var doc = modele.documents.find(function (d) { return d.id === h; });
    return doc ? { type: 'document', doc: doc, periode: modele.periode(doc.periode) } : { type: 'introuvable' };
  }

  function chargeMd(chemin) {
    if (cacheMd[chemin]) return Promise.resolve(cacheMd[chemin]);
    return fetch(chemin).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.text();
    }).then(function (t) { cacheMd[chemin] = t; return t; });
  }

  function slug(t) {
    return t.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'section';
  }

  /* Le Markdown d'un document, rendu et préparé pour le gabarit : le titre
     (h1), le corps sans ce titre, les sections (h2) avec un identifiant et
     leur période, et les badges de dates de la zone sur chaque « Période N ». */
  function prepareDocument(page) {
    return chargeMd(page.doc.md).then(function (md) {
      var div = document.createElement('div');
      div.innerHTML = marked.parse(GS.nettoieMarkdown(md));
      var h1 = div.querySelector('h1');
      var vus = {};
      page.sections = [];
      div.querySelectorAll('h2').forEach(function (h) {
        var id = slug(h.textContent);
        while (vus[id]) id += '-2';
        vus[id] = true;
        h.id = id;
        var n = /P[ée]riode\s*(\d)/i.exec(h.textContent);
        page.sections.push({ id: id, titre: h.textContent.trim(), periode: n ? parseInt(n[1], 10) : null });
      });
      // le titre, avant les badges de dates (sinon il porterait leur texte)
      page.titre = h1 ? h1.textContent.trim() : page.doc.titre;
      GS.annoteTitres(div);
      page.html = div.innerHTML;
      if (h1) h1.remove();
      page.corps = div.innerHTML;
      return page;
    });
  }

  /* La page des crédits : les images du thème et du projet, les photographies
     de l'imagier, les polices du thème — fabriquée ici, rendue par le gabarit
     des documents. */
  function prepareCredits(page) {
    var esc = GS.outils.esc;
    var C = GS.CLASSE;
    var tete = '<thead><tr><th>Œuvre</th><th>Auteur</th><th>Source</th><th>Licence</th></tr></thead>';
    function ligne(titre, auteur, href, source, licence) {
      return '<tr><td>' + titre + '</td><td>' + esc(auteur) + '</td><td>' +
        (href ? '<a href="' + esc(href) + '">' + esc(source) + '</a>' : esc(source)) + '</td><td>' + esc(licence) + '</td></tr>';
    }
    var lignes = modele.images.map(function (im) {
      return ligne(esc(im.titre) + (im.recadrage ? '<br><small>' + esc(im.recadrage) + '</small>' : ''),
        [im.auteur, im.date].filter(Boolean).join(', '), im.source, im.institution || 'source', im.licence);
    }).join('');
    var photos = '';
    Object.keys(modele.imagier).forEach(function (n) {
      ['faune', 'flore'].forEach(function (g) {
        (modele.imagier[n][g] || []).forEach(function (e) {
          photos += ligne(esc(e.nom), e.auteur, e.observation, 'iNaturalist', e.licence);
        });
      });
    });
    var polices = (C.polices_theme || []).map(function (p) {
      return '<li><strong>' + esc(p.famille) + '</strong>, ' + esc(p.auteur) + ' (' + esc(p.licence) + ')</li>';
    }).join('');
    page.titre = 'Crédits';
    page.sections = [];
    var corps = '<p>Les images de ce site sont du domaine public ou sous licence libre. Les cahiers imprimables portent leurs propres crédits.</p>';
    if (lignes) { corps += '<h2 id="images">Les images du site</h2><table>' + tete + '<tbody>' + lignes + '</tbody></table>'; page.sections.push({ id: 'images', titre: 'Les images du site' }); }
    if (photos) { corps += '<h2 id="imagier">Les photographies de l’imagier</h2><table>' + tete + '<tbody>' + photos + '</tbody></table>'; page.sections.push({ id: 'imagier', titre: 'Les photographies de l’imagier' }); }
    corps += '<h2 id="polices">Les polices et les icônes</h2><ul>' + polices +
      '<li><strong>Andika</strong>, SIL International (OFL-1.1) — les mots de l’enfant</li><li>Icônes : Lucide (ISC)</li></ul>';
    page.sections.push({ id: 'polices', titre: 'Les polices et les icônes' });
    page.corps = corps;
    page.html = '<h1>Crédits</h1>' + corps;
    page.doc = { id: 'credits', titre: 'Crédits', desc: '', icone: 'image', groupe: '', lien: '#/credits', pdf: null, extraits: [] };
    return Promise.resolve(page);
  }

  /* ——— Le rendu ——— */
  function poser(id, nom, page) {
    var el = document.getElementById(id);
    var g = gabarit(nom);
    el.innerHTML = g.fn(modele, page);
    el.dataset.gabarit = g.source;
  }

  function rend() {
    var page = route();
    var pret = page.type === 'document' ? prepareDocument(page)
      : page.type === 'credits' ? prepareCredits(page) : Promise.resolve(page);
    var contenu = document.getElementById('contenu');
    contenu.setAttribute('aria-busy', 'true');
    pret.catch(function () {
      page.erreur = true;
      page.titre = page.doc ? page.doc.titre : 'Page introuvable';
      page.corps = page.html = '<p>Impossible de charger ce document. Vérifiez votre connexion puis rechargez la page.</p>';
      page.sections = [];
      return page;
    }).then(function (page) {
      fermeMenu(false);
      document.body.dataset.page = page.type;
      if (page.periode) document.body.dataset.periode = page.periode.n; else delete document.body.dataset.periode;
      poser('entete', 'entete', page);
      poser('contenu', page.type === 'credits' ? 'document' : page.type, page);
      poser('pied', 'pied', page);
      garantirPied();
      marqueActifs();
      document.title = titrePage(page);
      contenu.removeAttribute('aria-busy');
      var monter = GS.gabarits.theme.monter || GS.gabarits.defaut.monter;
      if (monter) monter(document.body, modele, page);
      if (!premiere) {
        window.scrollTo(0, 0);
        contenu.focus({ preventScroll: true });
      }
      premiere = false;
      // le premier rendu a eu lieu : le garde-fou d'index.html se tait
      document.documentElement.setAttribute('data-rendu', 'ok');
      document.dispatchEvent(new CustomEvent('encrine:page', { detail: { type: page.type } }));
    });
  }

  /* Le titre de l'onglet (et du raccourci sur l'écran d'accueil) :
     « Encrine – <projet> » sur l'accueil, celui qu'écrit `classe.py generer`
     dans index.html pour les aperçus de lien (scripts/apercu.py), et
     « <titre de la page> · Encrine – <projet> » ailleurs. */
  function titrePage(page) {
    var fin = 'Encrine – ' + GS.CLASSE.projet;
    if (page.type === 'accueil') return fin;
    if (page.type === 'periode') return page.periode.milieu + ' · ' + fin;
    if (page.doc) return page.doc.titre + ' · ' + fin;
    return 'Page introuvable · ' + fin;
  }

  /* Ce que le pied doit toujours porter, quel que soit le gabarit : la
     signature « Conçu avec Encrine », le lien des crédits, et le crédit de
     la classe d'origine (CC BY et CC BY-SA l'exigent). Un gabarit qui les
     oublie les reçoit ici, sous leur forme sobre. */
  function garantirPied() {
    var pied = document.getElementById('pied');
    var esc = GS.outils.esc;
    if (!pied.querySelector('a[href="' + GS.SIGNATURE.lien + '"]')) {
      pied.insertAdjacentHTML('beforeend', '<p class="pied-signature"><a href="' + GS.SIGNATURE.lien + '">' + GS.SIGNATURE.texte + '</a></p>');
    }
    if (modele.images.length && !pied.querySelector('a[href="#/credits"]')) {
      pied.insertAdjacentHTML('beforeend', '<p class="pied-credits"><a href="#/credits">Crédits des images</a></p>');
    }
    var org = modele.classe.origine;
    if (org && !pied.querySelector('[data-origine]')) {
      pied.insertAdjacentHTML('beforeend', '<p class="pied-origine" data-origine>Classe partie de « ' +
        (org.site ? '<a href="' + esc(org.site) + '">' + esc(org.titre) + '</a>' : esc(org.titre)) + ' »' +
        (org.auteur ? ', de ' + esc(org.auteur) : '') + ' (' + esc(org.licence) + ').</p>');
    }
  }

  /* aria-current sur chaque lien de la page affichée ; data-actif sur le
     bouton du sous-menu qui la contient. */
  function marqueActifs() {
    var ici = location.hash && location.hash.indexOf('#/') === 0 ? location.hash : '#/accueil';
    document.querySelectorAll('a[href^="#/"]').forEach(function (a) {
      if (a.getAttribute('href') === ici) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-sous-menu]').forEach(function (b) {
      var cible = document.getElementById(b.getAttribute('aria-controls'));
      if (cible && cible.querySelector('[aria-current="page"]')) b.dataset.actif = '';
      else delete b.dataset.actif;
    });
  }

  /* ——— Le menu ———
     Le gabarit de l'en-tête pose des accroches ; le moteur leur donne vie :
       [data-sous-menu][aria-controls]   ouvre et ferme un sous-menu (un seul à
                                         la fois ; Échap, un clic ailleurs ou
                                         le focus qui s'en va le ferment) ;
       [data-menu-ouvrir][aria-controls] ouvre le menu du téléphone,
                                         [data-menu-panneau], un dialogue : le
                                         focus y reste, Échap le ferme et le
                                         rend au bouton ;
       [data-menu-fermer]                le ferme. */
  var ouvreur = null;

  function panneau() { return document.querySelector('[data-menu-panneau]:not([hidden])'); }

  function focusables(el) {
    return Array.prototype.filter.call(
      el.querySelectorAll('a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'),
      function (x) { return x.getClientRects().length > 0; });
  }

  function ouvreMenu(bouton) {
    var p = document.getElementById(bouton.getAttribute('aria-controls'));
    if (!p) return;
    fermeSousMenus();
    ouvreur = bouton;
    p.hidden = false;
    bouton.setAttribute('aria-expanded', 'true');
    document.body.dataset.menu = 'ouvert';
    document.documentElement.style.overflow = 'hidden';
    var actif = p.querySelector('[aria-current="page"]');
    var f = focusables(p);
    (actif || f[0] || p).focus();
  }

  function fermeMenu(rendreFocus) {
    fermeSousMenus();
    var p = panneau();
    if (!p) return;
    p.hidden = true;
    delete document.body.dataset.menu;
    document.documentElement.style.overflow = '';
    document.querySelectorAll('[data-menu-ouvrir]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    if (rendreFocus !== false && ouvreur && document.contains(ouvreur)) ouvreur.focus();
    ouvreur = null;
  }

  function fermeSousMenus(sauf) {
    document.querySelectorAll('[data-sous-menu][aria-expanded="true"]').forEach(function (b) {
      if (b === sauf) return;
      b.setAttribute('aria-expanded', 'false');
      var c = document.getElementById(b.getAttribute('aria-controls'));
      if (c) c.hidden = true;
    });
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-sous-menu]');
    if (b) {
      e.preventDefault();
      var ouvert = b.getAttribute('aria-expanded') === 'true';
      fermeSousMenus(b);
      b.setAttribute('aria-expanded', String(!ouvert));
      var c = document.getElementById(b.getAttribute('aria-controls'));
      if (c) c.hidden = ouvert;
      return;
    }
    var o = e.target.closest('[data-menu-ouvrir]');
    if (o) { e.preventDefault(); ouvreMenu(o); return; }
    if (e.target.closest('[data-menu-fermer]')) { e.preventDefault(); fermeMenu(); return; }
    var a = e.target.closest('a[href^="#"]');
    if (a) {
      var href = a.getAttribute('href');
      if (href.indexOf('#/') !== 0) {
        // une ancre dans la page (sommaire, lien d'évitement) : on y va sans
        // toucher à la route
        var cible = href.length > 1 && document.getElementById(decodeURIComponent(href.slice(1)));
        if (cible) {
          e.preventDefault();
          fermeMenu(false);
          if (!cible.hasAttribute('tabindex')) cible.setAttribute('tabindex', '-1');
          cible.scrollIntoView({ behavior: modele.mouvement ? 'smooth' : 'auto', block: 'start' });
          cible.focus({ preventScroll: true });
        }
        return;
      }
      if (href === location.hash) { fermeMenu(false); window.scrollTo(0, 0); }
    }
    if (!e.target.closest('[data-sous-menu-panneau]')) fermeSousMenus();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var ouvert = document.querySelector('[data-sous-menu][aria-expanded="true"]');
      if (panneau()) { fermeMenu(); e.preventDefault(); }
      else if (ouvert) { fermeSousMenus(); ouvert.focus(); e.preventDefault(); }
      return;
    }
    if (e.key === 'Tab') {
      var p = panneau();
      if (!p) return;
      var f = focusables(p);
      if (!f.length) return;
      var premier = f[0], dernier = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === premier || !p.contains(document.activeElement))) {
        e.preventDefault(); dernier.focus();
      } else if (!e.shiftKey && (document.activeElement === dernier || !p.contains(document.activeElement))) {
        e.preventDefault(); premier.focus();
      }
    }
  });

  // un sous-menu se ferme quand le focus le quitte (au clavier)
  document.addEventListener('focusin', function (e) {
    document.querySelectorAll('[data-sous-menu][aria-expanded="true"]').forEach(function (b) {
      var c = document.getElementById(b.getAttribute('aria-controls'));
      if (e.target !== b && c && !c.contains(e.target)) {
        b.setAttribute('aria-expanded', 'false');
        c.hidden = true;
      }
    });
  });

  window.addEventListener('hashchange', function () {
    if (!location.hash || location.hash.indexOf('#/') === 0) rend();
  });

  document.addEventListener('DOMContentLoaded', function () {
    marked.use({ gfm: true, breaks: false });
    modele = GS.modele();
    rend();
  });
})();
