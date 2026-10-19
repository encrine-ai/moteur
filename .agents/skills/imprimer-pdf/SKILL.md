---
name: imprimer-pdf
description: Fabriquer et contrôler les PDF de Ma Grande Section — les documents aux dates de la zone de la classe et leurs extraits par période, les cahiers de fiches élève et d'entraînement, les imagiers, les cartes-corpus — avec scripts/generer-pdf.sh et scripts/verifier-pagination.py. À utiliser avant tout commit qui touche à ce qui s'imprime (une fiche, une planche, une feuille CSS du papier, la charte, une police), pour régénérer les PDF, ou quand quelque chose « s'imprime mal ». Se déclenche aussi sans nom de fichier : « la fiche déborde sur deux pages », « le pied de page est tout seul sur une feuille », « vérifie que tout s'imprime bien », « le PDF de la période 3 a une page blanche », « refais les PDF », « les étiquettes passent sur les crédits ». La règle du dépôt : finir par le PDF, jamais par le HTML.
---

# Imprimer, et le prouver

Le HTML ne dit rien de la pagination : **un navigateur s'allonge, une feuille
A4 non.** Les deux pires défauts de ce matériel — les étiquettes non paginées
qui s'imprimaient par-dessus les crédits, le pied de la garde seul sur une
page — n'existaient pas à l'écran. Et quand la charte a changé de polices, le
contrôle a révélé quatre débordements qui étaient déjà sur `main` sans que
personne les voie. Toute retouche du papier se termine donc par le PDF.

## Ce qui s'imprime

| Source | PDF (dans `<site>/pdf/`) | Une page = |
|---|---|---|
| un document Markdown via `imprimer.html?doc=…` | `<doc>.pdf` | (libre) |
| le même, extrait d'une période (`&periode=N`) | `<doc>-periode-N.pdf` | (libre) |
| `site/fiches/periode-N.html` | `fiches-eleve-periode-N.pdf` | une `section.fiche` |
| `site/fiches/entrainement-periode-N.html` | `fiches-entrainement-periode-N.pdf` | une `section.fiche` |
| `site/imagier/periode-N.html` | `imagier-periode-N.pdf` | une `section.planche` (la couverture comprise) |
| `site/cartes-corpus/periode-N.html` | `cartes-corpus-periode-N.pdf` | une `section.planche` (la couverture comprise) |

Chaque **document** s'ouvre sur une **première page** (le document, la
classe, ses dates) au style de la marque Encrine, avec en-tête courant et
pied « Conçu avec Encrine · encrine.ai » · « page X / Y » (skill
charte-graphique, « La marque sur le papier ») : une page de plus par
document et par extrait. **Chaque page de chaque PDF** — documents et
cahiers — porte la mention « Conçu avec Encrine · encrine.ai » ; sur le
matériel des élèves, elle est dans la marge basse, sans rien prendre au
contenu.

L'imagier et les cartes-corpus s'ouvrent sur une **couverture**, une page de
plus par cahier (`couverture: false` dans `materiel` la retire ; skill
charte-graphique). Elle a une hauteur fixe de 271 mm : c'est la seule page
où le thème compose librement, sans risque pour la pagination.

Une classe n'a **qu'une zone** (`calendrier.zone` dans `classe.yml`) : chaque
document s'imprime une fois, à ses dates, et tout est à plat dans `pdf/`. Une
Grande Section complète, c'est 65 PDF — 45 documents et extraits, 20 cahiers ;
`verifier-pagination.py` les compte, donne le total des pages et cherche la
mention au pied de chaque page (`pdftotext`). Mesure sur la démonstration
lors du passage à la marque : 65 PDF, 366 → 409 pages ; documents 96 → 139
(+45 premières pages, −2 : deux extraits tiennent sur une page de moins),
les 20 cahiers inchangés, fichier par fichier. Ils **ne sont pas versionnés** : le workflow
`.github/workflows/pages.yml` les refait à chaque déploiement, puis lance
`verifier-pagination.py`, qui bloque la publication s'il reste un débordement,
un document sans PDF, ou un vieux dossier `pdf/zone-X/`.

