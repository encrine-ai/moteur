---
name: site-et-calendrier
description: L'application web de Ma Grande Section (site/, JavaScript sans cadriciel, publiée sur GitHub Pages) et le calendrier scolaire qui la date — zones de vacances A, B, C, périodes, liste des documents, vue d'impression, déploiement. À utiliser pour ajouter ou renommer un document dans le menu, changer d'année scolaire ou mettre à jour les dates de vacances, corriger le calcul des périodes ou des semaines, toucher à classe.yml, commun.js, app.js, imprimer.html ou au workflow .github/workflows/pages.yml, ou comprendre pourquoi le site déployé ne montre pas une modification. Se déclenche aussi sans nom de fichier : « passe le site en 2027-2028 », « les dates des vacances d'hiver sont fausses pour la zone C », « ajoute le document sur les sorties au menu », « le site n'est pas à jour », « le bouton PDF ne marche pas », « la période en cours n'est pas la bonne ». Pour l'apparence, voir charte-graphique ; pour la fabrication des PDF, imprimer-pdf.
---

# Le site et le calendrier

Le site est une application d'une page, sans cadriciel, qui lit les documents
Markdown du dépôt et les rend avec `marked`. Rien n'est construit à l'avance,
sauf les PDF.

| Fichier | Rôle |
|---|---|
| `classe.yml` | **la classe** : nom, niveau, année, projet, **le calendrier**, les milieux des périodes, **la liste des documents**. La seule source de ce qui distingue cette classe d'une autre ; rien de tout cela ne s'écrit dans le code |
| `scripts/classe.py` | `generer` fabrique `site/classe.json` et `site/classe.js` (versionnés) ; `verifier` sort en code 1 si ces fichiers sont périmés, ou si une donnée de la classe — l'année, le projet, un milieu — est écrite en dur dans le moteur. Le déploiement le refait |
| `site/commun.js` | l'objet `GS`, bâti sur `CLASSE` : le calendrier (`CAL`), les milieux (`THEMES`, `ICONES_MILIEU`), les documents (`DOCS`), le préfixe des fichiers téléchargés, le calcul des périodes et le badge de dates. Partagé par l'application et la vue d'impression |
| `site/app.js` | l'application : menu, accueil (frise, matériel, documents), rendu d'un document, boutons PDF, zone mémorisée |
| `site/imprimer.html` | la vue que Chromium imprime : `?doc=…&zone=A|B|C[&periode=N]` |
| `.github/workflows/pages.yml` | à chaque push sur `main` : contrôler `classe.yml`, assembler `_site/`, fabriquer les 155 PDF, contrôler la pagination, publier |

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

`calendrier` (dans `classe.yml`) porte les dates **officielles** (jeu de données
[fr-en-calendrier-scolaire](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/)) :
rentrée, Toussaint et Noël (communes aux trois zones), hiver et printemps
(par zone), fin d'année. Chaque vacance se note par son **premier jour** et son
**jour de reprise** ; la période se termine la veille du premier jour.

- **Ne pas écrire une date de période dans un document.** Le badge de chaque
  titre « Période N » la calcule pour la zone choisie. C'est pourquoi la zone
  change tout le site d'un clic, et pourquoi chaque document existe en trois
  PDF (`pdf/zone-A|B|C/`).
- **Toute date se relève dans le jeu de données, jamais de mémoire** : la fin
  de l'année 2026-2027 a d'abord été écrite « 6 juillet », alors que les
  cours finissent le **vendredi 2 juillet 2027**.
- Le nombre de semaines est un arrondi de jours / 7 : vérifier qu'il tombe
  juste quand on change d'année (P1 2026-2027 : 7 semaines, P5 zone A : 10).
- Les ponts (`calendrier.ponts`) s'affichent d'eux-mêmes dans l'accueil ;
  le README, lui, les écrit en clair : à reprendre à la main.

### Changer d'année scolaire

1. Relever les dates officielles des trois zones (le jeu de données ci-dessus,
   filtré sur l'année ; zone A, B, C de métropole).
2. Mettre à jour `annee` et `calendrier` dans `classe.yml` (ponts compris),
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
retouche de l'écran ») : accueil, une progression, une évaluation, les trois
zones, à 1280 px et 400 px.
