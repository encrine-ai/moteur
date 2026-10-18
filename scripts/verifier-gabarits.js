#!/usr/bin/env node
/* Essaie les gabarits d'un thème sur la vraie classe, sans navigateur.
 *
 * Usage : node scripts/verifier-gabarits.js <dossier-site> <gabarits.js du thème | ->
 * Charge classe.json, commun.js, modele.js, gabarits.js (ceux du moteur),
 * puis le gabarits.js du thème, dans un bac à sable ; rend chaque page —
 * l'accueil, chaque document, chaque période, les crédits, une page
 * introuvable — et contrôle ce que le moteur attend du HTML :
 *   - chaque gabarit rend un texte, sans erreur ;
 *   - l'en-tête a un menu de téléphone (data-menu-ouvrir → data-menu-panneau),
 *     et chaque aria-controls nomme un élément présent ;
 *   - toute page du menu a son lien ;
 *   - le document contient son texte (page.html ou page.corps) et ses PDF ;
 *   - la période porte ses cahiers (leurs PDF) ;
 *   - chaque <img> a un alt, chaque <button> un type ;
 *   - le pied porte la signature (lien vers https://encrine.ai).
 * Écrit une anomalie par ligne sur la sortie ; code 1 s'il y en a.
 * Lancé par scripts/verifier-theme.py.
 */
'use strict';
var fs = require('fs');
var path = require('path');
var vm = require('vm');

var site = process.argv[2];
var theme = process.argv[3];
var anomalies = [];
function ko(t) { anomalies.push(t); }

var CLASSE = JSON.parse(fs.readFileSync(path.join(site, 'classe.json'), 'utf8'));
var ctx = {
  CLASSE: CLASSE, console: console, Intl: Intl, Date: Date, Math: Math, JSON: JSON,
  location: { search: '', hash: '' },
  matchMedia: function () { return { matches: false }; },
  document: { createElement: function () { throw new Error('un gabarit ne fabrique pas d’élément : il rend du texte'); } }
};
ctx.window = ctx;
vm.createContext(ctx);
function charge(f, nom) {
  try { vm.runInContext(fs.readFileSync(f, 'utf8') + '\n;this.GS = typeof GS !== "undefined" ? GS : this.GS;', ctx, { filename: nom || f }); }
  catch (e) { ko(nom + ' : ' + e.message); }
}
// commun.js déclare `var GS` : dans le bac à sable, c'est une globale
charge(path.join(site, 'commun.js'), 'commun.js');
charge(path.join(site, 'modele.js'), 'modele.js');
charge(path.join(site, 'gabarits.js'), 'gabarits.js');
if (theme && theme !== '-') charge(theme, 'gabarits.js du thème');
if (anomalies.length) { console.log(anomalies.join('\n')); process.exit(1); }

var GS = ctx.GS;
var ATTENDUS = ['entete', 'accueil', 'document', 'periode', 'pied'];
var T = GS.gabarits.theme;
// d'autres fonctions que les gabarits attendus sont permises : des aides du thème
Object.keys(T).forEach(function (k) {
  if (typeof T[k] !== 'function') ko('GS.theme : « ' + k + ' » n’est pas une fonction');
});
if (theme && theme !== '-' && !Object.keys(T).length) ko('le gabarits.js du thème n’enregistre rien : GS.theme({ entete: …, accueil: …, … })');

