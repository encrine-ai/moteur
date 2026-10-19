---
name: synchroniser-moteur
description: Mettre à jour le moteur d'une classe — copier dans ce dépôt la nouvelle version du moteur (scripts, code du site, référentiel du programme, skills, déploiement) depuis le dépôt modèle, sans jamais toucher au contenu de la classe (classe.yml, classe/, les documents de l'enseignant, les cahiers fabriqués), sans écraser une modification faite à la main, puis régénérer et refaire tous les contrôles jusqu'au PDF. Le dépôt et la version du moteur se lisent dans classe.yml (`moteur`). À utiliser pour « mets l'outil à jour », « récupère les nouveautés du moteur », « il paraît qu'il y a une nouvelle version », « synchronise avec le modèle », ou quand une amélioration remontée a été intégrée au moteur. Ne concerne pas une retouche de la classe.
---

# Synchroniser le moteur

Une classe créée depuis le dépôt modèle **ne partage aucun historique** avec
lui : ce n'est pas une branche qu'on fusionne, c'est une **copie délibérée,
fichier par fichier**, de la couche moteur. Elle n'est possible que parce
que le moteur et le contenu sont séparés — `python3 scripts/classe.py
verifier` le prouve. Chaque enseignant met à jour **sa** classe, quand il
le veut.

## Ce qui bouge, ce qui ne bouge jamais

