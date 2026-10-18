---
name: progressions-programme
description: Écrire ou modifier le projet annuel, la programmation, une progression de domaine (03-progressions/) ou une batterie d'évaluation (04-evaluations/), en restant conforme au programme de l'école maternelle (cycle 1, BO n°19 du 7 mai 2026, BO n°41 du 31 octobre 2024, EVAR) — et prouver que l'année le couvre avec referentiel/ et scripts/couverture.py. À utiliser pour ajouter ou déplacer une séance, une notion, un album, une sortie, un corpus de vocabulaire, une fiche d'évaluation, pour changer le thème d'une période, ou pour répondre à « est-ce que l'année couvre tout le programme ? ». Se déclenche aussi sans nom de fichier : « il faudrait travailler les rimes plus tôt », « ajoute la comptine jusqu'à 30 en période 2 », « on peut faire la ferme en période 5 ? », « il manque quelque chose du programme ? », « remplace Le Gruffalo par un autre album », « ajoute une fiche d'évaluation sur les solides ». Ne concerne pas la mise en page d'une fiche élève imprimable (fiches-eleve).
---

# Les progressions et le programme

L'année est un **projet** (`projet` dans classe.yml — ici « À la découverte
de la faune et de la flore »), un **thème par période** (`periodes` — ici cinq
milieux : ville, forêt, montagne, campagne, mer), et
sept **progressions** de domaine qui déclinent chaque période dans un tableau.
Tout est écrit en Markdown, en français, et rendu tel quel par le site.

| Fichier | Ce qu'il porte |
|---|---|
| `01-projet-annuel.md` | intentions, fils rouges, calendrier, **trois corpus de vocabulaire par période** (le milieu, la faune, la flore), albums, chants, œuvres, sorties |
| `02-programmation-annuelle.md` | le « quoi, quand » : tous les domaines × les 5 périodes |
| `03-progressions/0N-*.md` | le « comment, dans quel ordre » : un rappel du programme, puis un tableau par période (Champ · Objectifs · Situations thématisées · Fin de période) |
| `04-evaluations/` | le mode d'emploi et livret de suivi, puis une batterie par période (fiches X.1…X.n, grilles d'observation, récapitulatif) |
| `referentiel/cycle1-gs.yml` | 159 attendus du programme, un par ligne, avec un identifiant stable |
| `classe/annotations.yml` | ce que chaque période de chaque document traite (les accroches) |

## La règle qui gouverne tout le reste

**Toute modification d'une progression se termine par :**

```sh
python3 scripts/couverture.py            # 159 attendus ; code 1 s'il en manque
python3 scripts/couverture.py --manques  # seulement ce qui cloche
```

Une séance ajoutée sans accroche dans `classe/annotations.yml` **n'est pas
comptée** : ajouter l'identifiant de l'attendu au bloc `document` × `periode`
concerné. Une séance retirée retire aussi son accroche — sinon le contrôle
reste vert sur un attendu que plus rien ne traite. C'est exactement ce qui
s'était produit : l'année *annonçait* trois attendus qu'aucune séance ne
traitait ; ils ont été comblés (commit « Comble les trois attendus que l'année
annonçait sans les traiter »).

**La programmation et les progressions disent la même chose.** Un des trois
trous venait de là : un champ « Articulation » présent dans
`02-programmation-annuelle.md` et absent de la progression de langage. Une
notion ajoutée à l'une s'ajoute à l'autre.

**Une modification pédagogique se propose, elle ne se glisse pas.** Ce qui
part en classe, et que les familles lisent sur le site, est relu par
l'enseignante : présenter la séance ajoutée et la faire valider, sauf
demande explicite de l'écrire directement. Les sept lignes ajoutées pour
combler les trous (cinq « Articulation » en langage, deux « Environnement »
— charte du promeneur en P2, ramassage raisonné des déchets de plage en
P5) attendent encore cette relecture.

