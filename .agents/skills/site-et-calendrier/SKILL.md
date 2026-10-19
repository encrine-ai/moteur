---
name: site-et-calendrier
description: L'application web de la classe (site/, JavaScript sans cadriciel, publiée sur GitHub Pages) et le calendrier scolaire qui la date — la zone de vacances de la classe (A, B ou C), le calendrier officiel de chaque année dans le moteur, périodes, liste des documents, vue d'impression, déploiement. À utiliser pour ajouter ou renommer un document dans le menu, changer de zone ou d'année scolaire, mettre à jour les dates de vacances, corriger le calcul des périodes ou des semaines, toucher à classe.yml, commun.js, app.js, imprimer.html ou au workflow .github/workflows/pages.yml, ou comprendre pourquoi le site déployé ne montre pas une modification. Se déclenche aussi sans nom de fichier : « passe le site en 2027-2028 », « les dates des vacances d'hiver sont fausses pour la zone C », « on est en zone B, pas en C », « ajoute le document sur les sorties au menu », « le site n'est pas à jour », « le bouton PDF ne marche pas », « la période en cours n'est pas la bonne ». Pour l'apparence, voir charte-graphique ; pour la fabrication des PDF, imprimer-pdf.
---

# Le site et le calendrier

Le site est une application d'une page, sans cadriciel, qui lit les documents
Markdown du dépôt et les rend avec `marked`. Rien n'est construit à l'avance,
sauf les PDF.

| Fichier | Rôle |
|---|---|
| `classe.yml` | **la classe** : nom, niveau, année, projet, **sa zone de vacances** (`calendrier.zone`), les milieux des périodes, **la liste des documents**. La seule source de ce qui distingue cette classe d'une autre ; rien de tout cela ne s'écrit dans le code |
| `referentiel/calendrier-AAAA-AAAA.yml` | **le calendrier officiel** d'une année scolaire, pour les trois zones : données nationales, communes à toutes les classes, qui font partie du moteur |
| `scripts/classe.py` | `generer` fabrique `site/classe.json` et `site/classe.js` (versionnés), avec les dates de **la zone de la classe** seulement, tirées du calendrier de son année ; `verifier` sort en code 1 si ces fichiers sont périmés, si la zone n'est pas A, B ou C, si l'année n'a pas de fichier de calendrier, s'il reste des dates (les anciennes clés) dans `classe.yml`, ou si une donnée de la classe — l'année, le projet, un milieu — est écrite en dur dans le moteur. Le déploiement le refait |
| `site/commun.js` | l'objet `GS`, bâti sur `CLASSE` : le calendrier de la classe (`CAL`, et sa zone `ZONE`), les milieux (`THEMES`, `ICONES_MILIEU`), les documents (`DOCS`), le préfixe des fichiers téléchargés, le calcul des périodes et le badge de dates. Partagé par l'application et la vue d'impression |
| `site/index.html` | le bloc du titre et de l'aperçu de lien (`scripts/apercu.py`, ci-dessous) ; trois emplacements — `#entete`, `#contenu`, `#pied` — et le lien d'évitement ; le manifeste et les meta de l'appli ; charge `modele.js`, `gabarits.js`, puis `charte/gabarits.js` (ceux du thème) et `app.js` |
| `site/modele.js` | `GS.modele()` : le modèle des pages — périodes datées pour la zone, « Nous y sommes » (une période, ou des vacances : « pendant les vacances de la Toussaint »), vacances, ponts, menu groupé, documents et leurs PDF, cahiers de chaque période, projet, imagier, corpus, images et crédits, signature. `?date=AAAA-MM-JJ` dans l'adresse simule un jour |
| `site/app.js` | la logique : routes (`#/accueil`, `#/<document>`, `#/periode/<clé>`, `#/credits`, `#/mentions-legales`), lecture et rendu du Markdown (titre, sections, badges de dates), menu (sous-menus, dialogue du téléphone, Échap, focus), crédits ; la **forme** vient des gabarits (skill charte-graphique, « Le mini-site ») ; aucun sélecteur de zone |
| `site/gabarits.js` | les gabarits par défaut : l'en-tête et le menu, l'accueil, le document (boutons PDF `pdf/<doc>.pdf`, extraits `pdf/<doc>-periode-N.pdf`), la période, le pied |
| `site/imprimer.html` | la vue que Chromium imprime : `?doc=…[&periode=N]`, aux dates de la zone de la classe |
| `.github/workflows/pages.yml` | à chaque push sur `main` : contrôler `classe.yml`, assembler `_site/`, fabriquer les PDF (un par document et par extrait de période, plus les cahiers : 65 pour une classe de Grande Section complète), contrôler la pagination, publier |
| `.github/workflows/controles.yml` | **dans le moteur seulement** (jamais copié dans une classe) : sur chaque demande de fusion et chaque envoi sur `main` d'`encrine-ai/moteur`, les contrôles rapides et sans réseau — `classe.py verifier`, `verifier-theme.py`, `verifier-partage.py` (et `tester`), `chemins_moteur.py verifier`, la syntaxe des scripts et du JavaScript ; `couverture.py` y est affiché sans être exigé, la démonstration du modèle étant en cours d'écriture |

