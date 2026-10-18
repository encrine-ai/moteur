---
name: charte-graphique
description: Le design system de la classe — le socle commun à toutes les classes (police de l'élève, contrastes, papier, mécanique des périodes) et le thème propre à la classe, qui fait de son site un MINI-SITE à son image (gabarits de l'en-tête et du menu, de l'accueil, des documents et des pages de période ; images libres créditées ; mouvement ; couleurs, polices, habillage, couverture), contrôlé par scripts/verifier-theme.py et verifier-gabarits.js. À utiliser dès qu'on touche à l'apparence de quoi que ce soit : site/charte/ (socle.css, composants.css, themes/ : theme.yml, theme.css, habillage.css, gabarits.js), site/gabarits.js, site/modele.js, site/app.css, site/index.html, l'accueil, fiches.css, imagier.css, cartes-corpus.css, impression.css, la couverture des cahiers, une nouvelle page ou un nouveau composant, une icône, une couleur, une police — et pour créer ou faire évoluer le style d'une classe avec son enseignant. Se déclenche aussi sans nom de fichier : « c'est moche », « je voudrais un style à nous », « rends l'accueil plus gai », « la couleur de l'Asie ne va pas », « je voudrais un mode sombre », « ajoute un bouton pour… », « le titre est trop gros sur téléphone », « on peut avoir une vraie couverture ? », « je voudrais que le site ressemble à notre projet », « fais-nous un vrai site », « construis le thème de la maquette retenue ». Ne concerne pas le choix d'une image de fiche (fiches-illustrations) ni d'une photographie de l'imagier (imagier-photos).
---

# Le design system de la classe

**Chaque classe a son propre style**, fait sur mesure avec son enseignant,
pour que la galerie « Les classes » montre des classes vraiment différentes
(décision du propriétaire, 18 octobre 2026). Mais toutes les classes
partagent ce qui sert l'enfant et le papier. D'où trois couches :

| Couche | Où | Qui la change |
|---|---|---|
| **le socle** | `site/charte/socle.css` (+ Andika dans `site/charte/polices/`) | le moteur seul ; aucun thème ne le défait |
| **les composants du moteur** | `site/app.css`, `site/impression.css`, `site/fiches/fiches.css`, `site/imagier/imagier.css`, `site/cartes-corpus/cartes-corpus.css`, `site/charte/composants.css` (la couverture) — tous dans `@layer moteur` | le moteur ; ils n'emploient que des jetons |
| **le thème de la classe** | `site/charte/themes/<thème>/` : `theme.yml`, `theme.css`, `habillage.css`, `gabarits.js`, `polices/`, `motifs/`, `images/` | la classe, avec son enseignant |

`python3 scripts/classe.py generer` assemble `socle.css`, `composants.css`,
puis `theme.css` et `habillage.css` du thème que nomme `theme:` dans
`classe.yml`, dans **`site/charte/charte.css`**, le seul fichier que chargent
les pages (jamais à éditer à la main ; `classe.py verifier` le refuse périmé).
Une page ne nomme jamais le dossier d'un thème.

**Pourquoi une couche CSS.** Les feuilles du moteur sont dans `@layer moteur` ;
le thème, hors couche, l'emporte donc sur elles **sans surenchère de
sélecteurs**, et un `style` écrit dans une fiche (une fiche resserrée à la
main) l'emporte sur les deux. Le socle est hors couche lui aussi : c'est le
contrôle qui empêche le thème d'y toucher.

**Deux supports, deux règles.** À l'écran, le thème fait un **mini-site** :
ses gabarits dessinent l'en-tête et le menu, l'accueil, la page de document
et la page de chaque période, avec ses images et son mouvement — « comme un
site différent, à son image » (décision du propriétaire, 18 octobre 2026).
Sur le papier (fiches, imagier, cartes-corpus, PDF des documents), le thème
**habille, il ne restructure pas** : couleurs, polices de l'adulte,
ornements, couverture, jamais la géométrie. C'est ce qui permet à une classe
de recevoir les nouvelles versions du moteur (skill synchroniser-moteur)
sans perdre son style : le moteur garde ses accroches et le contrat des
gabarits ; tout le reste lui est interne et peut changer.

## Le socle — non négociable

1. **La police de l'élève.** Andika (`--police-enfant`) pour tout mot qu'un
   enfant lit : cartes, étiquettes, étiquettes de tri, mots sous les images,
   lettres, tableaux, défis, le nom du milieu sur la couverture. La règle et
   sa liste de sélecteurs sont dans `socle.css`. Le thème ne touche ni à la
   police, ni au corps, ni à l'espacement, ni à la casse de ces mots, et leur
   couleur reste l'encre ou la période. La consigne, l'en-tête et le pied
   d'une fiche s'adressent à l'adulte : police du texte.
2. **La lisibilité.** Tout texte tient 4,5:1 sur le fond que nomme son usage,
   3:1 pour un bord de contrôle, dans les trois blocs (clair, sombre,
   impression). Le bloc d'impression est celui de la photocopie en noir et
   blanc : le rapport de luminance est tout ce qui y reste. La mention de
   rangement des cartes a un corps et une encre minimaux
   (`--repere-taille: 6.5pt`, `--repere-encre`) : à 5,5 pt en gris pâle,
   elle ne se lisait plus.
3. **Le papier.** A4, une page par fiche et par planche (les `@page` sont du
   moteur, le thème n'en écrit pas), aucun saut de page dans un thème. **Peu
   d'encre** sur ce que la classe photocopie : les fonds du papier restent
   clairs (luminance ≥ 0,70), un aplat sombre ne va qu'à l'écran et sur la
   couverture. Sur le papier, l'habillage ne change que l'apparence, jamais
   la géométrie ; un ornement y est toujours en position absolue.
4. **La mécanique des périodes.** `data-periode="N"` pose `--periode`,
   `--periode-trait`, `--periode-pale` à partir des `--pN` du thème. Les
   espacements (`--esp-*`) sont du socle aussi.

## Le contrat du thème — ce qu'il habille

### Les jetons (`theme.css`)

Trois blocs, chacun complet (un jeton oublié retombe sur rien) : `:root`
(clair), le sombre (`@media (prefers-color-scheme: dark)` sur
`:root:not([data-theme="light"])`, et `:root[data-theme="dark"]`), et
`@media print` (le papier reste clair).

| Jetons | Rôle |
|---|---|
| `--papier`, `--feuille`, `--feuille-creuse`, `--trait`, `--trait-fort` | fonds et traits |
| `--encre`, `--encre-douce` | texte, légendes |
| `--sapin`, `--sapin-pale`, `--sur-sapin` | la couleur de la maison (le nom est historique) : titres, action principale, état actif |
| `--bouton-dor`, `--sur-bouton-dor` | la mise en avant (*aujourd'hui*, le défi) — jamais de texte posé dessus sur fond clair |
| `--coquelicot`, `--anneau` | l'alerte, l'anneau de focus |
| `--p1`…`--p5` avec `-trait` et `-pale`, `--sur-periode` | une couleur par période |
| `--police-titre`, `--police-texte` (obligatoires), `--police-etiquette` (facultative : numéros, tampons, étiquettes ; par défaut celle des titres) | les polices de l'adulte, auto-hébergées |
| `--rayon-s`, `--rayon-m`, `--rayon-l`, `--rayon-pilule` | les arrondis — du thème, plus du socle |
| `--ombre-flotte` | ce qui flotte |
| `--consigne-fond/-bord/-encre/-accent`, `--sous-objectif-fond/-bord/-encre`, `--defi-fond/-bord/-accent`, `--fiche-cadre`, `--trait-coupe`, `--entete-planche-encre` | **accroches** du papier : le moteur les lit avec une valeur par défaut tirée de la charte (la consigne sur `--feuille-creuse`, le sous-objectif à la couleur de la période, le défi bordé de `--bouton-dor`) |
| `--t-…` | les variables propres au thème (`--t-kraft`) |

Les couleurs de période gardent une **famille** que l'enseignant peut dire
(« le filet bleu ») : elle est notée dans `periodes[].couleur` de
`classe.yml`, et les modes d'emploi imprimés la citent. On peut foncer ou
nuancer une teinte, pas en changer la famille.

### Les composants (`habillage.css`)

Chaque règle part d'une **racine** que le moteur garantit et ne nomme que
les **parties** listées. `scripts/verifier-theme.py` tient le même registre
(`COMPOSANTS`) : une racine ou une partie qui n'y est pas est refusée.

Les six premières lignes (bandeau, menu, barre, accueil, bloc, frise) et
les cartes du matériel et des documents sont les composants des **gabarits
par défaut** (`site/gabarits.js`) : un thème sans gabarits les habille ici ;
un thème qui a ses gabarits dessine les siens (« Le mini-site », plus bas).

| Composant | Racine | Parties | Ornements | Support |
|---|---|---|---|---|
| Bandeau | `[data-composant="bandeau"]` | `.marque`, `.marque-frise` (`.m1`…`.m5`), `.marque-texte`, `.marque-titre`, `.marque-sous`, `.menu-toggle`, `.ic` | `bandeau` | écran |
| Menu | `[data-composant="menu"]` | `.menu-groupe`, `.groupe`, `.actif`, `.pastille`, `.ic` | | écran |
| Barre d'outils | `[data-composant="barre"]` | `.fil`, `.boutons`, `.btn`, `.btn-principal` | | écran |
| Accueil (la page) | `[data-composant="accueil"]` | | | écran |
| En-tête de l'accueil | `[data-composant="accueil-tete"]` | `.surtitre`, `.chapo`, `h1` | `accueil` | écran |
| Bloc de l'accueil | `[data-composant="bloc"]` (+ `[data-bloc="annee|materiel|documents"]`) | `.bloc-tete`, `.zone-badge`, `.note`, `.vacances`, `.reprise`, `.materiels`, `.frise-total` | `::before`, `::after` | écran |
| Frise des périodes | `[data-composant="frise"]` | `.frise-periode`, `.en-cours`, `.frise-bande`, `.frise-num`, `.frise-milieu`, `.frise-dates`, `.frise-sem`, `.frise-ici` | `frise` (dans chaque bande) | écran |
| Carte d'un cahier à imprimer | `[data-composant="materiel"]` | `.materiel-tete`, `.materiel-num`, `.materiel-liste`, `.en-cours` | `materiel` | écran |
| Cartes des documents | `[data-composant="documents"]` | `.docs-groupe`, `.docs` | | écran |
| Document rendu | `[data-composant="document"]` | `.contenu`, `.zone-badge` | | écran |
| Invitation à installer l'appli | `[data-composant="invitation"]` | `.invitation-icone`, `.invitation-texte`, `.invitation-fermer`, `.btn`, `.btn-principal`, `.ic` | | écran |
| Pied, pastille, bouton | `[data-composant="pied"]`, `.pastille`, `.btn` | `.btn-principal` | | écran |
| **Couverture** d'un cahier | `[data-composant="couverture"]` (+ `data-periode`, `data-cle`) | `.couverture-tete`, `-classe`, `-annee`, `-centre`, `-cahier`, `-titre` (mot de l'enfant), `-sous`, `-pied`, `-periode`, `-num`, `-projet` | `couverture-fond`, `couverture-embleme`, `couverture-tampon` | papier |
| Page de garde | `[data-composant="garde"]` | `.sous-titre`, `.encadre`, `.titre-encadre`, `.trois-temps`, `.temps`, `.usages`, `.quand`, `.listes`, `.savant`, `.pied-garde`, `.note` | `garde` | papier |
| En-tête de planche | `[data-composant="entete-planche"]` | `.milieu` | | papier |
| Carte d'imagier | `[data-composant="carte-imagier"]` | `.photo`, `.mot`, `.vide`, `.repere` | `::before`, `::after` | papier |
| Carte-corpus | `[data-composant="carte-corpus"]` | `.visuel`, `.photo`, `.dessin`, `.mot`, `.vide`, `.repere` | `::before`, `::after` | papier |
| Étiquette-mot, étiquette de tri | `[data-composant="etiquette"]`, `[data-composant="etiquette-tri"]` | `.mot`, `.repere` ; `.mot-tri` | `::before`, `::after` | papier |
| Crédits | `[data-composant="credits"]` | | | papier |
| Fiche élève (écrite à la main) | `.fiche` | le **cadre** seulement : `.entete`, `.idext`, `.champ`, `.trait`, `.cartouche`, `.ref`, `.dom`, `.titre`, `.niveau`, `.n1`, `.n2`, `.sous-objectif`, `.consigne`, `.exo`, `.num`, `.enonce`, `.defi`, `.etoile`, `.pied-fiche`, `.codage`, `.paysage` — jamais le matériel de l'exercice | `::before`, `::after` | papier |
| Document imprimé | `[data-composant="bandeau-imprime"]`, `[data-composant="document-imprime"]` | `.zone-badge` | | papier |

Les **étiquettes de période** sont la `.pastille` (écran), le `.cartouche`
de la fiche, l'en-tête de planche et le `.repere` des cartes ; les **motifs
décoratifs** sont les fonds (`body[data-support="ecran"]` pour le fond de
l'écran, `background-image`), les filets et les ornements.

Attributs de contexte permis partout : `data-periode` (un motif par
continent), `data-support="ecran|papier"` (sur `<body>`), `data-cahier`
(`imagier`, `cartes-corpus`), `data-bloc`, `data-cle` (la clé du milieu, sur
la couverture), `data-theme`.

**Les ornements** sont des éléments vides (`<span class="orne"
data-orne="…">`) que le moteur pose et que le socle cache (`display: none`).
Un thème les montre et les remplit (`display: block; position: absolute;`
un motif en `mask` ou `background`). Leur hôte est déjà positionné et isolé
(`position: relative; isolation: isolate`), si bien qu'un `z-index: -1` les
passe sous le texte. Les `::before`/`::after` des parties servent
d'ornements supplémentaires.

### Ce que vérifie `scripts/verifier-theme.py` (code 1 s'il reste une anomalie)

Lancé par `python3 scripts/classe.py verifier` (donc par le déploiement), ou
seul : `python3 scripts/verifier-theme.py [thème…]`.

- **les fichiers** : `theme.yml` déclare chaque police et chaque motif, avec
  sa licence (OFL-1.1, CC0-1.0, PDM, CC-BY, CC-BY-SA) et son auteur ; chaque
  fichier déclaré existe et sert, chaque fichier du dossier est déclaré,
  chaque `url()` pointe sur un fichier déclaré, aucune ne sort sur le réseau
  (les PDF se fabriquent sans lui) ; un motif SVG ne contient ni script, ni
  image, ni texte, ni lien externe ;
- **les jetons** : complets dans les trois blocs ; `--police-titre`,
  `--police-texte`, `--police-etiquette` commencent par une police
  auto-hébergée (un `@font-face` du thème) ;
- **le contraste** : les paires d'usage (encre sur papier et sur feuille,
  période sur sa teinte pâle, texte sur la couleur de la maison, accroches
  de la fiche…, plus les `contrastes:` de `theme.yml`) dans les trois
  blocs ; au bloc d'impression, des fonds de papier clairs ;
- **le socle** : ni `--police-enfant`, ni `--esp-*`, ni `--periode*`, ni
  `--repere-*` redéfinis ; aucune règle de police, de corps, d'espacement ou
  de casse sur un mot de l'enfant ; ni `@page`, ni `@import`, ni saut de
  page, ni `!important` ; une `font-family` passe toujours par un jeton ;
- **les composants** : racine connue, parties documentées, attributs de
  contexte ; sur le papier, des propriétés d'apparence seulement (couleurs,
  fonds, styles et couleurs de bordure, arrondis, polices de l'adulte,
  graisse, casse, soulignement), un ornement en position absolue, pas
  d'aplat sombre hors de la couverture — dont l'intérieur, à hauteur fixe,
  se compose librement ; à l'écran, tout, sauf un corps sous 12 px.

- **le mini-site** : les images de `theme.yml` (licence, auteur, source,
  fichier, usage) ; `gabarits.js` sans logique du moteur, et **essayé** par
  `scripts/verifier-gabarits.js` (Node) sur chaque page de la vraie classe —
  chaque gabarit rend du texte sans erreur, l'en-tête a son `<nav>` et son
  menu de téléphone, chaque `aria-controls` nomme un élément, chaque
  document montre son texte et ses PDF, chaque période ses cahiers et ses
  documents, chaque image a un `alt`, chaque bouton un `type`, le pied la
  signature, et chaque entrée du menu a un lien ; sans `gabarits.js`, ce
  sont les gabarits par défaut qu'il essaie ; l'habillage d'écran dans
  `@media screen` (ci-dessous) ; toute animation sous
  `prefers-reduced-motion: no-preference`.

Il ne dit pas qu'un style est beau ni que la pagination tient : **cela se
regarde**, aux captures et au PDF (skill imprimer-pdf).

## Le mini-site : les gabarits du thème

Le moteur **calcule**, le thème **dessine**. `site/index.html` n'a plus que
trois emplacements — `#entete`, `#contenu` (`<main>`), `#pied` — et le lien
d'évitement ; à chaque page, `site/app.js` les fait remplir par les
gabarits, puis donne vie au menu. Il n'y a plus de bandeau (nom de la
classe, année, logo, burger) : **le menu est dans l'en-tête**, et le pied
porte la signature **« Conçu avec Encrine »**, liée à https://encrine.ai.

