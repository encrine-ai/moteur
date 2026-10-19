<!-- encrine:moteur -->
<p align="center">
  <a href="https://encrine.ai"><picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://encrine.ai/assets/logo-encrine-craie.svg">
    <img src="https://encrine.ai/assets/logo-encrine.svg" alt="Encrine" width="280">
  </picture></a>
</p>

<p align="center">
  <strong>Case après case, votre année de classe.</strong><br>
  Le moteur d’Encrine : vous répondez à quelques questions, il fabrique la programmation,
  des progressions qui couvrent tout le programme et le matériel de la classe, prêt à imprimer.
</p>

<p align="center">
  <a href="https://encrine.ai">encrine.ai</a> ·
  <a href="https://encrine.ai/tour-du-monde/">La classe d’exemple</a> ·
  <a href="https://github.com/new?template_owner=encrine-ai&amp;template_name=moteur"><strong>Créer ma classe</strong></a> ·
  <a href="https://encrine.ai/design/">Design system</a>
</p>

---

## Comment ça marche

1. **Deux départs.** De zéro, depuis ce modèle ; ou depuis une classe de la
   galerie d’[encrine.ai](https://encrine.ai), avec son bouton « Partir de
   cette classe » : vous gardez son thème, ses périodes, son style et son
   contenu, et votre site crédite son auteur.
2. **L’entretien.** Dans Claude Code, `/nouvelle-classe` pose quelques
   questions — le niveau, la zone de vacances, le thème, le matériel ;
   parti d’une classe, seulement ce qui vous est propre.
3. **Votre mini-site, à votre image.** Le site de la classe, à son thème,
   publié gratuitement sur GitHub Pages et installable comme une appli, avec
   chaque document et chaque cahier en PDF, prêt à imprimer.
4. **Des contrôles qui refusent plutôt que de laisser passer** : tout le
   programme couvert, une page par fiche, la bonne espèce sur chaque
   photographie, des images libres et créditées.
5. **Vos retours.** Vous dites ce qui ne va pas, avec vos mots : votre classe
   est corrigée, et ce qui vaut pour toutes remonte au moteur, puis revient
   dans chaque classe à la mise à jour suivante.

Le détail — les questions de l’entretien, ce que vous recevez, la galerie
des classes — est sur **[encrine.ai](https://encrine.ai)**. La classe
d’exemple, « Le tour du monde », est publiée sur
[encrine.ai/tour-du-monde](https://encrine.ai/tour-du-monde/) (dépôt
[encrine-ai/tour-du-monde](https://github.com/encrine-ai/tour-du-monde)) ;
elle est créée depuis ce modèle, comme la vôtre le sera. Le modèle, lui, ne
publie rien.

## Créer votre classe

Il faut un compte **GitHub** (gratuit) et **Claude Code**, l’agent de code
recommandé et le seul éprouvé (le moteur suit les standards ouverts
`AGENTS.md` et des skills, sans rien promettre pour un autre agent).

1. **Créez votre dépôt** avec **Use this template → Create a new
   repository** : depuis ce modèle
   ([lien direct](https://github.com/new?template_owner=encrine-ai&template_name=moteur)),
   ou depuis la classe de la galerie dont vous partez. Nommez-le (par
   exemple `ma-grande-section`) et choisissez **Public** : GitHub Pages
   publie gratuitement les dépôts publics.
2. **Activez le site** : **Settings → Pages → Source → « GitHub Actions »**.
   C’est le seul réglage à faire à la main.
3. **Ouvrez le dépôt dans Claude Code, sur la branche `main`**, et tapez
   **`/nouvelle-classe`**, sans rien d’autre : l’entretien voit s’il part de
   zéro ou d’une classe déjà là.
4. **Répondez, imprimez, dites ce qui ne va pas.**

> **Travaillez sur `main`.** Pages publie la branche par défaut : une
> session partie sur une autre branche fait échouer le premier déploiement.

Votre site vit alors à `https://<vous>.github.io/<dépôt>/`, et chaque envoi
sur `main` le republie, PDF compris. Le README de votre classe n’est pas
celui-ci : `python3 scripts/classe.py generer` y écrit, entre
`<!-- encrine:debut -->` et `<!-- encrine:fin -->`, un bloc tiré de
`classe.yml` (le projet, le niveau, l’année et la zone, le lien du site, la
licence, « Partir de cette classe » si elle le permet) ; le reste du fichier
est à vous.

## Dans ce dépôt

| Chemin | Rôle |
|---|---|
| `classe.yml`, `classe/` | la classe : son identité, ses périodes, son matériel, son contenu (une classe de départ vide, ici) |
| `site/` | le site de la classe et ses cahiers ; `site/charte/` le design system (un socle commun, un thème par classe) |
| `scripts/` | la fabrication des pages, des images et des PDF, et les contrôles |
| `referentiel/` | le programme en liste numérotée, et le calendrier scolaire officiel des trois zones |
| `.agents/skills/` | les skills (`.claude/skills` y renvoie, pour Claude Code) |
| `AGENTS.md` | les consignes de l’agent, à lire avant de toucher au moteur |

Les contrôles, qui sortent en erreur plutôt que de laisser passer :
`scripts/couverture.py` (chaque attendu du programme relié à une séance),
`scripts/verifier-pagination.py` (une page par fiche et par planche, sur les
PDF eux-mêmes), `scripts/verifier-imagier.py` et
`scripts/chercher-pictos.py verifier` (la bonne espèce, les licences et les
crédits), `scripts/classe.py verifier` (rien de propre à une classe écrit
dans le code).

## Les skills

Chaque capacité a son skill : on demande avec ses mots (« la consigne de la
fiche 2.4 n’est pas claire », « il manque le hérisson dans l’imagier »), et
le bon skill s’ouvre.

| Pour | Skill |
|---|---|
| créer sa classe | `nouvelle-classe` |
| l’année et le programme | `progressions-programme` |
| les fiches et leurs images | `fiches-eleve`, `fiches-illustrations` |
| l’imagier et les cartes | `imagier-photos`, `cartes-corpus` |
| l’apparence et l’impression | `charte-graphique`, `imprimer-pdf` |
| le site et le calendrier | `site-et-calendrier` |
| les retours et les mises à jour | `retours-enseignant`, `remonter-au-moteur`, `synchroniser-moteur` |
| partager sa classe | `partager-ma-classe` |
| retenir ce qu’on apprend | `capitaliser` |

## Ce qui est prêt

- **Grande Section** : prête — la liste numérotée du programme est écrite.
- **Petite et Moyenne Section**, **double niveau** : le matériel se fabrique,
  la liste du programme de ces niveaux est à écrire.
- **Élémentaire** : plus tard.

## Licences

Le **code du moteur** est sous licence MIT (fichier [`LICENSE`](LICENSE)). Le
**contenu des classes**, c’est-à-dire les documents et le matériel, reste sous
la licence choisie par chaque enseignant ; les **polices et les images**
gardent leurs propres licences (SIL Open Font License pour Andika, Bricolage
Grotesque et Atkinson Hyperlegible Next ; ISC pour les icônes Lucide ; la
licence de chaque image dans les crédits de son cahier).

## Vos mentions légales, et le nom « Encrine »

**Vos mentions légales.** Le pied de votre site porte « Conçu avec Encrine »
et « Mentions légales », une page fabriquée depuis `classe.yml` : sur votre
site, **c’est vous l’éditeur** (un site personnel non professionnel, signé
comme vous signez votre classe ; contact : votre compte GitHub, ou
`enseignant.contact`), GitHub Pages l’hébergeur, et le site ne collecte
aucune donnée personnelle. Encrine n’est pas l’éditeur de votre site et n’en
a pas vérifié le contenu ; la copie relue d’une classe de la galerie, servie
sur encrine.ai, porte les mentions d’Encrine. Si vous avez déjà vos propres
pages, `mentions_legales: https://…` y renvoie.

**Utiliser le nom « Encrine ».** Vous pouvez dire que votre site est « conçu
avec Encrine » ou « fait avec Encrine », avec un lien vers
https://encrine.ai — l’outil le pose de lui-même au pied de chaque page.
Vous ne pouvez pas laisser croire qu’Encrine a relu, approuvé ou publie votre
site (seules les copies relues de la galerie, servies sur encrine.ai, le
sont), utiliser le logo d’Encrine comme le vôtre, ni nommer votre classe ou
votre site « Encrine ». Pour signaler un site qui utilise le nom de façon
trompeuse : https://encrine.ai/contact/.