Les documents Markdown sont copiés dans `_site/content/` au déploiement ; en
local, il faut faire de même (voir le skill imprimer-pdf, étape 1).

## Pour qui est le site

« Je veux vraiment un site destiné à une maîtresse, pas à un développeur. »
Le site a été refait trois fois avant d'y arriver (un rendu des fichiers du
dépôt, refusé, puis l'application actuelle). Il n'affiche donc :

- **aucune référence technique** — ni GitHub, ni Markdown, ni dépôt, ni nom
  de fichier, ni lien vers le code ; le site est autoporté (`marked`, les
  polices et les icônes sont embarqués) ;
- **aucune phrase qui décrit le site à celle qui y est** (« Sur le site en
  ligne… » a été retiré) ;
- des **PDF déjà prêts** à télécharger et imprimer, pas une page « à
  imprimer depuis le navigateur ».

Le `README.md` se contente du lien du site : l'adresse du dépôt, sur le
dépôt, « n'a aucun intérêt ». Ce lien est dans son bloc de tête, que
`classe.py generer` tire de `depot` (`https://<propriétaire>.github.io/<dépôt>/`)
ou de `site` dans `classe.yml`, à écrire quand la classe est servie
ailleurs (un domaine propre : la classe d'exemple est sur
`https://encrine.ai/tour-du-monde/`).

Deux défauts déjà rencontrés : un bouton PDF à `display: inline-block`
annulait son attribut `hidden` et s'affichait, inerte, sur toutes les pages
(commit « Correction : boutons PDF inertes visibles hors des pages
concernées ») — vérifier qu'un élément masqué l'est vraiment ; et une favicon
SVG en *data URI* non échappée, remplacée par de vrais fichiers
(`site/favicon.ico`).

## L'appli installable

L'enseignant installe le site de **sa** classe sur l'écran d'accueil de son
téléphone ou de sa tablette, et l'ouvre en classe comme une appli, même sans
réseau. Tout est fabriqué par `scripts/appli.py`, que lance
`python3 scripts/classe.py generer` :