| Fichier | Rôle |
|---|---|
| `site/modele.js` | `GS.modele()` : le modèle que reçoivent les gabarits (ci-dessous) |
| `site/gabarits.js` | les **gabarits par défaut**, sobres ; `GS.theme({…})`, que le thème appelle |
| `themes/<thème>/gabarits.js` | les gabarits du thème : tout ou partie des fonctions ; `classe.py generer` le copie dans `site/charte/gabarits.js` (fabriqué, chargé après ceux du moteur) |
| `site/app.js` | la logique : routes, lecture et rendu du Markdown, extraits par période, menu, focus, crédits — un thème n'y touche pas |
| `scripts/verifier-gabarits.js` | essaie les gabarits sur la vraie classe, avec Node (lancé par `verifier-theme.py`) |

### L'API des gabarits

Un gabarit est une fonction `(m, page) → HTML` (une chaîne), sans cadriciel.

- **Attendus** : `entete`, `accueil`, `document`, `periode`, `pied` ;
  **facultatifs** : `introuvable`, et `monter(racine, m, page)`, appelé après
  chaque rendu (le mouvement, une interaction de pure forme). Le thème ne
  fournit que ce qu'il change : `GS.theme({ accueil: …, periode: … })` ; le
  reste vient des gabarits par défaut, qu'il peut aussi appeler
  (`GS.gabarits.defaut.boutons(m, page)`, `.extraits(m, page)`).
