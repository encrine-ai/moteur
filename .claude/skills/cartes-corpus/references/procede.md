# Le procédé, et comment l'étendre à un autre matériel

L'imagier et les cartes-corpus sont deux jeux de cartes très différents — des
photographies d'espèces d'un côté, des pictogrammes et des dessins de mots de
l'autre — fabriqués par **le même enchaînement**. C'est délibéré : ce qui a
été appris sur l'un vaut pour l'autre, et un troisième jeu de cartes ne devrait
pas repartir de zéro.

Ce fichier décrit l'enchaînement, ce qui doit être repris tel quel et pourquoi.

## Les six pièces, toujours les mêmes

| Pièce | Imagier | Cartes-corpus | Ce qu'elle porte |
|---|---|---|---|
| **Manifeste** | `classe/imagier.py` | `classe/corpus.py` | la liste des cartes, et pour chacune **le choix fait** (identifiant de photo, identifiant de pictogramme, fichier de dessin) |
| **Planche de candidats** | `candidats-imagier.py` | `chercher-pictos.py chercher` | plusieurs propositions par carte, à regarder |
| **Moisson** | `chercher-images-imagier.py` | `chercher-pictos.py installer` | télécharge ce qui a été choisi, et **relève les crédits** |
| **Génération** | `generer-imagier.py` | `generer-cartes-corpus.py` | les planches HTML, imprimées en PDF au déploiement |
| **Contrôle** | `verifier-imagier.py` | `verifier-cartes-corpus.py` | ce qui se vérifie sans regarder ; code 1 s'il reste une anomalie |
| **Revue** | `revoir-imagier.py` | `revoir-cartes-corpus.py` | les pages telles qu'elles s'imprimeront, à regarder |

## Les règles à ne pas contourner

**1. Le choix de l'image est un geste humain, et il est écrit.** Aucun tri
automatique ne convient : celui d'iNaturalist met en avant le spectaculaire
(un ours qui mange des pissenlits pour « le pissenlit »), celui de Global
Symbols cherche le mot et non le sens (un foret de perceuse pour « la
forêt »). Le manifeste porte donc l'identifiant retenu, **avec un commentaire
disant pourquoi celui-là**. Sans cette trace, la prochaine exécution du script
défait le choix.

**2. La moisson ne choisit jamais.** Un script de téléchargement qui « prend
le premier résultat » quand le manifeste ne dit rien finira par publier une
mauvaise carte. `chercher-pictos.py installer` exige l'identifiant retenu —
`mulberry:<nom>`, `arasaac:<id>` ou `openverse:<id>` — et ne devine rien ;
`verifier-cartes-corpus.py` nomme les mots encore sans image.

**3. Les crédits sont relevés au téléchargement, pas après.** Auteur, licence,
source, identifiant d'origine. Retrouver la provenance d'une image six mois
plus tard est impossible ; le contrôle refuse une image sans crédits.

**4. Une image n'est jamais dupliquée.** Une carte-corpus qui montre le renard
pointe vers `site/imagier/img/renard-roux.jpg`. Deux copies divergent : on
corrige l'une et pas l'autre.

**5. Le choix des images ne se décide pas ici.** Les sources, leur ordre,
leurs pièges et l'outil qui les moissonne sont dans le skill
[`fiches-illustrations`](../../fiches-illustrations/SKILL.md) : Mulberry
d'abord, ARASAAC ensuite, Openverse en troisième recours, aucun dessin à main
levée, et jamais Wikimedia Commons. Un jeu de cartes qui se donnerait ses
propres sources finirait par diverger.

**5 bis. Une banque partagée se contrôle sur tout le site.** Les cartes-corpus
puisent dans `site/fiches/img/` sans rien y ajouter qui leur soit propre. Un
contrôle qui ne regarderait que `site/fiches/*.html` déclarerait « jamais
référencées » — donc supprimables — les images qui ne servent qu'aux cartes.
`chercher-pictos.py verifier` parcourt `site/` en entier pour cette raison.

**6. Le contrôle dit ce qui manque, la revue montre ce qui est faux.** Les
deux sont nécessaires et ne se remplacent pas. Le contrôle est automatique et
sort en code 1 ; la revue produit des images qu'**il faut regarder**.

## Ce que le contrôle doit toujours vérifier

Quel que soit le matériel, ces quatre-là :

