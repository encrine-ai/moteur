---
name: site-et-calendrier
description: L'application web de Ma Grande Section (site/, JavaScript sans cadriciel, publiée sur GitHub Pages) et le calendrier scolaire qui la date — la zone de vacances de la classe (A, B ou C), le calendrier officiel de chaque année dans le moteur, périodes, liste des documents, vue d'impression, déploiement. À utiliser pour ajouter ou renommer un document dans le menu, changer de zone ou d'année scolaire, mettre à jour les dates de vacances, corriger le calcul des périodes ou des semaines, toucher à classe.yml, commun.js, app.js, imprimer.html ou au workflow .github/workflows/pages.yml, ou comprendre pourquoi le site déployé ne montre pas une modification. Se déclenche aussi sans nom de fichier : « passe le site en 2027-2028 », « les dates des vacances d'hiver sont fausses pour la zone C », « on est en zone B, pas en C », « ajoute le document sur les sorties au menu », « le site n'est pas à jour », « le bouton PDF ne marche pas », « la période en cours n'est pas la bonne ». Pour l'apparence, voir charte-graphique ; pour la fabrication des PDF, imprimer-pdf.
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
| `site/app.js` | l'application : menu, accueil (frise, matériel, documents), rendu d'un document, boutons PDF (`pdf/<doc>.pdf`, `pdf/<doc>-periode-N.pdf`) ; aucun sélecteur de zone |
| `site/imprimer.html` | la vue que Chromium imprime : `?doc=…[&periode=N]`, aux dates de la zone de la classe |
| `.github/workflows/pages.yml` | à chaque push sur `main` : contrôler `classe.yml`, assembler `_site/`, fabriquer les PDF (un par document et par extrait de période, plus les cahiers : 65 pour une classe de Grande Section complète), contrôler la pagination, publier |

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
dépôt, « n'a aucun intérêt ».

Deux défauts déjà rencontrés : un bouton PDF à `display: inline-block`
annulait son attribut `hidden` et s'affichait, inerte, sur toutes les pages
(commit « Correction : boutons PDF inertes visibles hors des pages
concernées ») — vérifier qu'un élément masqué l'est vraiment ; et une favicon
SVG en *data URI* non échappée, remplacée par de vrais fichiers
(`site/favicon.ico`).

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
node --check site/app.js site/commun.js
```

puis l'application servie en local (skill charte-graphique, « Vérifier une
retouche de l'écran ») : accueil (la mention « zone X » de la frise), une
progression, une évaluation, à 1280 px et 400 px.