- **`page`** : `{type: 'accueil'}` ; `{type: 'document', doc, periode,
  titre, corps, html, sections}` — `html` est le Markdown rendu, `corps` le
  même sans son titre, `sections` les `h2` (`id`, `titre`, `periode`), les
  badges de dates de la zone déjà posés ; `{type: 'periode', periode}` ;
  `{type: 'credits', …}` (rendu par `document`) ; `{type: 'introuvable'}`.
- **`m`, le modèle** : `m.classe` (nom, projet, niveau, annee, accroche,
  zone, periodes_nom, origine, **enseignant** : signature, mot) ;
  `m.periodes[]` (n, cle, milieu, icone, romain, lien `#/periode/<cle>`,
  debut, fin, sem, `dates.court|long|badge`, statut `passee|en-cours|a-venir`,
  prochaine, **cahiers** avec `href` et `nom` de leur PDF, **documents** de
  la période, **extraits** des progressions, **projet**, **embleme**,
  **imagier** `{faune, flore}`, **corpus**, **theme** — les données propres
  au thème, prete) ; `m.ici` (statut `periode|vacances|avant|apres`,
  periode, vacances, prochaine, titre « Nous y sommes », texte) ;
  `m.vacances[]` (nom, libelle, dates, reprise, enCours) ; `m.ponts`,
  `m.annee` (semaines, texte) ; `m.menu[]` (groupes et entrées, avec le
  groupe des périodes) ; `m.documents`, `m.groupes` (chaque document avec
  `pdf` et `extraits`) ; `m.sortes`, `m.materielNote` ; `m.projet` ;
  `m.images`, `m.image(fichier)` (chemin, crédit) ; `m.signature` ;
  `m.pied` (conformite, calendrier, credits) ; `m.mouvement` (faux si
  `prefers-reduced-motion`) ; `m.outils` (esc, texte, icone, pastille,
  romain, nombre, jourLong, jourCourt). Un gabarit **échappe** tout texte
  (`esc`, ou `texte` qui ne permet que `*italique*` et `**gras**`).