- **la couverture** — chaque élément de la source de vérité (le référentiel,
  le tableau des corpus, la liste des espèces) a une carte, ou est déclaré
  comme volontairement absent. Une déclaration périmée est signalée elle
  aussi, sans quoi la liste des exceptions enfle sans qu'on le voie ;
- **les fichiers** — chaque image existe là où le manifeste la désigne ;
- **les licences** — celles qu'admet le skill `fiches-illustrations` :
  CC0, CC BY, CC BY-SA sans réserve, CC BY-NC-SA (ARASAAC) faute de mieux ;
- **la fraîcheur des pages** — le nombre de cartes dans le HTML correspond au
  manifeste, donc la génération a bien été relancée après modification.

Et, dans la revue, la **pagination** : une page de garde qui déborde d'une
ligne pousse tout le cahier d'une page. Invisible à l'écran, gênant à
l'impression. Le nombre de pages attendu se calcule à partir du manifeste.

## Monter un nouveau jeu de cartes

Dans l'ordre, en copiant les scripts existants plutôt qu'en réinventant :

1. **La source de vérité d'abord.** D'où vient la liste des cartes ? Le
   tableau des corpus de `01-projet-annuel.md`, le référentiel, une
   progression. Le contrôle de couverture s'y adossera : sans source de
   vérité, on ne peut pas dire que le jeu est complet.
2. **Le manifeste**, sur le modèle de `classe/corpus.py` : la liste, les
   provenances, le dictionnaire des choix, la liste des éléments volontairement
   sans carte, et une fonction `entrees()` qui rend tout à plat.
3. **La planche de candidats**, si la source des images propose plusieurs
   possibilités. Une page HTML de vignettes numérotées suffit ; l'identifiant
   affiché est celui à recopier dans le manifeste.
4. **La moisson**, qui télécharge et relève les crédits.
5. **La génération**, en réutilisant la feuille de style existante quand la
   mise en page est la même — `cartes-corpus.css` reprend `imagier.css` avec
   une seule différence réelle : les photographies remplissent la carte
   (`cover`) tandis que les dessins s'y inscrivent en entier (`contain`).
6. **Le contrôle et la revue**, avec les quatre vérifications ci-dessus.
7. **Le câblage** : `scripts/generer-pdf.sh` pour le PDF, `site/index.html` et
   `site/app.js` pour le bouton et la rubrique d'accueil, `README.md` et
   `CLAUDE.md` pour la documentation.
8. **Le skill**, avec ses cas de déclenchement dans `tests/`, mesurés par
   `scripts/mesurer-declenchement.py`. Un procédé qui n'est pas dans un skill
   sera refait de zéro par la prochaine session.

## Mesurer le skill

```sh
SKILL=cartes-corpus python3 scripts/mesurer-declenchement.py \
  tests/declenchement-cartes-corpus.json
```

**Ne pas se fier au banc d'essai du skill-creator** : il passe par un faux
fichier de commande que cette version de Claude Code n'expose pas comme un
skill, si bien qu'aucune demande ne déclenche jamais rien. Il annonçait 10/20
là où la mesure directe donnait 20/20.

Les cas négatifs les plus utiles sont les **voisins** : une demande qui parle
des cartes-corpus mais relève du CSS, de la génération des PDF ou des
photographies de l'imagier ne doit pas ouvrir ce skill-ci.

**La mesure est bruitée : deux tirages par cas, et l'écart entre deux
exécutions d'une même description atteint un point.** Trois variantes de la
description ont donné 16, 16 et 15 sur 20 ; en conclure qu'une variante est
meilleure qu'une autre à un point près serait se mentir. Ne retoucher la
description que pour une raison qui se dit en français — « ces demandes
partaient vers le seul choix d'image, sans personne pour régénérer les
cahiers » en est une, « ça fait gagner un point » n'en est pas une.

Deux cas restent en échec, et ce sont les **cas de test** qui sont en cause :
« le dessin du trottoir, on ne comprend pas ce qu'on regarde » et « le
pictogramme de la ferme montre une porte fermée » ne nomment ni les cartes,
ni le corpus, ni un fichier. Rien ne les distingue d'une demande sur une
fiche élève, et y répondre en ouvrant `fiches-illustrations` n'est pas une
erreur. Les laisser rouges plutôt que d'élargir la description jusqu'à
avaler les demandes de CSS — c'est ce qui est arrivé en essayant.