var m = GS.modele();
function rend(nom, page) {
  var fn = T[nom] || GS.gabarits.defaut[nom];
  if (typeof fn !== 'function') { ko('gabarit « ' + nom + ' » absent'); return ''; }
  try {
    var html = fn(m, page);
    if (typeof html !== 'string' || !html.trim()) { ko('gabarit « ' + nom + ' » (' + page.type + ') : ne rend rien'); return ''; }
    return html;
  } catch (e) { ko('gabarit « ' + nom + ' » (' + (page.doc ? page.doc.id : page.type) + ') : ' + e.message); return ''; }
}
function controle(html, ou) {
  (html.match(/<img\b[^>]*>/g) || []).forEach(function (t) { if (!/\balt=/.test(t)) ko(ou + ' : une image sans alt (' + t.slice(0, 60) + '…)'); });
  (html.match(/<button\b[^>]*>/g) || []).forEach(function (t) { if (!/\btype=/.test(t)) ko(ou + ' : un bouton sans type'); });
  if (/<script\b/i.test(html)) ko(ou + ' : un gabarit n’écrit pas de <script>');
  if (/\son[a-z]+=/i.test(html)) ko(ou + ' : un gabarit n’écrit pas d’attribut on…= (le comportement est au moteur)');
}
var pages = [{ type: 'accueil' }];
m.documents.forEach(function (d) {
  pages.push({ type: 'document', doc: d, periode: m.periode(d.periode), titre: d.titre,
               html: '<h1>' + d.titre + '</h1><p>TEXTE-DU-DOCUMENT</p>', corps: '<p>TEXTE-DU-DOCUMENT</p>',
               sections: [{ id: 'section', titre: 'Période 1', periode: 1 }] });
});
m.periodes.forEach(function (p) { pages.push({ type: 'periode', periode: p }); });
pages.push({ type: 'credits', doc: { id: 'credits', titre: 'Crédits', desc: '', icone: 'image', groupe: '', lien: '#/credits', pdf: null, extraits: [] },
             titre: 'Crédits', html: '<h1>Crédits</h1><p>TEXTE-DU-DOCUMENT</p>', corps: '<p>TEXTE-DU-DOCUMENT</p>', sections: [] });
pages.push({ type: 'introuvable' });

var liens = {};
pages.forEach(function (page) {
  var ou = page.type + (page.doc ? ' ' + page.doc.id : page.periode ? ' ' + page.periode.cle : '');
  var entete = rend('entete', page);
  var corps = rend(page.type === 'credits' ? 'document' : page.type, page);
  var pied = rend('pied', page);
  var tout = entete + corps + pied;
  controle(tout, ou);
  (tout.match(/href="(#\/[^"]*)"/g) || []).forEach(function (h) { liens[h.slice(6, -1)] = true; });
  if (page.type === 'accueil') {
    if (!/data-menu-ouvrir/.test(entete)) ko('en-tête : pas de bouton data-menu-ouvrir (le menu du téléphone)');
    if (!/data-menu-panneau/.test(entete)) ko('en-tête : pas de data-menu-panneau (le menu du téléphone)');
    (entete.match(/aria-controls="([^"]+)"/g) || []).forEach(function (a) {
      var id = a.slice(15, -1);
      if (entete.indexOf('id="' + id + '"') === -1) ko('en-tête : aria-controls="' + id + '" ne nomme aucun élément');
    });
    if (!/<nav\b/.test(entete)) ko('en-tête : le menu est un <nav>');
  }
  if (page.type === 'document' || page.type === 'credits') {
    if (corps.indexOf('TEXTE-DU-DOCUMENT') === -1) ko(ou + ' : le gabarit n’affiche pas le texte (page.corps ou page.html)');
    if (page.doc.pdf && corps.indexOf(page.doc.pdf.href) === -1) ko(ou + ' : pas de lien vers son PDF (' + page.doc.pdf.href + ')');
    if (page.doc.extraits.length && corps.indexOf(page.doc.extraits[0].href) === -1) ko(ou + ' : pas de lien vers les extraits par période');
    if (page.periode) page.periode.cahiers.forEach(function (c) {
      if (corps.indexOf(c.href) === -1) ko(ou + ' : pas de lien vers le cahier ' + c.href);
    });
  }
  if (page.type === 'periode') {
    page.periode.cahiers.forEach(function (c) { if (corps.indexOf(c.href) === -1) ko(ou + ' : pas de lien vers le cahier ' + c.href); });
    page.periode.documents.forEach(function (d) { if (corps.indexOf(d.lien) === -1) ko(ou + ' : pas de lien vers ' + d.lien); });
  }
  if (pied && pied.indexOf('https://encrine.ai') === -1) ko(ou + ' : le pied ne porte pas la signature (lien vers https://encrine.ai)');
});
m.menu.forEach(function (g) {
  (g.lien ? [g] : []).concat(g.entrees).forEach(function (e) { if (!liens[e.lien]) ko('aucune page n’a de lien vers ' + e.lien + ' (' + e.titre + ')'); });
});
if (anomalies.length) console.log(anomalies.filter(function (a, i) { return anomalies.indexOf(a) === i; }).join('\n'));
process.exit(anomalies.length ? 1 : 0);
