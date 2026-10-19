/* Le service worker de l'appli de la classe.
 * Fabriqué par scripts/appli.py (python3 scripts/classe.py generer) depuis
 * scripts/modele-sw.js : ne pas modifier site/sw.js à la main.
 *
 * - À l'installation : l'application (HTML, JS, CSS, polices, icônes,
 *   classe.json) et les documents Markdown du menu entrent en cache, tous
 *   ensemble et tous de la même publication : c'est l'instantané de cette
 *   version, que rien ne vient ensuite modifier.
 * - Le déploiement (classe.py estampiller) écrit dans index.html et
 *   imprimer.html chaque script et chaque feuille de style avec `?v=VERSION` :
 *   une page ne demande que les scripts de sa publication, et le service
 *   worker ne lui rend jamais ceux d'une autre (ni du cache HTTP, l'adresse
 *   change à chaque version, ni de sa copie, qui ne répond qu'à sa version).
 * - Les pages, documents et scripts passent par le réseau d'abord, en
 *   revalidant le cache HTTP (`cache: 'no-cache'` : GitHub Pages sert tout
 *   avec max-age=600, qui servirait sinon une page de la publication
 *   d'avant) ; hors connexion, si le réseau échoue ou s'il tarde, la copie
 *   gardée prend le relais — l'instantané entier, page et scripts de la même
 *   version.
 * - Les PDF et les images n'entrent en cache que quand on les ouvre, dans
 *   une limite (les plus anciens sortent).
 * - VERSION est une empreinte du site publié : à chaque publication qui
 *   change quelque chose, le nouveau service worker prend la main tout de
 *   suite (skipWaiting, clients.claim), efface les caches des versions
 *   d'avant, et la page se recharge une fois (appli.js, controllerchange).
 * - Sa portée est le dossier du site (https://<propriétaire>.github.io/<dépôt>/) ;
 *   ses caches sont préfixés par cette portée, si bien que deux classes
 *   publiées sur le même domaine ne s'effacent pas l'une l'autre.
 */
'use strict';

