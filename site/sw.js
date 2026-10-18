/* Le service worker de l'appli de la classe.
 * Fabriqué par scripts/appli.py (python3 scripts/classe.py generer) depuis
 * scripts/modele-sw.js : ne pas modifier site/sw.js à la main.
 *
 * - À l'installation : l'application (HTML, JS, CSS, polices, icônes,
 *   classe.json) et les documents Markdown du menu entrent en cache.
 * - Les pages, documents et scripts passent par le réseau d'abord : en ligne,
 *   l'enseignant voit toujours la dernière publication ; hors connexion (ou
 *   si le réseau tarde), la copie gardée prend le relais.
 * - Les PDF et les images n'entrent en cache que quand on les ouvre, dans
 *   une limite (les plus anciens sortent).
 * - VERSION est une empreinte du site publié : à chaque publication qui
 *   change quelque chose, le nouveau service worker remplace l'ancien cache.
 * - Sa portée est le dossier du site (https://<propriétaire>.github.io/<dépôt>/) ;
 *   ses caches sont préfixés par cette portée, si bien que deux classes
 *   publiées sur le même domaine ne s'effacent pas l'une l'autre.
 */
'use strict';

var VERSION = "7a77527817b8";
var PRECACHE = [
  "./",
  "index.html",
  "imprimer.html",
  "app.css",
  "impression.css",
  "app.js",
  "appli.js",
  "commun.js",
  "classe.js",
  "classe.json",
  "marked.min.js",
  "manifest.webmanifest",
  "charte/charte.css",
  "charte/icones.svg",
  "favicon.ico",
  "icones/appli.svg",
  "icones/appli-192.png",
  "icones/appli-512.png",
  "icones/appli-maskable-512.png",
  "icones/apple-touch-icon.png",
  "icones/favicon-32.png",
  "charte/polices/andika-latin-400.woff2",
  "charte/polices/andika-latin-700.woff2",
  "charte/polices/andika-latin-ext-400.woff2",
  "charte/polices/andika-latin-ext-700.woff2",
  "charte/themes/demo/polices/atkinson-next-latin-ext.woff2",
  "charte/themes/demo/polices/atkinson-next-latin-italic.woff2",
  "charte/themes/demo/polices/atkinson-next-latin.woff2",
  "charte/themes/demo/polices/bricolage-grotesque-latin-ext.woff2",
  "charte/themes/demo/polices/bricolage-grotesque-latin.woff2",
  "content/01-projet-annuel.md",
  "content/02-programmation-annuelle.md"
];

var PORTEE = self.registration.scope;
var PREFIXE = 'encrine ' + PORTEE + ' ';
var CACHE_APPLI = PREFIXE + VERSION + ' appli';
var CACHE_PDF = PREFIXE + VERSION + ' pdf';
var CACHE_IMAGES = PREFIXE + VERSION + ' images';
var LIMITE = { pdf: 40, images: 300 };
// Au-delà de ce délai sans réponse du réseau, la copie gardée s'affiche
// (le réseau d'une école est parfois très lent) ; la réponse du réseau, si
// elle finit par arriver, met tout de même le cache à jour.
var DELAI_RESEAU = 4000;

