# Le référentiel du programme, et le contrôle de couverture

Ce dossier contient le référentiel ; un contrôle le confronte aux annotations de la classe :

| Fichier | Ce qu'il est |
|---|---|
| [`cycle1-gs.yml`](cycle1-gs.yml) | **159 attendus** du programme, un par ligne, chacun avec un identifiant stable — plus 5 règles de cadre |
| [`classe/annotations.yml`](../classe/annotations.yml) | **286 accroches** : ce que chaque période de chaque progression traite. C'est du contenu de la classe, désigné par `contenu.annotations` dans `classe.yml` |
| `scripts/couverture.py` | la soustraction des deux, et le rapport |

```sh
python3 scripts/couverture.py             # le rapport
python3 scripts/couverture.py --manques   # seulement ce qui cloche
python3 scripts/couverture.py --domaine langage
```

## 1. Le référentiel : de la prose à des lignes numérotées

Le programme existe sous trois formes, toutes trois inutilisables par une
machine : le texte du Bulletin officiel, sa reprise en prose au début de
chaque progression (« Attendus travaillés en GS — rappel du programme »), et
la mémoire de l'enseignante.

Le référentiel en fait des **lignes numérotées** :

```yaml
- {id: math.qte.comptine-30, domaine: Mathématiques, sous_domaine: Quantités,
   libelle: "Dire la suite orale des nombres jusqu'à 30"}
```

L'identifiant est tout l'enjeu. Tant que « dire la suite jusqu'à 30 » n'est
qu'une phrase dans un paragraphe, on ne peut rien en faire. Dès qu'elle porte
un nom, on peut la compter, la citer, et constater qu'elle manque.

Les 159 lignes se répartissent ainsi : Langage 39, Mathématiques 34,
Activités artistiques 24, Temps et espace 21, Monde du vivant 20, Activités
physiques 16, EVAR 5.

> **Sur la source.** Ces lignes sont la décomposition des rappels de
> programme des sept progressions de ce dépôt — donc d'une lecture déjà
> faite du programme, et non du texte officiel. Chaque ligne doit être relue
> contre le BO n°19 du 7 mai 2026 et le BO n°41 du 31 octobre 2024, et
> porter sa référence exacte. Un référentiel approximatif rendrait le
> contrôle faux, donc pire qu'inutile.

## 2. Les annotations : ce que l'année traite

Chaque bloc dit : dans ce document, à cette période, ces attendus-là sont
travaillés.

```yaml
- document: 03-progressions/02-mathematiques.md
  periode: 3
  attendus: [math.qte.rebours, math.rang.bande, math.pb.ecarts,
             math.for.solides, math.gr.masse-roberval, math.mot.evolutifs]
```

Établi en relisant les cinq tableaux de chacune des sept progressions.

**Maille : le document et la période.** C'est ce que permettent les tableaux
existants — un tableau par période, une ligne par champ. Dans la plateforme,
la maille sera la **séance**, ce qui donnera en plus le nombre de rencontres
de chaque attendu, et non seulement leur existence.

Les accroches traversent les domaines quand la réalité de la classe le fait :
les tangrams de la période 4 en mathématiques servent aussi
`te.esp.assemblages`, et l'affiche « en temps limité » des arts de la
période 5 sert `te.tps.organiser`. C'est exactement ce qu'un contrôle par
mots-clés, document par document, ne saurait pas voir.

## 3. Le résultat

Au premier passage, **156 attendus sur 159**. Les trois manques ont été
comblés (§4), et l'année est désormais complète :

```
  159 attendus couverts sur 159   (100 %)

    ██████████████████ 39/39  Langage
    ██████████████████ 34/34  Mathématiques
    ██████████████████ 24/24  Activités artistiques
    ██████████████████ 21/21  Temps et espace
    ██████████████████ 20/20  Monde du vivant
    ██████████████████ 16/16  Activités physiques
    ██████████████████  5/5   EVAR
```

Les quatre règles de cadre vérifiables passent également : 3 séances d'EVAR,
13 unités d'EPS toutes chiffrées entre 6 et 8 séances, 15 corpus de
vocabulaire, 3 œuvres patrimoniales.