| Fichier | Rôle |
|---|---|
| `site/manifest.webmanifest` | nom (`nom — projet`) et nom court (l'étiquette sous l'icône), tirés de `classe.yml` ; `start_url` et `scope` à `./` (le site vit dans un sous-dossier) ; **pas d'`id`** — résolu contre la seule origine, il ferait de deux classes d'un même domaine une seule appli ; `display: standalone`, `lang: fr` ; `theme_color` = `--feuille` (l'en-tête), `background_color` = `--papier`, lus dans le bloc clair de `theme.css` |
| `site/icones/` et `site/favicon.ico` | l'icône de la classe : les cinq bandes de ses périodes (`--p1`…`--p5`) et un disque `--feuille` portant son initiale en `--sapin`, dans la police des titres du thème — `appli.svg` (la lettre en contour, sans police), `appli-192.png`, `appli-512.png`, `appli-maskable-512.png` (le disque dans la zone sûre), `apple-touch-icon.png` (180, plein, iOS l'arrondit), `favicon-32.png`, `favicon.ico` (16, 32, 48). Aucun logo d'Encrine : c'est l'appli de la classe. Les PNG demandent Pillow, fontTools et brotli ; chaque icône porte l'empreinte de ce dont elle est faite, que `verifier` relit sans eux |
| `site/sw.js` | le service worker, tiré de `scripts/modele-sw.js` : l'application, les polices, les icônes, `classe.json` et les documents Markdown du menu en cache à l'installation ; **réseau d'abord**, en revalidant le cache HTTP (`cache: 'no-cache'` : GitHub Pages sert tout avec `max-age=600`), pour les pages, documents, scripts et `classe.json` (la copie gardée si le réseau échoue ou tarde 4 s — seulement de la version demandée) ; l'installation range un **instantané** de la version (pages et scripts de la même publication, sinon elle échoue), que le réseau ne modifie plus ; PDF et images **à l'usage** seulement (40 PDF, 300 images au plus) ; un PDF jamais ouvert répond hors connexion par une page qui le dit. `VERSION` est l'empreinte du site : chaque publication qui change quelque chose remplace l'ancien cache. Caches préfixés par la portée : deux classes d'un même domaine ne s'effacent pas |
| `site/appli.js` (moteur) | enregistre `sw.js` ; l'**invitation** (`data-composant="invitation"`) : « Installer » par `beforeinstallprompt` sur Android et Chrome, « Partager, puis Sur l'écran d'accueil » dans Safari d'iPhone et d'iPad ; refermée, elle ne revient plus (`localStorage`, par dossier de classe) ; jamais dans l'appli installée ni à l'impression. En mode appli sur iOS, les PDF s'ouvrent dans une feuille du navigateur (`target="_blank"`, sans `download`) ; la couleur de la barre et le titre iOS viennent du thème et de `classe.yml` |

- `classe.yml` peut fixer `appli: {nom, nom_court, initiale}` ; sinon le nom
  court est le nom de la classe (≤ 12 lettres), le projet sans article
  (≤ 15), ou « GS 2026-2027 », et l'initiale celle du nom court.
- **Jamais une page d'une publication avec les scripts d'une autre** (un
  iPhone est resté sur « Chargement… » : le nouvel `index.html` avec les
  anciens scripts, tirés du cache HTTP ou de la copie du service worker).
  Trois parades : `classe.py estampiller` écrit, sur le site assemblé
  seulement, chaque `<script src>` et `<link rel=stylesheet>` locaux
  d'`index.html` et d'`imprimer.html` en `?v=<version de sw.js>` (jamais
  dans le dépôt : `verifier` refuse un `?v=` en dur) ; le service worker
  sert un `?v=` de sa version depuis son instantané, un autre depuis le
  réseau, jamais une copie d'une autre version ; et un nouveau service
  worker prend la main tout de suite — la page se recharge **une fois**
  (`controllerchange`, garde de 30 s dans `sessionStorage`, pas au premier
  enregistrement).
- **Le garde-fou** (`<script id="garde-fou">`, en ligne et en ES5, avant
  tous les autres dans `index.html`) : une erreur de script ou une promesse
  rejetée avant le premier rendu, ou pas de rendu au bout de 15 s, et
  « Chargement… » laisse place à « Le site n'a pas pu se charger. » et un
  bouton « Recharger », qui désinscrit le service worker de la classe, vide
  ses caches (`encrine <portée>`) et recharge. `app.js` pose
  `data-rendu="ok"` sur `<html>` au premier rendu ; `verifier` refuse un
  `index.html` sans garde-fou.
