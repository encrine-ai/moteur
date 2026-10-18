# Encrine — le moteur

Un **dépôt modèle** pour fabriquer l'année d'une classe : la programmation,
des progressions qui couvrent le programme, les fiches élève, l'imagier, les
cartes de vocabulaire et tous les PDF, prêts à imprimer. On ne programme
rien : on répond à quelques questions, et le skill **`/nouvelle-classe`**
écrit la classe dans `classe.yml` et fabrique le reste.

Pour voir ce que cela donne : la **classe de démonstration**, une Grande
Section « Le tour du monde », un continent par période, publiée sur
**https://encrine.ai/tour-du-monde/** (dépôt
[encrine-ai/tour-du-monde](https://github.com/encrine-ai/tour-du-monde)).
Elle est créée depuis ce modèle, comme la vôtre le sera ; ses documents
arrivent période par période. Le modèle, lui, ne publie rien.

▶ **[encrine.ai](https://encrine.ai)** — le principe, et « Les classes » que
des enseignants ont choisi de partager.

---

## Créer sa classe, en quatre étapes

1. **Use this template → Create a new repository.** Sur la page de ce dépôt,
   le bouton vert **« Use this template »** — ou directement
   **[github.com/new?template_owner=encrine-ai&template_name=moteur](https://github.com/new?template_owner=encrine-ai&template_name=moteur)** ; nommez votre classe (par
   exemple `ma-grande-section`) et choisissez **Public** — GitHub Pages
   publie gratuitement les dépôts publics. Vous obtenez votre propre dépôt :
   le moteur entier et une classe de départ, que l'entretien remplace par la
   vôtre.
2. **Activez le site** : dans votre dépôt, **Settings → Pages → Source →
   « GitHub Actions »**. C'est le seul réglage à faire à la main.
3. **Ouvrez le dépôt dans Claude Code, sur la branche `main`**, et tapez
   **`/nouvelle-classe`**. L'entretien vous demande le niveau, votre zone de
   vacances (le site et les PDF prennent ses dates), le thème de l'année, le matériel voulu ; il commence par une
   période complète, ou par les cinq si vous le préférez.
4. **Répondez, imprimez, dites ce qui ne va pas.** Vos retours corrigent votre
   classe ; ce qui vaut pour tous remonte au moteur, avec votre accord, et
   revient dans chaque classe à la mise à jour suivante.

> **⚠️ Travaillez sur `main`.** Pages publie la branche par défaut : une
> session partie sur une autre branche fait échouer le premier déploiement.

Votre site vit alors à `https://<vous>.github.io/<dépôt>/`, et chaque envoi
sur `main` le republie, PDF compris.

---

## Ce que le moteur garantit

Des contrôles qui sortent en erreur plutôt que de laisser passer :

- **le programme** : chaque attendu de la liste numérotée (`referentiel/`)
  relié à une séance — `scripts/couverture.py` refuse une année incomplète ;
- **l'impression** : une page par fiche et par planche, vérifiée sur les PDF
  eux-mêmes — `scripts/verifier-pagination.py` ;
- **les images** : licences libres et crédits, la bonne espèce sur chaque
  photographie — `scripts/verifier-imagier.py`, `scripts/chercher-pictos.py verifier` ;
- **la classe à sa place** : rien de propre à une classe écrit dans le code —
  `scripts/classe.py verifier`.

## Les skills

Chaque capacité a son skill, dans `.claude/skills/` : on demande avec ses mots (« la consigne de la fiche 2.4 n'est pas claire », « il manque le hérisson dans l'imagier »), et le bon skill s'ouvre.

| Pour | Skill |
|---|---|
| créer sa classe | `nouvelle-classe` |
| l'année et le programme | `progressions-programme` |
| les fiches et leurs images | `fiches-eleve`, `fiches-illustrations` |
| l'imagier et les cartes | `imagier-photos`, `cartes-corpus` |
| l'apparence et l'impression | `charte-graphique`, `imprimer-pdf` |
| le site et le calendrier | `site-et-calendrier` |
| les retours et les mises à jour | `retours-enseignant`, `remonter-au-moteur`, `synchroniser-moteur` |
| partager sa classe | `partager-ma-classe` |
| retenir ce qu'on apprend | `capitaliser` |

## Ce qui est prêt

- **Grande Section** : prête — la liste numérotée du programme est écrite.
- **Petite et Moyenne Section**, **double niveau** : le matériel se fabrique,
  la liste du programme de ces niveaux est à écrire.
- **Élémentaire** : plus tard.

## Licences

Le **code du moteur** est sous licence MIT (fichier [`LICENSE`](LICENSE)). Le
**contenu des classes**, c'est-à-dire les documents et le matériel, reste sous
la licence choisie par chaque enseignant ; les **polices et les images**
gardent leurs propres licences (SIL Open Font License pour Andika, Bricolage
Grotesque et Atkinson Hyperlegible Next ; ISC pour les icônes Lucide ; la
licence de chaque image dans les crédits de son cahier).
