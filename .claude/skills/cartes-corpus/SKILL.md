---
name: cartes-corpus
description: Les cartes-corpus de vocabulaire (site/cartes-corpus/) — les mots des trois corpus de chaque période, en cartes de nomenclature à découper, et le matériel des fiches d'évaluation X.1 et X.3. À utiliser pour ajouter un mot à un corpus, **remplacer ou corriger l'image d'une carte**, refaire un cahier, produire les étiquettes de tri (les « boîtes-catégories » des fiches X.1), ou contrôler avant d'imprimer que chaque mot a sa carte. Couvre classe/corpus.py, generer-cartes-corpus.py, verifier-cartes-corpus.py, revoir-cartes-corpus.py. Se déclenche même quand la demande ne nomme aucun fichier : « il manque le mot brouette dans le corpus de la campagne », « l'image de la carte du sentier ne veut rien dire pour un GS », « le pictogramme d'une carte montre autre chose que le mot écrit dessous », « il faut les trois boîtes-catégories de la fiche 3.1 », « vérifie que tous les mots des corpus ont leur carte avant que j'imprime », « reprends le cahier de cartes de la période 4 ». Une image de carte qui ne va pas relève **aussi** de ce skill, jamais de fiches-illustrations seul : celui-ci dit comment choisir l'image, celui-là dit quoi régénérer et contrôler ensuite — les deux se chargent ensemble. Ne concerne pas les photographies d'espèces (voir imagier-photos).
---

# Les cartes-corpus de vocabulaire

Cinq cahiers A4, un par période, qui portent **tous les noms des trois corpus**
de `01-projet-annuel.md` — le milieu, la faune, la flore. Chaque mot donne
trois cartes : image + mot, image seule, mot seul ; le cahier se termine par
les **étiquettes de tri**, c'est-à-dire les « boîtes-catégories » que la fiche
d'évaluation X.1 demande de préparer.

Ils existent parce que les fiches X.1 (vocabulaire) et X.3 (phonologie)
réclamaient « 12 cartes-images des corpus » que rien ne fabriquait.

## L'image d'une carte : deux skills, pas un

Une demande du genre « le dessin du trottoir ne va pas » demande les deux, et
dans cet ordre :

1. **[`fiches-illustrations`](../fiches-illustrations/SKILL.md)** dit *quelle*
   image — l'ordre des sources (Mulberry d'abord, ARASAAC ensuite, Openverse
   en troisième recours), les pièges, les règles de choix, l'outil. Rien de
   tout cela n'est répété ici : une copie finit par diverger de l'original.
2. **Ce skill-ci** dit ce qu'il faut faire *ensuite* — régénérer les cahiers,
   relancer le contrôle, regarder le PDF. Une image remplacée sans cela laisse
   les pages HTML périmées, et le cahier imprimé montre encore l'ancienne.

Charger `fiches-illustrations` avant de toucher à la moindre image ; revenir
ici pour la boucle de travail ci-dessous.

Ce qu'il faut en retenir pour ces cahiers :

- **il n'y a pas de banque d'images propre aux cartes-corpus.** Les
  pictogrammes viennent de `site/fiches/img/`, la banque partagée du dépôt,
  et `credits.json` en est la source de vérité ;
- **on n'y installe rien à la main** : `scripts/chercher-pictos.py` cherche,
  fabrique une planche **à regarder**, puis installe et crédite ;
- **on ne dessine pas.** Seules les formes géométriques élémentaires sont
  fabriquées dans ce dépôt, et il n'y en a aucune dans ces cahiers.

Une seule provenance s'y ajoute, propre à ces cartes : les **photographies de
l'imagier** (`site/imagier/img/`), quand le mot est une des espèces déjà
photographiées et choisies à la main. On ne recopie pas le fichier, la carte
pointe dessus.

## Le manifeste

`classe/corpus.py` porte, période par période et corpus par corpus :

| Clé | Rôle |
|---|---|
| `CARTES` | la liste des mots, avec pour chacun `("imagier", slug)` ou `("fiche", slug)` |
| `RAPPELS` | un mot qui revient dans une autre période — la carte y est réimprimée, pour que chaque cahier soit complet |
| `NON_ILLUSTRES` | les **verbes et adjectifs** des corpus, qui n'ont volontairement pas de carte |
| `TRI`, `TRI_MILIEUX` | les intitulés des étiquettes de tri |

Les verbes et les adjectifs (*traverser*, *hiberner*, *rugueux*…) n'ont pas de
carte : une image les ambiguïse plus qu'elle ne les enseigne, et ils s'évaluent
dans le réemploi, comme le demandent les critères des fiches X.1.

## La boucle de travail

```sh
# 1 — déclarer le mot dans CARTES (classe/corpus.py)

# 2 — voir ce qui manque : le contrôle nomme les mots sans image
python3 scripts/verifier-cartes-corpus.py

# 3 — pour chacun, la boucle du skill fiches-illustrations
python3 scripts/chercher-pictos.py chercher potager "vegetable_garden allotment"
#     → REGARDER /tmp/pictos/potager.png
python3 scripts/chercher-pictos.py installer potager mulberry:vegetable_garden

# 4 — régénérer, contrôler, puis REGARDER les pages
python3 scripts/generer-cartes-corpus.py
python3 scripts/verifier-cartes-corpus.py
REVUE_DIR=/tmp/revue python3 scripts/revoir-cartes-corpus.py 4
```

## Ce que le contrôle vérifie

`scripts/verifier-cartes-corpus.py`, code 1 s'il reste quelque chose :

- **la couverture** : chaque nom des corpus de `01-projet-annuel.md` a une
  carte, ou est déclaré dans `NON_ILLUSTRES`. Un mot ajouté à un corpus sans
  carte fait échouer le contrôle au lieu de passer inaperçu — même filet que
  `couverture.py` pour le programme ;
- **les images manquantes** : les mots dont le slug n'est pas encore dans la
  banque partagée sont listés, avec la commande qui les installe ;
- **les crédits** : source, licence et auteur renseignés pour chaque image ;
- **les doublons** : deux cartes ne peuvent pas porter les mêmes octets ;
- **la fraîcheur des pages** : le nombre de cartes du HTML correspond au
  manifeste, donc la génération a bien été relancée.

`scripts/revoir-cartes-corpus.py` ajoute ce que le HTML ne montre pas : la
**pagination**. Une page de garde qui déborde d'une ligne pousse tout le cahier
d'une page. Le nombre de pages attendu se calcule et l'écart est signalé.

Aucun de ces contrôles ne dit qu'une image montre le bon sens. **Cela se
regarde**, sur la planche de candidats puis sur les pages rendues.

## Monter un troisième jeu de cartes

L'enchaînement — manifeste, planche de candidats, moisson, génération,
contrôle, revue — est commun à l'imagier et à ces cahiers. Il est décrit dans
[`references/procede.md`](references/procede.md).