function url(rel) { return new URL(rel, PORTEE).href; }

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE_APPLI).then(function (cache) {
    // Un fichier qui manque ne bloque pas l'installation : le reste suffit.
    return Promise.all(PRECACHE.map(function (rel) {
      return fetch(new Request(url(rel), { cache: 'reload' })).then(function (rep) {
        if (rep.ok) return cache.put(url(rel), rep);
      }).catch(function () {});
    }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (noms) {
    return Promise.all(noms.filter(function (n) {
      return n.indexOf(PREFIXE) === 0 && n.indexOf(PREFIXE + VERSION + ' ') !== 0;
    }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});

function chercher(cache, req) {
  return cache.match(req, { ignoreSearch: true }).then(function (rep) {
    if (rep || req.mode !== 'navigate') return rep;
    // une page de l'appli jamais vue : l'accueil, qui sait afficher le reste
    return cache.match(url('./')).then(function (r) { return r || cache.match(url('index.html')); });
  });
}

/* Garde au plus `max` entrées : les plus anciennes sortent. */
function limiter(cache, max) {
  return cache.keys().then(function (cles) {
    return Promise.all(cles.slice(0, Math.max(0, cles.length - max)).map(function (k) { return cache.delete(k); }));
  });
}

function ranger(nomCache, req, rep, max) {
  if (!rep || !rep.ok || rep.type === 'opaque' || rep.status === 206) return Promise.resolve();
  return caches.open(nomCache).then(function (cache) {
    // supprimer avant de remettre : l'entrée passe en fin de liste (la plus récente)
    return cache.delete(req, { ignoreSearch: true }).then(function () { return cache.put(req, rep); })
      .then(function () { return max ? limiter(cache, max) : null; });
  });
}

function horsLigne(req) {
  var pdf = /\.pdf$/i.test(new URL(req.url).pathname);
  var texte = pdf
    ? 'Ce PDF n’a pas encore été ouvert sur cet appareil : il sera lisible hors connexion une fois ouvert avec le réseau.'
    : 'Pas de connexion, et cette page n’a pas encore été ouverte sur cet appareil.';
  return new Response(
    '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<title>Hors connexion</title><style>body{font:17px/1.6 system-ui,sans-serif;margin:0;padding:max(24px,env(safe-area-inset-top)) 24px 24px;color:#222;background:#f6f6f2}' +
    'main{max-width:34em;margin:10vh auto}a{color:inherit}</style></head><body><main><h1>Hors connexion</h1><p>' + texte +
    '</p><p><a href="' + url('./') + '">Revenir à l’accueil</a></p></main></body></html>',
    { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

/* Le réseau d'abord, la copie gardée s'il échoue ou s'il tarde. */
function reseauDabord(e, nomCache, max) {
  var req = e.request;
  var reseau = fetch(req);
  // la copie se range même si la copie gardée a déjà été rendue (réseau lent)
  e.waitUntil(reseau.then(function (rep) { return ranger(nomCache, req, rep.clone(), max); })
    .catch(function () {}));
  return new Promise(function (resolve) {
    var fini = false;
    function rendre(rep) { if (!fini && rep) { fini = true; resolve(rep); } }
    var minuteur = setTimeout(function () {
      caches.open(nomCache).then(function (c) { return chercher(c, req); }).then(rendre);
    }, DELAI_RESEAU);
    reseau.then(function (rep) { clearTimeout(minuteur); rendre(rep); }, function () {
      clearTimeout(minuteur);
      caches.open(nomCache).then(function (c) { return chercher(c, req); })
        .then(function (rep) { rendre(rep || horsLigne(req)); });
    });
  });
}

/* La copie gardée d'abord (polices, icônes, photographies : elles ne
 * changent qu'avec une publication, qui vide le cache). */
function cacheDabord(e, nomCache, max) {
  var req = e.request;
  return caches.open(nomCache).then(function (c) { return chercher(c, req); }).then(function (rep) {
    return rep || fetch(req).then(function (r) {
      e.waitUntil(ranger(nomCache, req, r.clone(), max));
      return r;
    }).catch(function () { return horsLigne(req); });
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;
  var u = new URL(req.url);
  if (u.href.indexOf(PORTEE) !== 0) return;   // hors du site de la classe
  var chemin = u.pathname;
  if (/\.pdf$/i.test(chemin)) {
    e.respondWith(reseauDabord(e, CACHE_PDF, LIMITE.pdf));
  } else if (/\.(jpe?g|png|webp|avif|gif)$/i.test(chemin) && PRECACHE.indexOf(u.href.slice(PORTEE.length)) === -1) {
    e.respondWith(cacheDabord(e, CACHE_IMAGES, LIMITE.images));
  } else if (/\.(woff2?|svg|ico)$/i.test(chemin)) {
    e.respondWith(cacheDabord(e, CACHE_APPLI));
  } else {
    // pages, documents Markdown, classe.json, scripts, feuilles de style
    e.respondWith(reseauDabord(e, CACHE_APPLI));
  }
});