## Ce que le référentiel peut contenir, et ce qu'il ne doit pas contenir

- `cycle1-gs.yml` ne contient **que des exigences du programme**, relues contre
  le BO. Une règle que la classe se donne (le nombre d'espèces de l'imagier,
  trois corpus de quinze mots…) n'y a pas sa place : logée parmi les autres,
  elle laisse croire que le programme la prescrit — ce qui a déjà été affirmé
  à tort. Ces conventions vivent dans le script du matériel concerné
  (`verifier-imagier.py`, `verifier-cartes-corpus.py`).
- Les lignes actuelles décomposent les rappels de programme des progressions :
  elles restent **à relire contre le texte officiel**. Ne jamais présenter le
  référentiel comme le BO, ni citer un attendu sans dire d'où il vient.
- Ne pas inventer d'attendu « pour que le contrôle passe ». Un manque se comble
  par une séance, pas par une ligne.

## Écrire dans une progression

- Garder la structure : un `## Période N — <milieu>` par période (le site
  repère « Période N » dans les titres pour y poser le badge de dates de la
  zone, et en tire les extraits imprimables par période) ; un tableau par
  période, une ligne par champ.
- **Ne jamais écrire une date de période à la main** dans un document : elle
  dépend de la zone. Le badge la calcule (`GS.annoteTitres`). Une date fixe
  pour toutes les zones (rentrée, Toussaint, Noël, fin d'année) peut s'écrire.
- Chaque situation est **thématisée par le milieu** de la période : c'est le
  principe du projet. Un exercice hors milieu doit avoir une raison.
- Démarche à respecter en maths : manipulation → représentation →
  verbalisation → abstraction. En langage : les trois corpus s'enseignent
  explicitement (apport → structuration → mémorisation → réemploi) et
  s'évaluent chaque mois.
- EVAR : les trois séances spécifiques obligatoires restent dans
  `07-evar.md`, avec leur fil continu.

## Écrire une batterie d'évaluation

- Une fiche = `## Fiche X.n — Domaine : titre *(modalité, durée)*`, puis
  **Compétence**, **Matériel**, **Où le trouver**, **Passation**, **Critères**
  (A / EC / NE).
- **Où le trouver** renvoie à l'une des trois provenances, et à aucune autre :
  *fourni, à télécharger* (fiche élève, cartes-corpus, imagier),
  *matériel de classe*, *à fabriquer en classe*. Rien n'est mentionné sans
  qu'on puisse dire où le prendre — c'est ce que le dépôt a dû réparer quand
  les fiches X.1 réclamaient « 12 cartes-images » que rien ne fabriquait.
- Évaluation **positive** : observation en situation d'abord, la fiche n'est
  qu'une trace ; jamais de « contrôle ». Une compétence codée EC/NE est
  reprise à la période suivante, à un niveau supérieur.
- Une fiche qui a un support élève imprimable renvoie au skill
  [`fiches-eleve`](../fiches-eleve/SKILL.md) ; ses mots de vocabulaire, au skill
  [`cartes-corpus`](../cartes-corpus/SKILL.md).

## Ce qui dépend d'une progression

| Si l'on change… | …il faut aussi |
|---|---|
| un corpus de `01-projet-annuel.md` | le manifeste des cartes-corpus (skill cartes-corpus) |
| une espèce citée dans une séance | l'imagier, s'il doit la montrer (skill imagier-photos) |
| une fiche d'évaluation | la fiche élève correspondante (skill fiches-eleve) |
| le thème d'une période | tout ce qui précède, et `periodes` dans `classe.yml` (milieu, icône, couleur, phrase de l'imagier) — c'est un changement de projet, pas une retouche |

Finir par `couverture.py`, puis par le PDF du document modifié (skill
[`imprimer-pdf`](../imprimer-pdf/SKILL.md)) : un tableau qui s'allonge peut
pousser une période sur une page de plus, ce qui est permis pour un document
— mais il faut l'avoir regardé.