- Safari d'iOS : le JS du moteur et des gabarits reste en ES5 (ni `=>`, ni
  `?.`, ni `groupBy`, `toSorted`, `findLast`, `at()`, `structuredClone`,
  lookbehind, champs privés, blocs `static`) ; `marked.min.js` v12 utilise
  des méthodes privées (`#e()`), d'où iOS 15 au minimum.
- `imprimer.html` lie le manifeste mais **n'enregistre pas** le service
  worker : Chromium y fabrique les PDF sans rien en cache (vérifié : mêmes
  PDF, mêmes pages, avant et après l'appli).
- `classe.py verifier` refuse un manifeste, une icône ou un `sw.js` absent ou
  périmé, un chemin absolu ; une version en retard (un document changé sans
  `generer`) n'est qu'un avertissement : le déploiement la recalcule sur le
  site assemblé (`python3 scripts/classe.py estampiller _site --adresse …`).
- Pour l'essayer : servir le site assemblé **dans un sous-dossier**
  (`http://127.0.0.1:PORT/<dépôt>/`). Hors connexion : arrêter le serveur —
  `setOffline` de Playwright ne coupe pas les requêtes du service worker.
  Mode appli : Chromium lancé avec `--app=<adresse>` (profil non privé :
  en navigation privée, Chrome refuse l'installation par principe).
- **Limites d'iOS** : pas d'invitation système (d'où l'explication) ;
  l'appli installée a son propre stockage, distinct de Safari ; Safari
  d'iOS 26 range parfois « Partager » dans le menu « ··· ».

## Le calendrier

**Une classe a une zone de vacances, la sienne**, choisie au départ (skill
nouvelle-classe), et c'est **le seul réglage du calendrier** dans
`classe.yml` :

```yaml
annee: 2026-2027
calendrier:
  zone: C
```

Les dates, elles, sont **nationales** et vivent dans le moteur :
`referentiel/calendrier-<annee>.yml` porte, pour une année scolaire, les
dates **officielles** (jeu de données
[fr-en-calendrier-scolaire](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/)) :
rentrée, Toussaint et Noël (communes aux trois zones), hiver et printemps
(par zone), fin d'année, ponts nationaux. Chaque vacance se note par son
**premier jour** et son **jour de reprise** ; la période se termine la
veille du premier jour. `classe.py generer` n'en retient que la zone de la
classe : `site/classe.json` et `classe.js` ne portent qu'une zone, et le site
n'a ni sélecteur ni mémoire de zone.

- **Un pont propre à l'école** (un pont local décidé par l'inspection, par
  exemple) s'écrit dans `classe.yml`, sous `calendrier.ponts`
  (`{nom, du, au}`) : il s'ajoute aux ponts nationaux, et l'accueil
  l'affiche. Rien d'autre du calendrier ne s'écrit dans la classe ;
  `classe.py verifier` refuse toute autre clé.
- **Ne pas écrire une date de période dans un document.** Le badge de chaque
  titre « Période N » la calcule pour la zone de la classe, et chaque
  document n'existe qu'en **un** PDF, à plat dans `pdf/`.
- **Toute date se relève dans le jeu de données, jamais de mémoire** : la fin
  de l'année 2026-2027 a d'abord été écrite « 6 juillet », alors que les
  cours finissent le **vendredi 2 juillet 2027**.
- Le nombre de semaines est un arrondi de jours / 7 : vérifier qu'il tombe
  juste quand on change d'année (P1 2026-2027 : 7 semaines, P5 zone A : 10).
- Les ponts s'affichent d'eux-mêmes dans l'accueil ; le README, lui, les
  écrit en clair : à reprendre à la main.

### Changer de zone

Une ligne : `calendrier.zone` dans `classe.yml`, puis tout se refabrique.

```sh
python3 scripts/classe.py generer && python3 scripts/classe.py verifier
python3 scripts/generer-imagier.py && python3 scripts/generer-cartes-corpus.py
bash scripts/generer-pdf.sh /tmp/site && python3 scripts/verifier-pagination.py /tmp/site
```

Les PDF des documents changent de dates d'eux-mêmes (le déploiement les
refait). Reste à la main ce qui est du contenu : les dates de la zone dans
le `README.md` et dans `01-projet-annuel.md`, s'ils en citent.

