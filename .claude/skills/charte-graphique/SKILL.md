---
name: charte-graphique
description: La charte « Carnet de terrain » de Ma Grande Section — couleurs des cinq périodes, trois polices (titres, texte de l'adulte, mots de l'enfant), icônes, composants de l'application et du papier — et son miroir publié, le design system Claude « Carnet de terrain ». À utiliser dès qu'on touche à l'apparence de quoi que ce soit : site/charte/, site/app.css, site/index.html, l'accueil (app.js), fiches.css, imagier.css, cartes-corpus.css, impression.css, une nouvelle page ou un nouveau composant, une icône de l'interface, une couleur, une police. Se déclenche aussi sans nom de fichier : « c'est moche », « rends l'accueil plus clair », « la couleur de la montagne ne va pas », « je voudrais un mode sombre », « ajoute un bouton pour… », « le titre est trop gros sur téléphone », « mets la charte à jour dans Claude Design ». Ne concerne pas le choix d'une image de fiche (fiches-illustrations) ni d'une photographie de l'imagier (imagier-photos).
---

# La charte graphique

Un papier légèrement vert, une encre de sapin, et **une couleur par milieu**,
qui dit la période sans jamais être seule à le dire. La charte habille deux
mondes aux règles différentes : **l'écran** de l'enseignante et **le papier**
de la classe (photocopié en noir et blanc, découpé, plastifié).

## Où elle vit

| Chemin | Rôle |
|---|---|
| `site/charte/socle.css` | **le socle**, commun à toutes les classes : Andika (`--police-enfant`), espacements, rayons, et la mécanique `data-periode` qui pose `--periode` à partir des `--pN` du thème |
| `site/charte/themes/faune-flore/theme.css` | **le style du thème** — ici « faune et flore », la charte « Carnet de terrain » : jetons de couleur (clair, sombre, impression), couleurs des cinq périodes, polices de l'adulte (`--police-titre`, `--police-texte`), ombre ; ses polices dans `polices/` à côté |
| `site/charte/charte.css` | **fabriqué** par `python3 scripts/classe.py generer` : le socle puis le thème que nomme `theme:` dans `classe.yml`, ses `url()` réécrites. C'est le seul fichier que chargent les pages ; ne jamais l'éditer à la main, `classe.py verifier` le refuserait |
| `site/charte/polices/` | Andika, auto-hébergée (le PDF se fabrique sans réseau), OFL |
| `site/charte/icones.svg` | le sprite des icônes Lucide, fabriqué par `scripts/generer-icones.py` : les icônes génériques listées dans le script, celles des milieux tirées de `periodes[].icone` dans `classe.yml` |
| `site/app.css`, `fiches/fiches.css`, `imagier/imagier.css`, `cartes-corpus/cartes-corpus.css`, `impression.css` | les composants, qui n'emploient que des jetons |
| design system « Carnet de terrain » | le miroir publié dans Claude : https://claude.ai/artifact/Lrda8LZTUsfNNPGtenscvC |

Chaque page charge `charte/charte.css` **avant** sa propre feuille. Une
couleur écrite en dur dans une feuille de composant est un défaut : elle ne
suit ni le thème sombre, ni la période.

### Ce qui va dans le socle, ce qui va dans le thème

Le socle porte ce qui sert la lecture et l'impression quel que soit le thème
(Andika, les espacements, les rayons, la mécanique des périodes). Le thème
porte tout ce qui donne un visage à la classe : chaque couleur, y compris les
neutres, l'encre, la couleur d'action et l'alerte, et ses trois blocs (clair,
sombre, impression), ainsi que les polices de l'adulte. Une page ne nomme
jamais le dossier d'un thème : elle charge `charte.css` (`classe.py verifier`
refuse `themes/<thème>` écrit dans `site/*.html` ou `site/*.js`).

### Ajouter un thème

1. Copier `site/charte/themes/faune-flore/` sous un nouveau nom
   (`themes/contes/`…), avec ses polices.
2. Y redéfinir **tous** les jetons du thème, dans les trois blocs (clair,
   sombre, impression) : `--papier` … `--anneau`, `--p1` … `--p5` avec leurs
   `-trait` et `-pale`, `--sur-periode`, `--police-titre`, `--police-texte`,
   `--ombre-flotte`. Un jeton oublié retombe sur rien, pas sur l'ancien
   thème.
3. Les couleurs de période gardent un nom de famille que l'enseignante peut
   dire (« le filet bleu ») : le noter dans `periodes[].couleur` de
   `classe.yml`, et les icônes des milieux dans `periodes[].icone` (puis
   `scripts/generer-icones.py`, qui demande le réseau).
4. `theme: <nom>` dans `classe.yml`, `python3 scripts/classe.py generer`,
   puis finir par le PDF (skill imprimer-pdf) : contrastes, pagination.

## Les règles, et d'où elles viennent

1. **Une couleur par période, et jamais seule.** `p1` bleu (la ville), `p2`
   vert (la forêt), `p3` violet (la montagne), `p4` ocre (la campagne), `p5`
   turquoise (la mer), chacune avec `-trait` et `-pale`. Un bloc la reçoit par
   `data-periode="N"`, qui pose `--periode`, `--periode-trait`,
   `--periode-pale`. Le nom du milieu ou « P2 » l'accompagne toujours : les
   fiches se photocopient en noir et blanc.