**La liste des chemins du moteur n'est écrite qu'à un endroit** :
`scripts/chemins_moteur.py` (`MOTEUR`, `FABRIQUES`, `PROPRES_AU_MOTEUR`).
Ce skill, remonter-au-moteur et l'agent moteur d'Encrine (sa procédure
vit dans `encrine-ai/agents`) la lisent ; aucun ne la recopie. La commande de copie écrite ici à la main oubliait
`site/modele.js`, `site/gabarits.js`, `site/appli.js` et `site/marque/`,
que la table ci-dessous annonçait pourtant (« `site/*.js` ») : une liste
recopiée vieillit sans que personne le voie. La table résume ; en cas de
doute, c'est le script qui a raison (`python3 scripts/chemins_moteur.py
fichiers moteur/main` liste ce qui sera copié).

| Couche | Chemins | Synchronisée ? |
|---|---|---|
| **le moteur** | `scripts/`, `site/*.js` (sauf `site/classe.js` et `site/sw.js`), `site/*.html`, `site/*.css`, `site/marque/` (le logo et les polices d'Encrine), les feuilles des cahiers (`site/fiches/fiches.css`, `site/imagier/imagier.css`, `site/cartes-corpus/cartes-corpus.css`), le socle de la charte : `site/charte/socle.css`, `site/charte/composants.css` et `site/charte/polices/` (Andika), `referentiel/` (la liste du programme **et le calendrier officiel de chaque année**, `calendrier-AAAA-AAAA.yml`), `.agents/skills/` (les skills, au standard ouvert) et le lien symbolique `.claude/skills` qui y renvoie pour Claude Code, `.github/workflows/`, `tests/` | **oui** |
| **propre à la classe, dans un skill** | la section qui finit un `SKILL.md`, entre `<!-- classe:debut -->` et `<!-- classe:fin -->` (« ## Propre à cette classe » : son thème, une décision de l'enseignant…) | **jamais écrasée** : `copier` la garde et la repose à la fin du skill neuf ; `ecarts` et `bilan` ne la comptent pas comme une retouche du moteur |
| **propre au moteur** | `.github/workflows/controles.yml`, les contrôles de ses demandes de fusion (la boîte du moteur, elle, est traitée par l'agent moteur, dont la procédure vit dans `encrine-ai/agents` : elle n'arrive jamais dans une classe) | **jamais** : la copie les écarte, `chemins_moteur.py verifier` refuse de les trouver dans une classe |
| **la classe** | `classe.yml`, `classe/`, les documents `01-…` à `04-…`, `README.md` (jamais écrasé par celui du modèle : seul son bloc de tête, entre `<!-- encrine:debut -->` et `<!-- encrine:fin -->`, est refait par `classe.py generer`), les cahiers fabriqués (`site/fiches/*.html`, `site/imagier/`, `site/cartes-corpus/`, leurs images et crédits), `site/classe.json`, `site/classe.js`, les thèmes `site/charte/themes/` | **jamais** |
| **fabriqué** | `site/charte/charte.css` (socle + thème), `site/charte/gabarits.js` (le renvoi vers les gabarits du thème), `site/charte/icones.svg` (icônes génériques + celles des milieux de `classe.yml`), l'appli installable : `site/manifest.webmanifest`, `site/sw.js` (malgré `site/*.js`), `site/icones/`, `site/favicon.ico` ; `PRISE-EN-MAIN.md`, le guide de l'enseignant (sa section « Propre à cette classe », entre `<!-- classe:debut -->` et `<!-- classe:fin -->`, est gardée) | **jamais copiés** : refaits après la synchronisation, `python3 scripts/classe.py generer` puis `python3 scripts/generer-icones.py` (réseau) |
| **à la main** | `AGENTS.md` (les consignes de l'agent : il mêle les règles du moteur et l'identité de la classe) ; `CLAUDE.md` (l'import `@AGENTS.md` et quelques lignes propres à Claude Code) | ne reprendre que les règles générales, par une lecture attentive ; une classe d'avant `AGENTS.md`, dont tout tient dans `CLAUDE.md`, y déplace ses consignes et ne garde dans `CLAUDE.md` que l'import |

La charte est scindée en deux couches :
le socle suit le moteur, **les thèmes jamais** — même celui que le modèle
apporterait sous le même nom, puisque la classe a pu retoucher le sien. Un
thème nouveau du modèle ne s'ajoute que si l'enseignant le demande.

## 0. Avant de commencer

- **Ce dépôt est-il le moteur lui-même ?** Le dépôt courant — `depot` de
  `classe.yml`, ou à défaut celui de `git remote get-url origin` — est
  `moteur.depot` : c'est là que le moteur se développe, il n'y a rien à
  synchroniser ; une correction s'y fait sur place. Arrêter.

  ```sh
  python3 scripts/chemins_moteur.py ou     # « moteur » : arrêter ; « classe » : continuer
  ```

  (L'ancien test, « `depot` à définir », est périmé : le modèle garde
  `depot: à définir`, mais une copie toute fraîche faite par « Use this
  template », avant son entretien, aussi — et elle, se synchronise.
  `chemins_moteur.py copier` refuse de toute façon de tourner dans le moteur.)
- L'arbre de travail doit être **propre** (`git status`) : sinon, finir ou
  committer le travail en cours d'abord.
- **`moteur.version` vaut `null`** (une classe créée avant que
  nouvelle-classe ne l'écrive, ou dont personne ne l'a noté) : sans elle, on
  ne sait ni ce qui a changé ni ce que la classe a retouché. La
  reconstituer, une fois le dépôt modèle récupéré (étape 1) : le commit du
  moteur dont les fichiers du moteur égalent le mieux ceux de la classe,
  sur la liste unique.

  ```sh
  python3 scripts/chemins_moteur.py version moteur/main --ecrire
  ```

  Il dit combien de fichiers diffèrent encore de ce commit : zéro, la
  classe est une copie exacte ; quelques-uns, ce sont ses retouches (les
  voir avec `ecarts`, ci-dessous). L'annoncer à l'enseignant en une phrase
  (« ta classe venait de la version de septembre de l'outil »), et le
  garder dans le commit de l'étape 5.
- **Les modifications faites ici au moteur** : comparer les fichiers du
  moteur à la version d'où la classe dérive (`moteur.version`), une fois le
  dépôt modèle récupéré (étape 1) :

  ```sh
  python3 scripts/chemins_moteur.py ecarts <moteur.version>
  ```

  `M` : un fichier du moteur retouché ici (hors de la section propre à la
  classe d'un skill, qui est à elle et que la copie garde) ; `A` : un fichier rangé dans un
  dossier du moteur qui n'existe que dans la classe (un vieux script : la
  copie le laisse en place) ; `D` : un fichier du moteur absent d'ici. Le
  titre et l'aperçu de lien d'`index.html`, refaits pour chaque classe, ne
  comptent pas, ni la section « Propre à cette classe » d'un skill. Deux
  sortes d'écarts :
  - **une leçon qui vaut pour toutes les classes** (un contrôle retouché
    dans la classe, par exemple `verifier-cartes-corpus.py`) : la remonter
    (skill remonter-au-moteur) ;
  - **du contenu de la classe écrit dans un skill** (le nom de son thème
    dans `charte-graphique`, une décision de l'enseignant sur une espèce
    dans `imagier-photos`) : le déplacer **une fois**, dans un commit à lui, dans
    la section balisée qui finit le skill (`<!-- classe:debut -->`, « ##
    Propre à cette classe », `<!-- classe:fin -->`), et rendre au reste du
    skill le texte du moteur ; `chemins_moteur.py verifier` contrôle la
    forme. Dès lors, `copier` la garde à chaque synchronisation.

  Un fichier du moteur modifié ici
  et pas encore remonté serait **perdu** : passer par le skill **remonter-au-moteur**
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

Le script de copie est **celui de la nouvelle version** : c'est elle qui
sait quels sont ses fichiers. On le prend du moteur avant de s'en servir.

```sh
git checkout moteur/main -- scripts/chemins_moteur.py
python3 scripts/chemins_moteur.py copier moteur/main --depuis <moteur.version>
# copie (index compris) les fichiers du moteur de moteur/main, et eux seuls ;
# écarte ce qui est propre au moteur (controles.yml) ;
# repose à la fin de chaque skill neuf sa section propre à la classe ;
# remplace un vieux dossier .claude/skills par le lien vers .agents/skills ;
# retire ce que le moteur a retiré depuis <moteur.version>, s'il n'a pas été
# retouché ici (sinon il le garde et le dit) ; liste ce qui n'existe qu'ici
python3 scripts/chemins_moteur.py verifier   # rien de propre au moteur, sections « Propre à cette classe » bien formées
git ls-files -s .claude/skills         # doit montrer le mode 120000 (un lien, pas un dossier)
python3 scripts/classe.py generer      # refait charte.css : nouveau socle + thème de la classe ;
                                       # et le titre et l'aperçu de lien d'index.html (venu du modèle) ;
                                       # et le bloc de tête du README.md, le reste restant à la classe
python3 scripts/verifier-theme.py      # le thème de la classe tient-il le contrat du nouveau moteur ?
```

Puis le bilan, qui range chaque fichier changé — du moteur, refait par
`classe.py generer`, ou du contenu — et sort en code 1 si le contenu de la
classe a bougé (`classe.yml` n'a le droit de changer que par
`moteur.version`) ; il signale aussi, d'un ⚠, chaque fichier du moteur que
la classe avait retouché et que la copie écrase — à retrouver dans la
nouvelle version, ou à réappliquer (étape 0) :

```sh
python3 scripts/chemins_moteur.py bilan --depuis <moteur.version>
```

et **relire `git diff --cached`** fichier par fichier : rien de la classe
ne doit y apparaître, et une retouche locale déjà remontée doit être
retrouvée dans la nouvelle version (sinon la réappliquer et la signaler à
nouveau). Un skill que la classe avait enrichi d'une leçon à elle : garder
la leçon si elle vaut toujours, en la remontant.

## 3. Mettre la classe d'accord avec le nouveau moteur

- **Le calendrier** : les dates des trois zones arrivent avec `referentiel/`
  (`calendrier-AAAA-AAAA.yml`) ; la classe ne garde que sa zone
  (`calendrier.zone`). C'est ainsi qu'une nouvelle année scolaire parvient
  aux classes : la synchronisation apporte son fichier, puis on change
  `annee` (skill site-et-calendrier). Une classe d'avant ce découpage, qui
  porte encore les dates des trois zones dans `classe.yml`, voit
  `classe.py verifier` refuser ces anciennes clés : ne garder que
  `calendrier: {zone: X}` — la zone qu'utilise l'enseignant, à lui
  demander si rien ne la dit — plus ses ponts propres s'il en a ajouté.
- **Le thème** : il ne se synchronise jamais, mais il dépend des accroches
  du moteur (skill charte-graphique, « Le contrat du thème »).
  `verifier-theme.py` le dit si une accroche a disparu ou si le contrat a
  changé ; le moteur s'engage à ne jamais renommer une accroche. Regarder
  les captures et le PDF avec le nouveau moteur avant de committer.
- **Nouvelles clés de `classe.yml`** : si le moteur en attend une que la
  classe n'a pas, `python3 scripts/classe.py verifier` le dit. L'ajouter
  avec la valeur par défaut annoncée par le skill concerné, et l'annoncer à
  l'enseignant ; ne poser la question que si la valeur change le résultat.
- **`depot` et `origine`** (l'identité de la classe, et la classe d'où elle
  est partie) sont du contenu : jamais copiés depuis le modèle. Une classe
  d'avant ces clés reçoit seulement l'avertissement de `classe.py verifier`
  pour `depot` : le renseigner depuis `git remote get-url origin`
  (`propriétaire/dépôt`), et l'annoncer.
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
moteur (`git checkout HEAD -- $(python3 scripts/chemins_moteur.py chemins)`).

## 5. Committer, noter la version

Mettre `moteur.version` à jour dans `classe.yml` (le commit du moteur
copié : `python3 scripts/chemins_moteur.py ecrire-version moteur/main`),
`classe.py generer`, puis un seul
commit : `Moteur <version courte> : <ce qui change pour la classe>`, avec
dans le corps la liste des contrôles et leurs résultats chiffrés. Fusionner
sur `main` une fois les contrôles verts (AGENTS.md, « Branches, commits,
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