Le nombre d'espèces de l'imagier a un temps figuré ici. Il n'y avait pas sa
place : c'est une convention que la classe s'est donnée pour son matériel,
et rien dans le programme ne prescrit un nombre d'espèces. Mêlée aux règles
du BO, elle laissait croire le contraire. Elle est vérifiée par
`scripts/verifier-imagier.py`.

## 4. Les trois trous — trouvés, puis comblés

Ils avaient un point commun qui les rendait intéressants : **les documents
les annonçaient, et aucune période ne les traitait.** Le document de
programmation `02-programmation-annuelle.md` porte une ligne « Articulation »
complète, période par période — et la progression de langage n'avait tout
simplement pas ce champ dans ses tableaux. C'est une incohérence entre deux
documents qui ne se lisent jamais côte à côte, et qu'aucune relecture
humaine ne repère. Une recherche par mots-clés ne l'aurait pas vue non plus :
elle aurait trouvé ces attendus dans le rappel de programme en tête de
fichier et les aurait déclarés couverts.

| Attendu | Ce qui manquait | Ce qui a été écrit |
|---|---|---|
| Prononcer les doubles consonnes br, cr, bl, pl, sl (`lang.art.doubles`) | la progression de langage n'avait aucune ligne « Articulation » | une ligne **Articulation** dans les **cinq** périodes, reprenant exactement la répartition qu'annonçait déjà la programmation : t/k et f/s en P1, ch/s et ch/j en P2, les doubles consonnes en P3 (*brume, cristal, blizzard, slalom* — le lexique de la montagne s'y prête), ch/z et p/b en P4, consolidation en P5 |
| Prononcer les 36 phonèmes avec exactitude (`lang.art.phonemes-36`) | idem ; c'est un attendu de fin de maternelle | le bilan de la ligne Articulation en P5 : s'enregistrer sur 20 mots tirés des 15 corpus de l'année, relevé individuel des phonèmes encore fragiles transmis avec le dossier de liaison CP |
| Agir de manière autonome pour le respect de l'environnement (`monde.mat.environnement`) | rien, alors que le projet s'y prête entièrement | une ligne **Environnement** en P2 (charte du promeneur écrite avant la sortie, déchets du goûter rapportés, tri en classe) et en P5 (ramassage raisonné, frise « combien de temps ça reste ? », retour sur la charte de P2) |

Le parti pris, pour les deux premiers : plutôt que de rustiner l'attendu
manquant dans la période la plus commode, **rétablir le champ entier** sur
les cinq périodes, en suivant la progression que la programmation annonçait.
Les deux documents disent maintenant la même chose.

Ce n'étaient pas des reproches à l'année : sur 159 exigences, en trouver
trois oubliées est un bon résultat. Mais ces trois-là seraient passées
inaperçues, et c'est la démonstration que le contrôle sert à quelque chose.

## 5. Ce que le contrôle ne dit pas encore

Il signale 87 attendus « rencontrés dans une seule période ». À cette maille,
le signal est faible : une séance d'EVAR est unique par construction, et un
attendu peut être repris cinq fois dans la même période sans que cela se
voie. Ce chiffre deviendra exploitable quand les accroches seront portées par
les séances elles-mêmes — et c'est alors qu'il dira quelque chose qu'aucune
relecture humaine ne sait dire : *cet attendu n'est rencontré qu'une fois
dans l'année, il ne sera pas acquis.*

## 6. Ce qu'il reste à faire

1. **Relire les 159 lignes contre le texte officiel** et leur donner leur
   référence exacte. C'est le travail sérieux, et il ne peut pas être fait
   depuis les rappels du dépôt.
2. **Distinguer** ce qui est prescrit de ce qui est recommandé, et les
   attendus de fin de cycle des repères par âge (PS, MS, GS) — le référentiel
   doit servir les trois niveaux, pas seulement la GS.
3. **Descendre à la séance** : accrocher les identifiants aux séances plutôt
   qu'aux périodes.
4. **Combler les trois trous** ci-dessus dans les progressions.
5. **Verrouiller la règle** dans la plateforme : une séance sans attendu
   déclaré ne peut pas être publiée. Le script sort en code 1 quand il manque
   un attendu ou qu'une annotation cite un identifiant inconnu — il est donc
   utilisable tel quel comme contrôle de publication.