var VERSION = "d12c0f85c3f6";
var PRECACHE = [
  "./",
  "index.html",
  "imprimer.html",
  "app.css",
  "impression.css",
  "app.js",
  "appli.js",
  "commun.js",
  "modele.js",
  "gabarits.js",
  "charte/gabarits.js",
  "classe.js",
  "classe.json",
  "marked.min.js",
  "manifest.webmanifest",
  "charte/charte.css",
  "marque/marque.css",
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
  "marque/polices/figtree-latin-ext.woff2",
  "marque/polices/figtree-latin.woff2",
  "marque/polices/marelle.woff2",
  "marque/polices/unbounded-latin-ext.woff2",
  "marque/polices/unbounded-latin.woff2",
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
// (le réseau d'une école est parfois très lent) — seulement si elle est de
// la version demandée : sinon on attend le réseau.
var DELAI_RESEAU = 4000;
// Ce que le déploiement versionne (?v=VERSION) dans index.html et imprimer.html.
var VERSIONNE = /\.(js|css)$/i;

function url(rel) { return new URL(rel, PORTEE).href; }
function sansRecherche(u) { u = new URL(u); return u.origin + u.pathname; }
/* L'adresse sous laquelle un fichier de l'instantané est gardé : celle
 * qu'écrit le déploiement, ?v=VERSION pour les scripts et les feuilles. */
function cle(rel) { return VERSIONNE.test(rel) ? url(rel) + '?v=' + VERSION : url(rel); }

// L'instantané de la version : ce que l'installation a rangé, et que le
// réseau ne vient jamais remplacer (une page d'une autre publication, rangée
// ici, demanderait des scripts que ce cache n'a pas).
var INSTANTANE = {};
PRECACHE.forEach(function (rel) { INSTANTANE[url(rel)] = true; });

/* Une page de l'instantané doit être de cette version : si le serveur sert
 * encore celle d'avant (publication en cours), l'installation échoue, et le
 * navigateur la retentera à la prochaine visite. */
function memeVersion(rel, rep) {
  if (!/(^|\/|\.html)$/.test(rel)) return Promise.resolve(rep);
  return rep.clone().text().then(function (html) {
    // la version d'un script ou d'une feuille (pas celle de l'image de partage)
    var m = /\.(?:js|css)\?v=([0-9a-f]+)/.exec(html);
    if (m && m[1] !== VERSION) throw new Error(rel + ' est de la version ' + m[1] + ', pas ' + VERSION);
    return rep;
  });
}

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE_APPLI).then(function (cache) {
    // Un document ou une police qui manque ne bloque pas l'installation : le
    // reste suffit. Une page ou un script, si, comme une page d'une autre
    // version : l'instantané serait incomplet ou mélangé.
    return Promise.all(PRECACHE.map(function (rel) {
      var essentiel = VERSIONNE.test(rel) || /(^|\/|\.html)$/.test(rel);
      return fetch(new Request(cle(rel), { cache: 'reload' })).then(function (rep) {
        if (!rep.ok) { if (essentiel) throw new Error(rel + ' : ' + rep.status); return; }
        return memeVersion(rel, rep).then(function (r) { return cache.put(cle(rel), r); });
      }, function (err) { if (essentiel) throw err; });
    }));
  }).catch(function (err) {
    return caches.delete(CACHE_APPLI).then(function () { throw err; });
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (noms) {
    return Promise.all(noms.filter(function (n) {
      return n.indexOf(PREFIXE) === 0 && n.indexOf(PREFIXE + VERSION + ' ') !== 0;
    }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});

/* La copie gardée d'une requête — jamais celle d'une autre version. */
function chercher(cache, req) {
  var u = new URL(req.url);
  var v = u.searchParams.get('v');
  var trouve;
  if (v !== null) {
    // une adresse versionnée : la copie de cette version-là, ou rien
    trouve = v === VERSION ? cache.match(req.url) : Promise.resolve(undefined);
  } else {
    trouve = cache.match(req.url).then(function (rep) {
      if (rep) return rep;
      // un script demandé sans version (une page que le déploiement
      // n'estampille pas) : celui de l'instantané
      if (VERSIONNE.test(u.pathname)) return cache.match(sansRecherche(req.url) + '?v=' + VERSION);
      // imprimer.html?doc=… : la page, quels que soient ses paramètres
      return cache.match(sansRecherche(req.url));
    });
  }
  return trouve.then(function (rep) {
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
  if (nomCache === CACHE_APPLI && (INSTANTANE[sansRecherche(req.url)] || new URL(req.url).searchParams.has('v'))) {
    return Promise.resolve();   // l'instantané ne change qu'avec la version
  }
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

/* Le réseau, en revalidant le cache HTTP du navigateur : GitHub Pages sert
 * tout avec max-age=600, si bien qu'un simple fetch(req) rendrait, dix
 * minutes durant, la page ou le script de la publication d'avant. */
function aJour(req) {
  try {
    return fetch(new Request(req, { cache: 'no-cache' }));
  } catch (err) {
    // un navigateur qui refuse de recopier une requête de navigation
    return fetch(new Request(req.url, {
      cache: 'no-cache', credentials: 'same-origin',
      redirect: req.mode === 'navigate' ? 'manual' : 'follow'
    }));
  }
}

/* Le réseau d'abord, la copie gardée s'il échoue ou s'il tarde. */
function reseauDabord(e, nomCache, max, revalider) {
  var req = e.request;
  var reseau = revalider ? aJour(req) : fetch(req);
  // la copie se range même si la copie gardée a déjà été rendue (réseau lent)
  e.waitUntil(reseau.then(function (rep) { return ranger(nomCache, req, rep.clone(), max); })
    .catch(function () {}));
  return new Promise(function (resolve) {
    var fini = false;
    // pas de copie de la version demandée : on attend le réseau
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
  if (u.searchParams.get('v') === VERSION) {
    // un script ou une feuille de cette version : l'instantané d'abord (le
    // serveur, lui, ignore ?v= et rendrait peut-être déjà ceux d'après)
    e.respondWith(cacheDabord(e, CACHE_APPLI));
  } else if (/\.pdf$/i.test(chemin)) {
    e.respondWith(reseauDabord(e, CACHE_PDF, LIMITE.pdf, false));
  } else if (/\.(jpe?g|png|webp|avif|gif)$/i.test(chemin) && !INSTANTANE[u.origin + chemin]) {
    e.respondWith(cacheDabord(e, CACHE_IMAGES, LIMITE.images));
  } else if (/\.(woff2?|svg|ico)$/i.test(chemin)) {
    e.respondWith(cacheDabord(e, CACHE_APPLI));
  } else {
    // pages, documents Markdown, classe.json, scripts, feuilles de style
    e.respondWith(reseauDabord(e, CACHE_APPLI, 0, true));
  }
});