### Changer d'année scolaire

1. **Dans le moteur** (le dépôt modèle) : un nouveau fichier
   `referentiel/calendrier-AAAA-AAAA.yml`, sur le modèle du précédent, avec
   les dates officielles des **trois** zones relevées dans le jeu de données
   ci-dessus (filtré sur l'année ; zones A, B, C de métropole) et les ponts
   nationaux. `classe.py verifier` contrôle sa forme. Les classes le
   reçoivent par **synchroniser-moteur** ; une classe qui n'a pas encore
   synchronisé voit `verifier` refuser l'année (« … n'existe pas »).
2. **Dans la classe** : `annee` dans `classe.yml` (la zone ne bouge pas),
   puis `python3 scripts/classe.py generer`. Le site, les noms des PDF
   téléchargés et les pieds de page des cahiers suivent ; régénérer les
   cahiers (`generer-imagier.py`, `generer-cartes-corpus.py`).
3. Reste ce qui est du contenu, à reprendre à la main : le tableau des
   vacances et des périodes du `README.md`, le calendrier de
   `01-projet-annuel.md` (dates communes seulement), et l'en-tête de
   `classe/annotations.yml` — `grep -rn 2026-2027` les trouve.
4. Vérifier à l'écran : frise, semaines, badge d'un titre, période en cours
   pour une date simulée.

## La page de chaque période

`#/periode/<clé>` (la `cle` de la période dans `classe.yml`) existe pour
chaque période, prête ou non, et le menu les liste (« Les continents », du
nom de `periodes_nom`). Elle montre ses dates pour la zone et son statut
(passée, en cours — « Nous y sommes » —, prochaine, à venir), **ses
cahiers** (ceux que `materiel` déclare pour elle, avec leur PDF), **ses
documents** (l'évaluation qui porte `fiches: N`, l'extrait de chaque
progression `par_periode`), les **données du projet** (`classe/projet.yml` :
ce qu'on y fait, le fil rouge, les albums, les œuvres, la musique, les
sorties, les textes appris, l'emblème, et les données propres au thème),
l'**imagier** de la période et les **mots de ses corpus**. Rien à déclarer
pour qu'elle existe ; pour la remplir, écrire `classe/projet.yml` (skill
charte-graphique, « La page de période ») — seulement ce que le projet
annuel dit déjà. Le lien d'une ancienne adresse (`#/eval-p1`) marche
toujours : c'est un document.

## Ajouter un document au menu

Une entrée de `documents` dans `classe.yml` : `{id, titre, icone, md, groupe,
desc}`, plus `par_periode: true` pour une progression (extraits imprimables
par période) et `fiches: N` pour une évaluation (boutons du matériel de la
période, couleur de la période ; le titre et l'icône viennent alors du
milieu). `icone` est un nom d'icône du sprite (skill charte-graphique). Puis
`python3 scripts/classe.py generer` : `scripts/generer-pdf.sh` lit la même
liste dans `site/classe.json`, si bien que le PDF du nouveau document est
fabriqué sans autre retouche.

## Le matériel à imprimer

L'accueil (« À imprimer pour la classe ») et les boutons d'une période
n'annoncent que les cahiers que déclare `materiel` dans `classe.yml` :
`{cle, titre, icone, desc, periodes}`, avec `cle` parmi `entrainement`,
`evaluation`, `imagier`, `cartes-corpus` — `scripts/classe.py` (`CAHIERS`) en
déduit la page source et le PDF. Une période sans cahier n'a pas de carte à
l'accueil ; sans aucun cahier, la section disparaît. `generer-pdf.sh` et
`verifier-pagination.py` lisent la même liste, et `classe.py verifier`
refuse qu'elle s'écarte des pages fabriquées : un cahier déclaré sans page,
ou une page sans déclaration. Les nombres (« 18 animaux et 18 plantes ») et
l'intitulé de l'imagier (`intitule`, ici « faune et flore ») vivent là, jamais
dans `site/*.js`.

