---
name: charte-graphique
description: Le design system de la classe — le socle commun à toutes les classes (police de l'élève, contrastes, papier, mécanique des périodes) et le thème propre à la classe (couleurs, polices de l'adulte, rayons, habillage des composants nommés, couverture, motifs et ornements), contrôlé par scripts/verifier-theme.py. À utiliser dès qu'on touche à l'apparence de quoi que ce soit : site/charte/ (socle.css, composants.css, themes/), site/app.css, site/index.html, l'accueil (app.js), fiches.css, imagier.css, cartes-corpus.css, impression.css, la couverture des cahiers, une nouvelle page ou un nouveau composant, une icône, une couleur, une police — et pour créer ou faire évoluer le style d'une classe avec son enseignant. Se déclenche aussi sans nom de fichier : « c'est moche », « je voudrais un style à nous », « rends l'accueil plus gai », « la couleur de l'Asie ne va pas », « je voudrais un mode sombre », « ajoute un bouton pour… », « le titre est trop gros sur téléphone », « on peut avoir une vraie couverture ? ». Ne concerne pas le choix d'une image de fiche (fiches-illustrations) ni d'une photographie de l'imagier (imagier-photos).
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
| **le thème de la classe** | `site/charte/themes/<thème>/` : `theme.yml`, `theme.css`, `habillage.css`, `polices/`, `motifs/` | la classe, avec son enseignant |

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

Le thème **habille, il ne restructure pas** : il ne réécrit aucun HTML. C'est
ce qui permet à une classe de recevoir les nouvelles versions du moteur
(skill synchroniser-moteur) sans perdre son style : le moteur s'engage à
garder les accroches ci-dessous ; tout le reste lui est interne et peut
changer.

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

Il ne dit pas qu'un style est beau ni que la pagination tient : **cela se
regarde**, aux captures et au PDF (skill imprimer-pdf).

## Créer le design system d'une classe

C'est l'étape « le style » du skill nouvelle-classe ; la même marche sert à
le faire évoluer.

1. **Une question, des univers.** Demander à l'enseignant ce qu'il aime
   (« plutôt carnet, affiche, album, atelier ? ») en partant du thème de
   l'année, avec deux ou trois exemples d'univers. **Pas de cliché** : pour
   le voyage, pas la carte au trésor ; pour la mer, pas l'ancre et le
   gouvernail. Chercher l'objet que manipule un enfant de cinq ans (le
   carnet, le tampon, l'étiquette de bagage).
2. **Deux ou trois directions nettement distinctes**, pas trois palettes du
   même gabarit : chacune avec ses polices (libres, OFL), son principe
   d'ornement, sa façon d'occuper la couverture, la frise, l'en-tête. Chaque
   direction est un dossier `themes/<nom>/` complet, que
   `verifier-theme.py` accepte. Partir de `themes/demo/` (neutre) ou du
   thème d'une autre classe.
3. **Les montrer sur de vraies pages** : l'accueil à 1280 et à 390 px, une
   fiche, une carte d'imagier, une couverture — à l'écran **et** au PDF
   (`--print-to-pdf`, puis `pdftoppm`, aussi en `-gray` pour la photocopie).
   Tant que la classe n'a pas de cahier, assembler une classe d'essai dans
   le scratchpad avec le contenu d'une autre classe ; jamais dans le dépôt.
4. **L'enseignant choisit et ajuste** ; son verdict s'écrit dans le message
   de commit et dans `theme.yml` (`description`, `retenu_le`). Les
   directions écartées ne restent pas dans le dépôt.
5. `theme: <nom>` dans `classe.yml`, `python3 scripts/classe.py generer`
   puis `verifier`, les icônes des milieux (`periodes[].icone`, puis
   `scripts/generer-icones.py`, qui demande le réseau), et le PDF (skill
   imprimer-pdf).

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

Assembler le site (skill imprimer-pdf, étape 1), le servir, puis une capture
Playwright (Node : `require('playwright')`, le Chromium est dans
`/opt/pw-browsers`) à 1280 et à 390 px, en `colorScheme: 'light'` **et**
`'dark'`, de l'accueil, d'une progression et d'une évaluation. Gouttière de
16 px au moins, aucun défilement horizontal, jamais une carte seule sur sa
rangée. Regarder les captures avant de commiter.

## Le miroir publié

Si la classe a publié son design system dans Claude (un artefact), il
reprend les jetons du thème, les règles ci-dessus et les composants ; quand
une valeur change ici, le mettre à jour (outil Artifact, `read` puis
`publish` sur son URL). Le dépôt fait foi en cas d'écart.