## La marche à suivre

```sh
# 1. assembler le site comme le fait le workflow
rm -rf /tmp/site && mkdir -p /tmp/site/content && cp -r site/. /tmp/site/ \
  && cp 01-projet-annuel.md 02-programmation-annuelle.md /tmp/site/content/ \
  && cp -r 03-progressions 04-evaluations /tmp/site/content/
# 2. fabriquer les PDF (5 minutes ; le Chromium de Playwright est trouvé seul)
bash scripts/generer-pdf.sh /tmp/site
# 3. une page par fiche, une page par planche
python3 scripts/verifier-pagination.py /tmp/site
```

Pour un seul cahier, inutile de tout refaire :

```sh
(cd /tmp/site && python3 -m http.server 8934 &)
/opt/pw-browsers/chromium-*/chrome-linux/chrome --headless --no-sandbox --no-pdf-header-footer \
  --virtual-time-budget=10000 --print-to-pdf=/tmp/f.pdf http://127.0.0.1:8934/fiches/periode-2.html
pdfinfo /tmp/f.pdf | grep Pages
```

(30 000 ms de budget pour un imagier ou des cartes-corpus : beaucoup de
photographies à charger avant l'impression.)

Puis **regarder** : `pdftoppm -f N -l N -r 60 -png fichier.pdf /tmp/p` rend
la page N en image. Le compte de pages ne voit pas une étiquette tronquée, une
image manquante ni une consigne illisible.

## La mention de la marque manque

`verifier-pagination.py` dit « la mention … manque » : presque toujours une
police pas chargée à temps. Une boîte de marge `@page` sans sa police
n'imprime rien, sans erreur. Vérifier que la page charge bien Figtree
(`pdffonts`), que le `html::before` du socle est là (matériel) ou que le
texte du document est en Figtree (documents), et que `site/marque/polices/`
a été copié dans le site assemblé.

## Quand une section déborde

- Trouver la page fautive : `pypdf` (`PdfReader(f).pages[i].extract_text()`)
  montre où commence chaque fiche — la page de trop ne porte souvent que le
  pied (« Compétences : … »).
- Resserrer **la fiche fautive**, pas la feuille commune : un `style` local sur
  ses éléments (la fiche A6 de l'entraînement P1 a perdu 0,5 mm de marge sur
  six cases et 2 mm avant son défi). Changer `fiches.css` déplace la
  pagination des 96 autres fiches.
- Ne jamais réduire le corps des mots que l'enfant lit pour faire tenir une
  page : enlever un item, ou couper la fiche en deux.
- Garde et crédits sont du texte : `height: auto`, jamais la hauteur exacte
  de la page (aucune tolérance d'arrondi : c'est ce qui faisait passer le pied
  de la garde seul sur une page).

## Quand l'enseignante dit que « ça s'imprime mal »

**La croire, et chercher ce qui touche le bord.** « Tous les PDF sont un peu
tronqués sur le bord droit » : la première réponse a été que les fichiers
étaient sains — marges mesurées, symétriques — et que l'imprimante était en
cause. Sa photo de la feuille imprimée a montré la vraie raison : la bordure
droite des tableaux tombait **pile sur la limite du bloc d'impression**, que
les imprimantes rognent. D'où le `padding-right: 1.2mm` de
`site/impression.css` et de `site/fiches/fiches.css` (commit « Correctif
troncature PDF ») : rien d'utile ne doit toucher la marge. Demander la photo
de la feuille plutôt que de défendre le fichier.

**Prévenir quand le volume change.** Une modification qui ajoute des pages
(l'imagier doublé : de 45 à 80 pages A4 par an, à plastifier) se signale à
l'enseignante au moment où elle est faite.

## Après le contrôle

- Le compte rendu de `verifier-pagination.py` va dans le message de commit
  quand il a changé quelque chose (« 20 cahiers, 0 anomalie »).
- Les nombres de pages ont changé ? Rien d'autre à mettre à jour : aucun
  document n'annonce un nombre de pages.