## Le titre des pages et l'aperçu de lien

Le titre de l'onglet (et du raccourci posé sur l'écran d'accueil) est
**« Encrine – <projet> »** sur l'accueil, **« <titre de la page> · Encrine –
<projet> »** ailleurs (« L’Afrique · Encrine – Le tour du monde », « Crédits ·
… », « Page introuvable · … ») : `titrePage()` dans `app.js`. Le manifeste,
lui, garde son nom court sous l'icône.

Les messageries (iMessage, WhatsApp, Signal, Slack) et les réseaux
**n'exécutent pas le JavaScript** : ils lisent le `<head>` statique de
`index.html`. `scripts/apercu.py` y écrit, entre `<!-- apercu:debut -->` et
`<!-- apercu:fin -->`, le `<title>` de l'accueil, la meta description, les
balises Open Graph (`og:type` website, `og:locale` fr_FR, `og:site_name`
Encrine, `og:title`, `og:description`, `og:url`, `og:image` et ses
`width`/`height`/`alt`) et Twitter (`summary_large_image`). La description
est l'`accroche` de `classe.yml`, suivie de « La classe de <signature>. » si
l'enseignant signe. Ce bloc porte la classe par construction : la chasse aux
données écrites en dur l'ignore ; ne jamais le retoucher à la main.

- `classe.py generer` écrit le bloc en adresses **relatives** (le dépôt ne
  connaît pas son adresse) ; `classe.py verifier` refuse un bloc absent ou
  périmé. Après une synchronisation du moteur, `index.html` arrive avec le
  bloc du modèle : `generer` le refait.
