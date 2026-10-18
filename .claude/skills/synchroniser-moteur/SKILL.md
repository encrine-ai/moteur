---
name: synchroniser-moteur
description: Mettre à jour le moteur d'une classe — copier dans ce dépôt la nouvelle version du moteur (scripts, code du site, référentiel du programme, skills, déploiement) depuis le dépôt modèle, sans jamais toucher au contenu de la classe (classe.yml, classe/, les documents de l'enseignant, les cahiers fabriqués), sans écraser une modification faite à la main, puis régénérer et refaire tous les contrôles jusqu'au PDF. Le dépôt et la version du moteur se lisent dans classe.yml (`moteur`). À utiliser pour « mets l'outil à jour », « récupère les nouveautés du moteur », « il paraît qu'il y a une nouvelle version », « synchronise avec le modèle », ou quand une amélioration remontée a été intégrée au moteur. Ne concerne pas une retouche de la classe.
---

# Synchroniser le moteur

Une classe créée depuis le dépôt modèle **ne partage aucun historique** avec
lui : ce n'est pas une branche qu'on fusionne, c'est une **copie délibérée,
fichier par fichier**, de la couche moteur. Elle n'est possible que parce
que le moteur et le contenu sont séparés — `python3 scripts/classe.py
verifier` le prouve. C'est la mécanique de Ludea (`sync-engine`) :
chaque enseignant met à jour **sa** classe, quand il le veut.

## Ce qui bouge, ce qui ne bouge jamais

| Couche | Chemins | Synchronisée ? |
|---|---|---|
| **le moteur** | `scripts/`, `site/*.js` (sauf `site/classe.js`), `site/*.html`, `site/*.css`, `site/marked.min.js`, le socle de la charte : `site/charte/socle.css` et `site/charte/polices/` (Andika), `referentiel/`, `.claude/skills/`, `.github/workflows/`, `tests/` | **oui** |
| **la classe** | `classe.yml`, `classe/`, les documents `01-…` à `04-…`, `README.md`, les cahiers fabriqués (`site/fiches/*.html`, `site/imagier/`, `site/cartes-corpus/`, leurs images et crédits), `site/classe.json`, `site/classe.js`, les thèmes `site/charte/themes/` | **jamais** |
| **fabriqué** | `site/charte/charte.css` (socle + thème), `site/charte/icones.svg` (icônes génériques + celles des milieux de `classe.yml`) | **jamais copiés** : refaits après la synchronisation, `python3 scripts/classe.py generer` puis `python3 scripts/generer-icones.py` (réseau) |
| **à la main** | `CLAUDE.md` (il mêle les règles du moteur et l'identité de la classe) | ne reprendre que les règles générales, par une lecture attentive |

La charte est scindée (`docs/vers-un-moteur.md`, « Deux couches de style ») :
le socle suit le moteur, **les thèmes jamais** — même celui que le modèle
apporterait sous le même nom, puisque la classe a pu retoucher le sien. Un
thème nouveau du modèle ne s'ajoute que si l'enseignant le demande.

## 0. Avant de commencer

- Lire `moteur` dans `classe.yml`. **`depot` non renseigné** : ce dépôt est
  celui où le moteur se développe, il n'y a rien à synchroniser. Arrêter.
- L'arbre de travail doit être **propre** (`git status`) : sinon, finir ou
  committer le travail en cours d'abord.
- **Les modifications faites ici au moteur** : comparer les fichiers du
  moteur à la version d'où la classe dérive (`moteur.version`) —
  `git diff --stat <version>..HEAD -- <chemins du moteur>` une fois le dépôt
  modèle récupéré (étape 1). Un fichier du moteur modifié ici et pas encore
  remonté serait **perdu** : passer par le skill **remonter-au-moteur**
  d'abord, puis le réappliquer après la synchronisation si le moteur ne l'a
  pas encore intégré. On ne force jamais.

## 1. Récupérer la nouvelle version

```sh
git remote add moteur https://github.com/<moteur.depot>.git   # la première fois
git fetch moteur main
git log --oneline <moteur.version>..moteur/main               # ce qui a changé
```

Résumer pour l'enseignant, en deux ou trois phrases sans technique, ce que
la mise à jour apporte (« les fiches savent maintenant faire des cases plus
grandes ; l'entretien demande le modèle d'écriture cursive »).

## 2. Copier la couche moteur, et elle seule

```sh
git checkout moteur/main -- scripts/ referentiel/ .claude/skills/ .github/workflows/ tests/ \
  site/app.js site/commun.js site/marked.min.js site/index.html site/imprimer.html \
  site/app.css site/impression.css site/charte/socle.css site/charte/polices/
python3 scripts/classe.py generer      # refait charte.css : nouveau socle + thème de la classe
```

Puis **relire `git diff --cached`** fichier par fichier : rien de la classe
ne doit y apparaître, et une retouche locale déjà remontée doit être
retrouvée dans la nouvelle version (sinon la réappliquer et la signaler à
nouveau). Un skill que la classe avait enrichi d'une leçon à elle : garder
la leçon si elle vaut toujours, en la remontant.

## 3. Mettre la classe d'accord avec le nouveau moteur

- **Nouvelles clés de `classe.yml`** : si le moteur en attend une que la
  classe n'a pas, `python3 scripts/classe.py verifier` le dit. L'ajouter
  avec la valeur par défaut annoncée par le skill concerné, et l'annoncer à
  l'enseignant ; ne poser la question que si la valeur change le résultat.
- `python3 scripts/classe.py generer`, puis régénérer les cahiers
  (`generer-imagier.py`, `generer-cartes-corpus.py`, `generer-credits.py`).
- Une régénération ne doit écraser **aucune** retouche faite à la main par
  l'enseignant dans un cahier : relire le diff des cahiers, et rétablir à la
  main ce qui doit l'être.

## 4. Tout contrôler, finir par le PDF

```sh
python3 scripts/classe.py verifier        # 0 anomalie
python3 scripts/couverture.py             # code 0
python3 scripts/verifier-imagier.py
python3 scripts/verifier-cartes-corpus.py
python3 scripts/chercher-pictos.py verifier
bash scripts/generer-pdf.sh <site assemblé> && python3 scripts/verifier-pagination.py <site assemblé>
```

Assembler le site comme le déploiement (skill imprimer-pdf, étape 1). Un
contrôle rouge : ne pas committer ; corriger s'il s'agit du contenu de la
classe, sinon **remonter** le défaut et revenir à la version précédente du
moteur (`git checkout HEAD -- <chemins>`).

## 5. Committer, noter la version

Mettre `moteur.version` à jour dans `classe.yml` (le commit du moteur
copié, `git rev-parse moteur/main`), `classe.py generer`, puis un seul
commit : `Moteur <version courte> : <ce qui change pour la classe>`, avec
dans le corps la liste des contrôles et leurs résultats chiffrés. Fusionner
sur `main` une fois les contrôles verts (CLAUDE.md, « Branches, commits,
publication »), et ne dire « c'est en ligne » qu'après l'avoir vu en ligne
(skill site-et-calendrier).

## Garde-fous

- Ne copier **que** les chemins du moteur ; jamais `classe.yml`, `classe/`,
  un document de l'enseignant, un cahier fabriqué.
- Jamais `--force`, jamais d'écrasement d'une modification non remontée.
- `classe.py verifier` doit rester vert : un moteur qui écrit une donnée de
  classe en dur est un défaut du moteur — à remonter, pas à corriger chez
  soi.

## Enchaînement

remonter-au-moteur (s'il y a des modifications locales) → **synchroniser-moteur**
→ imprimer-pdf → site-et-calendrier (le déploiement).