- **Les accroches du menu**, que `app.js` anime : `[data-sous-menu]` +
  `aria-controls` (un sous-menu, `hidden` ; un seul ouvert ; Échap, un clic
  ailleurs ou le focus qui part le ferment) ; `[data-menu-ouvrir]` +
  `aria-controls` vers `[data-menu-panneau]` (le menu du téléphone, un
  dialogue `role="dialog" aria-modal="true"` : le focus y entre et y reste,
  Échap le ferme et rend le focus au bouton) ; `[data-menu-fermer]`. Le
  moteur pose `aria-current="page"` sur chaque lien de la page affichée et
  `data-actif` sur le bouton du sous-menu qui la contient. Une ancre
  `href="#id"` (sommaire, renvoi) défile sans changer de page.
- **Le moteur garantit** : le lien d'évitement, le focus sur `<main>` à
  chaque page, le titre de l'onglet, la signature « Conçu avec Encrine »,
  le lien des crédits (`#/credits`) et le crédit de la classe d'origine
  (CC BY) — un pied qui les oublie les reçoit sous leur forme sobre —, et
  l'invitation à installer l'appli (`appli.js`, composant `invitation`).
- **Interdit à un gabarit** (refusé par `verifier-theme.py`) : lire
  (`fetch`, `import`), stocker (`localStorage`…), changer la route, écouter
  le clavier, écrire `<script>` ou `on…=`, nommer une adresse extérieure.
  Animer (`requestAnimationFrame`, `setInterval`, `.animate`) seulement en
  lisant `m.mouvement`.