- Au déploiement, `classe.py estampiller _site --adresse <base_url>` (l'étape
  `actions/configure-pages`, `id: pages`, passe donc **avant** l'estampille)
  fabrique l'image de partage puis réécrit le bloc du site assemblé en
  adresses **absolues** — Open Graph l'exige ; `og:image` porte `?v=<empreinte>`
  pour que les messageries ne gardent pas l'ancienne image. Sans `--adresse`,
  le bloc reste relatif et un avertissement le dit. L'aperçu passe avant la
  version de `sw.js`, calculée sur ce qui sera publié.
- **L'image de partage**, `partage.png`, 1200 × 630, n'est pas versionnée :
  Chromium (celui des PDF) rend le haut de l'accueil à 1200 × 630, sur une
  copie temporaire de `index.html` sans `appli.js` (ni service worker, ni
  invitation à installer), avec une discrète pastille « Conçu avec
  Encrine ». Un thème peut dessiner la sienne : un gabarit `partage`
  (`GS.theme({ partage: function (m) { … } })`, une vignette de 1200 × 630).
  Pillow la réduit à une palette (sous 300 Ko ; d'où `pip install pillow`
  dans le workflow). Piège : le nouveau mode sans tête de Chrome retranche
  87 px de `--window-size` pour une barre fantôme ; `apercu.py` mesure cet
  écart, agrandit la fenêtre d'autant et recadre.
- Pour vérifier : assembler le site comme le workflow, lancer
  `estampiller --adresse https://<domaine>/<dépôt>/`, lire les balises
  **sans JavaScript** (le HTML brut), regarder `partage.png` réduite à
  300 px de large (la taille d'un aperçu sur téléphone) et simuler une bulle
  d'iMessage ou de WhatsApp.

## Les mentions légales

Le pied de **chaque** classe porte « Mentions légales » (`m.mentions`,
`site/modele.js` ; `garantirPied` dans `app.js` l'ajoute si le gabarit
l'oublie). Où mène le lien, dans cet ordre :

1. **Une classe servie par Encrine** — la classe d'exemple, une copie relue
   de la galerie : l'adresse de la page (`encrine.ai`), ou `depot` dans
   `encrine-ai/`, ou `site` sous `https://encrine.ai/` → les mentions
   d'Encrine, https://encrine.ai/mentions-legales/ (Encrine l'héberge).
2. **`mentions_legales: https://…`** dans `classe.yml` (facultatif) : la
   classe a déjà ses pages légales, le pied y pointe.
3. **Sinon — le cas ordinaire, le site de l'enseignant** : la page
   `#/mentions-legales`, que `prepareMentions()` (`app.js`) fabrique depuis
   `classe.yml` et que le gabarit `document` du thème rend, comme les
   crédits (`page.type === 'mentions'`). Elle dit :
   - **Éditeur** : `enseignant.signature` (sinon « L’enseignant de cette
     classe »), « site personnel non professionnel » ; **contact** :
     `enseignant.contact` (une adresse e-mail ou une page https://,
     facultatif), sinon le compte GitHub du propriétaire de `depot`
     (https://github.com/<propriétaire>) ; sans `depot` défini, pas de
     contact ;
   - **Hébergeur** : GitHub B.V. (GitHub Pages), Vijzelstraat 68-72,
     1017 HL Amsterdam, Pays-Bas — https://support.github.com (une seule
     constante, `HEBERGEUR` dans `app.js`) ;
   - **Données personnelles** : aucune collecte (ni compte, ni formulaire,
     ni cookie, ni publicité, ni mesure d’audience), aucune page n'appelle un
     autre site ; restent sur l'appareil le refus de l'invitation à installer
     l'appli (`localStorage`, `appli.js`) et la copie hors ligne (`sw.js`) ;
     GitHub traite l'adresse IP comme tout hébergeur. **Ce paragraphe décrit
     le code** : un changement du moteur qui appelle un autre site (une
     police en ligne, une mesure d'audience, un formulaire) ou stocke autre
     chose doit le réécrire dans le même commit ;
   - **Fait avec Encrine** : outil libre (MIT) ; « Encrine n’est pas
     l’éditeur de ce site et n’en a pas vérifié le contenu » ;
   - **Contenu** : `partage.licence` (et `licence_note`) s'il existe, la
     classe d'origine (`origine`), le lien vers la page des crédits.

Le modèle est celui des jeux de Ludea (« Made with Ludea + legal notice »).
Le texte **n'a pas été relu par un juriste** : il reprend les mentions
qu'impose la LCEN (art. 6, III) à un site personnel, où un particulier peut
ne pas publier son nom quand l'hébergeur est nommé. Ne pas l'écrire sur le
site ; le dire si l'enseignant pose la question.

## Le déploiement

- Pages déploie **la branche `main`**. Un travail sur une autre branche n'est
  visible qu'une fois fusionné ; « le site n'est pas à jour » vient presque
  toujours de là, ou d'un workflow rouge.
- Le workflow échoue volontairement si un cahier déborde
  (`verifier-pagination.py`) : réparer la fiche, ne pas retirer l'étape.
- Les PDF ne sont jamais versionnés.
- **Ne dire « c'est en ligne » qu'après l'avoir vu en ligne.** Le site a déjà
  été annoncé déployé alors qu'il ne l'était pas. Le déploiement suit le push
  d'environ trois minutes ; vérifier ensuite la page (HTTP 200), que le
  fichier servi est bien celui du dépôt (même empreinte), et télécharger puis
  ouvrir un PDF.

## Contrôles

```sh
python3 scripts/classe.py verifier
node --check site/app.js && node --check site/commun.js && node --check site/modele.js && node --check site/gabarits.js
```

puis l'application servie en local (skill charte-graphique, « Vérifier une
retouche de l'écran ») : accueil (la mention « zone X » de la frise), une
progression, une évaluation, à 1280 px et 400 px.
