/* L'appli installable : le site de la classe sur l'écran d'accueil.
 *
 * - enregistre le service worker (sw.js, fabriqué par scripts/appli.py), qui
 *   garde l'application et les documents déjà vus pour le hors-connexion ;
 * - propose, discrètement, d'installer l'appli : le bouton « Installer » sur
 *   Android et Chrome (beforeinstallprompt), le chemin « Partager, puis Sur
 *   l'écran d'accueil » sur iPhone et iPad ; ni dans l'appli déjà installée,
 *   ni à l'impression, et plus jamais une fois refermée ;
 * - en mode appli sur iOS, ouvre les PDF hors de l'appli (sinon le PDF
 *   s'affiche par-dessus l'appli, sans bouton pour en revenir) ;
 * - donne à la barre du système la couleur de l'en-tête (theme-color).
 * Les textes de la classe viennent de classe.js (CLASSE.appli).
 */
(function () {
  'use strict';

  var C = window.CLASSE || {};
  var A = C.appli || {};
  var ua = navigator.userAgent;
  var IOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  // Safari lui-même : les autres navigateurs d'iOS n'ont pas tous « Sur l'écran d'accueil »
  var SAFARI_IOS = IOS && /Safari\//.test(ua) && !/CriOS|FxiOS|EdgiOS|OPiOS|GSA\/|YaBrowser|DuckDuckGo/.test(ua);
  // Chaque classe a sa mémoire : plusieurs classes peuvent vivre sur le même
  // domaine (https://<propriétaire>.github.io/<dépôt>/).
  var CLE = 'encrine-invitation:' + location.pathname.replace(/[^/]*$/, '');

  function enAppli() {
    return navigator.standalone === true ||
      ['standalone', 'fullscreen', 'minimal-ui'].some(function (m) {
        return window.matchMedia('(display-mode: ' + m + ')').matches;
      });
  }

  function lire(cle) { try { return window.localStorage.getItem(cle); } catch (e) { return null; } }
  function ecrire(cle, v) { try { window.localStorage.setItem(cle, v); } catch (e) { /* stockage bloqué : tant pis */ } }

  function icone(nom) {
    return '<svg class="ic" aria-hidden="true"><use href="charte/icones.svg#i-' + nom + '"/></svg>';
  }

  /* ——— La couleur de la barre du système : celle de l'en-tête ——— */
  function couleurBarre() {
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) return;
    // l'en-tête que dessine le gabarit : son emplacement, ou son premier élément
    var entete = document.getElementById('entete');
    var fond = '';
    [entete, entete && entete.firstElementChild].forEach(function (el) {
      var f = el ? getComputedStyle(el).backgroundColor : '';
      if (!fond && f && f !== 'rgba(0, 0, 0, 0)') fond = f;
    });
    if (fond) meta.setAttribute('content', fond);
  }

  /* ——— Le service worker ———
   * Une nouvelle publication installe un nouveau service worker, qui prend
   * la main tout de suite (skipWaiting, clients.claim) : la page, chargée
   * par l'ancien, se recharge alors une fois, pour être toute de la
   * nouvelle version. Pas au premier enregistrement (rien à remplacer), et
   * jamais deux fois de suite en moins de 30 s (garde contre les boucles). */
  var CLE_RECHARGE = 'encrine-recharge:' + location.pathname.replace(/[^/]*$/, '');
  function enregistrer() {
    if (!('serviceWorker' in navigator) || !/^https?:$/.test(location.protocol)) return;
    var sw = navigator.serviceWorker;
    var avait = !!sw.controller;
    var recharge = false;
    sw.addEventListener('controllerchange', function () {
      if (!avait) { avait = true; return; }
      if (recharge) return;
      var avant = 0;
      try { avant = parseInt(window.sessionStorage.getItem(CLE_RECHARGE) || '0', 10); } catch (e) { /* bloqué */ }
      if (Date.now() - avant < 30000) return;
      recharge = true;
      try { window.sessionStorage.setItem(CLE_RECHARGE, String(Date.now())); } catch (e) { /* bloqué */ }
      location.reload();
    });
    sw.register('sw.js').catch(function () { /* le site marche sans */ });
  }

  /* ——— L'invitation à installer ——— */
  var invitation = null;
  var demande = null;   // l'évènement beforeinstallprompt, gardé pour le bouton

  function fermer(definitivement) {
    if (invitation) { invitation.remove(); invitation = null; }
    if (definitivement) ecrire(CLE, 'fermee');
  }

  function montrer(mode) {
    if (invitation || enAppli() || lire(CLE)) return;
    invitation = document.createElement('aside');
    invitation.className = 'invitation';
    invitation.dataset.composant = 'invitation';
    invitation.dataset.mode = mode;
    invitation.setAttribute('aria-label', 'Installer l’appli de la classe');
    var texte = mode === 'ios'
      ? '<strong>Sur l’écran d’accueil</strong><span>Touchez ' + icone('share') + '<b>Partager</b>, puis ' +
        icone('square-plus') + '<b>« Sur l’écran d’accueil »</b> : la classe s’ouvrira comme une appli.</span>'
      : '<strong>Installer l’appli de la classe</strong><span>Sur l’écran d’accueil, elle s’ouvre d’un geste, même sans réseau.</span>';
    invitation.innerHTML =
      '<img class="invitation-icone" src="icones/appli-192.png" alt="" width="44" height="44">' +
      '<p class="invitation-texte">' + texte + '</p>' +
      (mode === 'ios' ? '' : '<button type="button" class="btn btn-principal" data-action="installer">' + icone('download') + 'Installer</button>') +
      '<button type="button" class="invitation-fermer" data-action="fermer" aria-label="Ne plus proposer">' + icone('x') + '</button>';
    invitation.addEventListener('click', function (e) {
      var b = e.target.closest('[data-action]');
      if (!b) return;
      if (b.dataset.action === 'fermer') { fermer(true); return; }
      if (demande) {
        var d = demande;
        demande = null;
        d.prompt();
        d.userChoice.then(function (choix) { fermer(choix && choix.outcome === 'accepted'); });
      }
    });
    document.body.appendChild(invitation);
  }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();          // pas la bannière du navigateur : la nôtre, refermable
    demande = e;
    montrer('android');
  });
  window.addEventListener('appinstalled', function () { fermer(true); });

  /* ——— Les PDF en mode appli sur iOS ———
   * Dans l'appli installée, un PDF ouvert sur place recouvre l'appli sans
   * bouton de retour, et l'attribut download n'y télécharge rien : on
   * l'ouvre dans une feuille du navigateur (« OK » pour revenir). */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || !/\.pdf(?:[?#]|$)/i.test(a.getAttribute('href')) || !enAppli()) return;
    a.setAttribute('target', '_blank');
    a.setAttribute('rel', 'noopener');
    if (IOS) a.removeAttribute('download');
  }, true);

  document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.toggleAttribute('data-appli', enAppli());
    var titre = document.querySelector('meta[name="apple-mobile-web-app-title"]');
    if (titre && A.nom_court) titre.setAttribute('content', A.nom_court);
    // l'en-tête n'existe qu'une fois la première page rendue (app.js)
    document.addEventListener('encrine:page', couleurBarre);
    if (window.matchMedia) {
      var sombre = window.matchMedia('(prefers-color-scheme: dark)');
      if (sombre.addEventListener) sombre.addEventListener('change', couleurBarre);
    }
    if (SAFARI_IOS && !enAppli()) setTimeout(function () { montrer('ios'); }, 1200);
  });
  window.addEventListener('load', enregistrer);
})();