**Les gabarits par défaut** — ceux du thème neutre `demo` — font un site
sobre : en-tête avec le nom du projet et un sous-menu par groupe
(ordinateur), un bouton « Menu » qui ouvre le même menu en plein écran
(téléphone) ; l'accueil (projet, signature et mot de l'enseignant, frise de
l'année, vacances avec « Nous y sommes », cahiers à imprimer, documents) ;
le document (PDF, cahiers de la période, extraits, texte) ; la période (ce
qu'on y fait, fil rouge, cahiers, documents, projet, imagier, mots des
corpus) ; le pied (signature de la classe, conformité, crédits, « Conçu
avec Encrine »).

### La page de période

`#/periode/<clé>` existe pour chaque période, prête ou non : dates de la
zone, statut, **ses cahiers et leurs PDF**, **ses documents** (l'évaluation,
l'extrait de chaque progression), et **les données du projet** que porte
`classe/projet.yml` (`contenu: projet:` dans classe.yml) : `resume` (ce
qu'on y fait), `fil_rouge` ou `mascotte`, `albums`, `documentaires`,
`textes`, `oeuvres`, `musique`, `sorties`, `spectacle`, `embleme` (une image
déclarée, ou `{imagier: <slug>}`), et `theme:` — les données propres au
thème (pour un atlas : la position du continent sur la carte, ses repères).
L'imagier (espèces, photographie, crédit) et les mots des corpus viennent
des manifestes de la classe. `classe.py verifier` contrôle la forme du
fichier ; **on n'y met que ce que le projet annuel dit déjà** — une période
en esquisse a une page en esquisse.

### Les images du thème

`theme.yml`, section `images:` — une entrée par fichier de `images/` :

```yaml
images:
  - fichier: images/carte-du-monde.jpg
    titre: Mappemonde à l'usage du roi
    auteur: Guillaume Delisle
    date: vers 1750
    institution: Rijksmuseum
    source: https://id.rijksmuseum.nl/200450285
    licence: PDM          # CC0-1.0, PDM, CC-BY-x.0, CC-BY-SA-x.0 — jamais NC ni ND
    recadrage: cartouche allégorique effacé, recadré sur le trait
```

`verifier-theme.py` refuse une licence hors de ces quatre familles, un
auteur ou une source qui manque, Wikimedia, un fichier déclaré absent, un
fichier non déclaré, une image dont aucune feuille ni aucun gabarit ne se
sert. Les images de **contenu** (une œuvre étudiée, la gravure de la
mascotte) vont dans `classe/projet.yml` (`images:`, fichiers sous
`site/projet/`), avec les mêmes champs. Les **crédits s'affichent tout
seuls** : la page `#/credits` les liste (thème, projet, photographies de
l'imagier, polices), et le pied y renvoie.

**Sources** : Openverse en énumérant `license=cc0,pdm,by,by-sa` (jamais le
filtre `commercial`, qui laisse passer ND) ; Rijksmuseum
(`data.rijksmuseum.nl/search/collection`, puis l'objet Linked Art → `shows`
→ `digitally_shown_by` → `access_point`, une adresse IIIF micr.io :
`/full/1600,/0/default.jpg` ; un `User-Agent` de navigateur ou `curl`) ;
The Met Open Access (`collectionapi.metmuseum.org/public/collection/v1.1/search`,
`isPublicDomain`) ; Biodiversity Heritage Library. **Jamais Wikimedia.**

**À regarder à l'œil, toujours** : les cartes et gravures anciennes portent
des allégories (les continents en figures dénudées, des putti, l'enlèvement
d'Europe). Le site est pour des enfants de cinq ans : aucune figure
dénudée ni violente. Effacer le cartouche (papier nu, de la couleur du
papier voisin) et le dire dans `recadrage`, ou choisir une autre image —
la carte de Blaeu et l'Europe de Schenk, retenues en maquette pour l'atlas
de la démo, ont été écartées ainsi. Et **aucune illustration de contenu
dessinée** : une image vient d'une source libre, ou n'est pas.

### L'habillage du mini-site (`habillage.css`, `@media screen`)

Le HTML des gabarits du thème s'habille dans `habillage.css`, **dans un
bloc `@media screen { … }`** : il ne peut pas toucher le papier. Ses classes
y sont libres, sauf : jamais un composant du papier, jamais un élément nu à
la racine du sélecteur (il toucherait les fiches ouvertes à l'écran ; partir
d'une classe ou de `body[data-support="ecran"]`), `font-family` par les
jetons (`--police-titre|texte|etiquette|enfant`), 12 px au moins, et les
mots de l'enfant (`.mot-enfant` : un nom d'espèce, un mot de corpus) en
Andika — le thème en règle la taille, pas la police. Les règles **hors** de
ce bloc gardent le contrat des composants (ci-dessus).

**Le mouvement** : toute `animation` sous
`@media (prefers-reduced-motion: no-preference)`, tout script par
`m.mouvement` ; le moteur coupe de toute façon transitions et animations
quand l'enseignant l'a demandé.

**L'accessibilité** se vérifie, elle ne se suppose pas : tout au clavier
(lien d'évitement, sous-menus, menu du téléphone ouvert, parcouru, refermé
par Échap), 4,5:1 pour tout texte (les jetons privés aussi : les déclarer
dans `contrastes:` de `theme.yml`, par paires `[texte, fond]`), un `alt` à
chaque image (vide si elle est décorative), les mots de l'enfant en Andika.

### Construire le mini-site d'une classe à partir d'une maquette

La maquette retenue (skill nouvelle-classe, « Le style ») est du HTML
statique : on la **traduit** en thème, sans rien perdre des rubriques.

1. Lire la maquette, ses `NOTES.md` et `CREDITS.md`. Lister ses écrans
   (accueil, menu, document, période) et ce que chacun montre.
2. Écrire `classe/projet.yml` avec les données réelles (le projet annuel
   les porte) ; les données propres au thème sous `periodes.<clé>.theme`.
3. `themes/<nom>/theme.yml` (polices, images, icônes demandées, contrastes),
   `theme.css` (jetons ; les couleurs de période gardent leur **famille**,
   celle que citent les modes d'emploi imprimés), `gabarits.js` (une
   fonction par écran, à partir du HTML de la maquette, les données venant
   du modèle), `habillage.css` (le CSS de la maquette dans `@media screen`,
   les couleurs passées en jetons).
4. **Toutes les rubriques**, pas seulement les pages de la maquette : chaque
   progression, le projet, la programmation, les évaluations, chaque
   période (même en esquisse), les crédits, une page introuvable.
5. Le papier reste sobre : un thème peut ne rien habiller du papier (les
   gabarits n'y touchent jamais), ou reprendre l'habillage d'avant.
6. Contrôles : `classe.py generer` et `verifier` (dont `verifier-theme.py`
   et l'essai des gabarits), un parcours Playwright de chaque lien du menu
   à 390 et 1280 px dans un **sous-dossier** comme en production (aucune
   erreur, aucun 404, aucun débordement, menu au clavier), puis le PDF
   (`generer-pdf.sh`, `verifier-pagination.py` : même nombre de PDF et de
   pages qu'avant). Vider les caches du service worker entre deux essais
   (`serviceWorkers: 'block'` dans Playwright).
7. Relire les captures avec l'œil de l'enseignant : le niveau visé est
   celui de la maquette, ou mieux.

## Créer le design system d'une classe

C'est l'étape « Le style » du skill nouvelle-classe, qui en tient la marche
complète : **trois maquettes de mini-site radicalement différentes**, quatre
écrans chacune, sur le vrai contenu de la classe, une planche comparative,
le choix de l'enseignant — et **seulement ensuite** le thème choisi se
construit (« Construire le mini-site… », ci-dessus). La même marche sert à
faire évoluer un style.

Une fois le thème construit : `theme: <nom>` dans `classe.yml`,
`python3 scripts/classe.py generer` puis `verifier`, les icônes
(`periodes[].icone` et `icones:` de `theme.yml`, puis
`scripts/generer-icones.py`, qui demande le réseau), les icônes de l'appli
(refaites par `generer` depuis les couleurs et la police des titres du
thème), et le PDF (skill imprimer-pdf). Le verdict de l'enseignant s'écrit
dans le message de commit et dans `theme.yml` (`description`,
`retenu_le`) ; les directions écartées ne restent pas dans le dépôt.

**Polices** : Fontsource (`cdn.jsdelivr.net/npm/@fontsource/<nom>/…`, ou
`@fontsource-variable/<nom>` pour un fichier par sous-ensemble) ; lire la
licence dans son `package.json` (OFL-1.1) ; télécharger les sous-ensembles
`latin` et `latin-ext` en woff2 dans `polices/`, les déclarer avec leur
`unicode-range`. Jamais Andika dans un thème : elle est du socle.

**Motifs** : des tracés simples (filet, tampon, onde, perforation, coin,
ficelle) tracés soi-même en SVG (CC0, « tracé pour le thème »), ou des
motifs libres déclarés avec leur auteur. **Aucune illustration de contenu**
(animal, objet reconnaissable) : elles viennent des pictogrammes et des
photographies, selon leurs skills. Un motif en `mask` prend la couleur du
jeton qu'on lui donne (`background: var(--periode)`) : un seul fichier sert
les cinq périodes.

## Faire évoluer le style

- Une retouche de l'enseignant (« la couverture est trop chargée ») se fait
  dans le thème, jamais dans une feuille du moteur.
- Il manque une accroche (un composant, une partie, un ornement) : l'ajouter
  **au moteur**, de façon générique — l'attribut dans le HTML fabriqué, la
  partie dans `COMPOSANTS` de `verifier-theme.py`, la ligne du tableau
  ci-dessus — puis la remonter (skill remonter-au-moteur). Ne jamais
  renommer une accroche existante : les thèmes des classes en dépendent.
- Une couleur écrite en dur dans une feuille du moteur est un défaut : elle
  ne suit ni le thème, ni la période. La remplacer par un jeton, ou une
  accroche dont la valeur par défaut vient de la charte.

## La couverture des cahiers

L'imagier et les cartes-corpus s'ouvrent sur une couverture
(`classe.couverture()` dans `scripts/classe.py`) : une page de plus par
cahier ; `couverture: false` sur le cahier, dans `materiel` de `classe.yml`,
la retire. Les fiches élève, photocopiées une à une, n'en ont pas. Sa
structure est fixe ; sans thème elle est sobre (un cadre à la couleur de la
période, le milieu en grand, en Andika) ; un thème en fait une vraie
couverture. Hauteur 271 mm : 6 mm de tolérance, sinon elle pousse le cahier
d'une page.

## Les règles, et d'où elles viennent

1. **Une couleur par période, et jamais seule.** Le nom du milieu ou « P2 »
   l'accompagne toujours : les fiches se photocopient en noir et blanc.
2. **Pas d'émoji dans l'interface.** Les icônes de l'écran sont des Lucide
   (ISC), inscrites dans `ICONES` de `scripts/generer-icones.py`. Sur le
   papier, jamais d'icône Lucide : des pictogrammes (skill
   fiches-illustrations), ou les ornements du thème.
3. **Une mise en page imprimée se juge au PDF.** Après toute retouche du
   thème, de `fiches.css`, `imagier.css`, `cartes-corpus.css`,
   `impression.css`, `composants.css` ou du socle : skill imprimer-pdf,
   `verifier-pagination.py` à 0 anomalie, puis regarder les pages.

## Vérifier une retouche de l'écran

Assembler le site (skill imprimer-pdf, étape 1), le servir **dans un
sous-dossier** (`/<dépôt>/`, comme GitHub Pages), puis une capture
Playwright (Node : `require('playwright')`, le Chromium est dans
`/opt/pw-browsers`, `--no-proxy-server` pour le serveur local,
`serviceWorkers: 'block'` pour ne pas voir une vieille page) à 1280 et à
390 px, en `colorScheme: 'light'` **et** `'dark'` : l'accueil, le menu du
téléphone ouvert, une progression, une évaluation, une page de période, le
pied. `?date=AAAA-MM-JJ` dans l'adresse simule un jour (une période en
cours, des vacances). Gouttière de 16 px au moins, aucun défilement
horizontal, jamais une carte seule sur sa rangée. Regarder les captures
avant de commiter.

## Le miroir publié

Si la classe a publié son design system comme artefact de claude.ai (propre
à Claude), il reprend les jetons du thème, les règles ci-dessus et les
composants ; quand une valeur change ici, le mettre à jour (dans Claude
Code : outil Artifact, `read` puis `publish` sur son URL ; un agent qui n'a
pas cet outil le signale à l'enseignant). Le dépôt fait foi en cas d'écart.