2. **On ne change pas la famille d'une teinte.** Les modes d'emploi imprimés
   de l'imagier et des cartes-corpus disent « la barquette repérée par le
   filet bleu » : les classes ont rangé leurs cartes ainsi. On peut foncer un
   bleu pour le contraste, pas le rendre rouge. (La première version de la
   charte avait choisi brique, mousse, glacier, blé, lagon ; elle a été
   reprise sur les couleurs déjà imprimées.)
3. **Trois polices, trois rôles.** `--police-titre` (Bricolage Grotesque) pour
   les titres de l'adulte ; `--police-texte` (Atkinson Hyperlegible Next) pour
   tout le texte de l'adulte ; `--police-enfant` (Andika) pour **tout mot
   qu'un enfant lit** — cartes, étiquettes, mots sous les images, lettres. Sur
   une fiche, la consigne reste en Atkinson, les mots de l'exercice passent en
   Andika : c'est l'écriture script de la classe (a et g à un étage).
4. **Pas d'émoji dans l'interface.** Les icônes de l'écran sont des Lucide
   (ISC) ; ajouter une icône = l'inscrire dans `ICONES` de
   `scripts/generer-icones.py` et relancer. Sur une fiche, jamais d'icône
   Lucide : des pictogrammes Mulberry ou ARASAAC (skill fiches-illustrations).
   Les émojis présents dans le texte Markdown des documents sont du contenu.
5. **Le papier reste clair.** `charte.css` remet les jetons clairs sous
   `@media print` ; le thème sombre ne concerne que l'écran.
6. **Contraste.** Tout texte tient 4,5:1 sur le fond que nomme son usage, dans
   les deux thèmes ; un bord de contrôle 3:1 (`trait-fort`). `bouton-dor` ne
   porte jamais de texte sur fond clair : il marque *aujourd'hui*, rien d'autre.
7. **Une mise en page imprimée se juge au PDF.** Changer une police, une
   taille ou une marge dans une feuille du papier change la pagination. Après
   toute retouche de `fiches.css`, `imagier.css`, `cartes-corpus.css`,
   `impression.css` ou de `charte.css`, passer par le skill
   [`imprimer-pdf`](../imprimer-pdf/SKILL.md) : `verifier-pagination.py` doit
   répondre 0 anomalie. Le changement de polices de la charte a ainsi fait
   disparaître trois débordements et en a laissé un, qu'il a fallu resserrer à
   la main.

## Les composants de l'application

| Composant | Classes | Notes |
|---|---|---|
| Bandeau | `.bandeau`, `.marque`, `.marque-frise` | la marque = cinq bandes aux couleurs des périodes |
| Menu | `.sidebar`, `.menu-groupe`, `.groupe`, `a.actif` | les évaluations y portent une pastille de période |
| Bouton | `.btn`, `.btn-principal` | un seul principal par barre : le PDF du document |
| Pastille, badge | `.pastille[data-periode]`, `.zone-badge` | le badge porte les dates calculées de la zone de la classe ; à l'accueil, la mention discrète « zone X » |
| Frise | `.frise`, `.frise-periode.en-cours`, `.frise-ici` | une bande par période, `flex-grow` = semaines |
| Matériel | `.materiels`, `.materiel.en-cours` | 2 colonnes, la période en cours (ou à venir) en tête et sur toute la largeur |
| Document | `.contenu[data-periode]` | le Markdown rendu ; une évaluation prend la couleur de sa période |

Disposition : cinq cartes dans une grille ne doivent jamais en laisser une
seule sur sa rangée — c'est pourquoi la première prend toute la largeur.
Gouttière de 16 px au moins à toutes les largeurs, aucun défilement
horizontal, essai à 400 px de large.

## Vérifier une retouche de l'écran

```sh
mkdir -p /tmp/site/content && cp -r site/. /tmp/site/ \
  && cp 01-*.md 02-*.md /tmp/site/content/ && cp -r 03-progressions 04-evaluations /tmp/site/content/
(cd /tmp/site && python3 -m http.server 8765 &)
```

Puis une capture Playwright (Node : `require('playwright')`, le Chromium est
déjà installé) à 1280 px et à 400 px, en `colorScheme: 'light'` **et**
`'dark'`, de l'accueil, d'une progression et d'une évaluation. Regarder les
captures avant de commiter.

## Tenir le miroir à jour

Le design system publié dans Claude reprend les jetons du socle et du thème de la classe (ici « faune et flore »), les règles
ci-dessus (README) et les composants (aperçus). Quand une valeur ou une règle
change ici, mettre à jour l'artefact (outil Artifact, `read` puis `publish`
sur son URL, en ne renvoyant que les fichiers modifiés, `tokens.json` en
entier) ; et inversement, une retouche faite dans Claude Design se reporte
dans `socle.css` ou `theme.css`. La charte du dépôt fait foi en cas d'écart.
