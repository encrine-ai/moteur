---
name: fiches-eleve
description: Créer, modifier ou corriger une fiche élève imprimable de Ma Grande Section (site/fiches/) — les cahiers d'évaluation (periode-N.html) et d'entraînement (entrainement-periode-N.html, séries A ★ et B ★★ avec sous-objectifs et défis) — en respectant sa structure A4, la consigne donnée à l'oral, le codage, la police des mots de l'enfant et la règle d'une fiche par page. À utiliser pour ajouter une fiche ou un exercice, changer une consigne, adapter une fiche à un autre niveau, réparer une fiche qui déborde, ou aligner une fiche sur sa fiche d'évaluation (04-evaluations/). Se déclenche aussi sans nom de fichier : « il faudrait une fiche d'entraînement sur les rimes », « la consigne de la fiche 3.4 n'est pas claire », « ajoute un exercice de dénombrement jusqu'à 10 », « les cases sont trop petites pour écrire », « fais une version plus facile ». Pour choisir ou remplacer une image de fiche, charger aussi fiches-illustrations.
---

# Les fiches élève

Des feuilles **A4 individuelles, à photocopier**. L'enseignante donne la
consigne **à l'oral** ; la fiche la rappelle en encadré pour les familles. Les
enfants ont cinq ans et ne lisent pas encore : l'image et la mise en page
portent l'exercice.

| Cahier | Fichier | Contenu |
|---|---|---|
| Évaluation | `site/fiches/periode-N.html` | les supports des fiches X.n de `04-evaluations/periode-N-*.md` qui en demandent un |
| Entraînement | `site/fiches/entrainement-periode-N.html` | 12 fiches : série A (★ je m'entraîne) et série B (★★ je consolide), 2 à 3 par semaine |
| Crédits | dernière section de chaque cahier | générée par `scripts/generer-credits.py` |

## La structure d'une fiche

```html
<section class="fiche">            <!-- class="fiche paysage" pour l'A4 à l'italienne -->
  <div class="entete">
    <div class="idext"><span class="champ">Prénom : <span class="trait"></span></span>…Date…</div>
    <div class="cartouche"><div class="ref">Période 2 · Fiche élève 1</div>
      <div class="dom">Phonologie — rimes (éval. 2.3)</div></div>
  </div>
  <div class="titre">J'entends les rimes de la forêt</div>
  <!-- entraînement seulement : -->
  <span class="niveau n1">★ je m'entraîne</span> (dans le titre) · <div class="sous-objectif">…(prépare la fiche d'évaluation 2.3)</div>
  <div class="consigne"><strong>Consigne :</strong> <strong>1.</strong> …</div>
  <div class="exo"><span class="num">1</span> <span class="enonce">J'entoure…</span> …</div>
  <!-- entraînement seulement : --> <div class="defi"><span class="etoile">★ Défi :</span> …</div>
  <div class="pied-fiche"><span>Compétence : …</span><span class="codage">A ☐ · EC ☐ · NE ☐</span></div>
</section>
```

- Le `<body data-periode="N">` du cahier donne la couleur de la période au
  cartouche, au titre et aux numéros (skill charte-graphique). Rien ne doit
  dépendre de cette couleur : la fiche se photocopie en noir et blanc.
- Codage : **A / EC / NE** sur une fiche d'évaluation ; **Seul · Avec aide · À
  revoir** sur une fiche d'entraînement.
- Les énoncés sont à la première personne de l'enfant (« J'entoure si
  j'entends « ou » à la fin »). La consigne est numérotée comme les
  exercices et écrite **telle que l'enseignante la dit à l'enfant**, au
  tutoiement : « Entoure toutes les lettres de ton prénom dans la grille. »
  Les familles lisent ainsi ce qui a été dit en classe. Jamais de mention
  « consigne dite à l'oral » : l'enseignante l'a refusée, l'encadré
  *Consigne :* suffit. (Une version antérieure de ce skill disait que la
  consigne « s'adresse à l'adulte » ; les fiches, elles, suivent la demande
  de l'enseignante, et c'est la règle.)
- Chaque fiche d'entraînement dit quelle fiche d'évaluation elle prépare ; la
  série B reprend les notions de la série A à un niveau supérieur.

## Ce qu'une fiche doit contenir

Ce sont des demandes de l'enseignante, chacune née d'un premier jet refusé.

- **Une fiche remplit sa page** : trois à cinq exercices, de quoi occuper
  vraiment l'enfant. Les premiers cahiers ont été jugés « trop légers en
  termes de travail, ça va être trop vite fait » et tous enrichis (commits
  « Enrichit les fiches de la période N », de 158 à 269 exercices). Modèle :
  les fiches du commerce — bandes de discrimination, dominos des
  compléments, colorie-autant-que, bandes numériques à trous, sériations,
  quadrillages, alphabet à compléter, tableaux OUI / NON, graphisme, dictées.
- **Un niveau un peu soutenu.** La classe a de bonnes compétences
  (« on peut un peu corser les exercices ») : viser le haut des attendus de
  GS, sans sortir du programme. La série ★★ et les défis portent l'écart.
- **Deux à trois fiches par semaine**, d'où les douze fiches d'entraînement
  par période en plus des fiches d'évaluation.
- **Chaque fiche est habillée au milieu de la période** — le parking, les
  réserves de l'écureuil, le télésiège, le marché aux œufs, la sirène. Un
  exercice hors thème doit avoir une raison.
- **Le paysage pour les grands formats.** Quand l'exercice ne remplit pas un
  portrait — reconstitution d'un mot avec des lettres à découper, grille de
  lettres —, la fiche passe en `fiche paysage` : il faut de grosses lettres.
  Portrait et paysage cohabitent dans un même PDF par les `@page` nommées de
  `fiches.css`.
- **Le modèle de cursive est écrit par l'enseignante**, à la main (« lettres
  données par la maîtresse », « la maîtresse ajoute la cursive au dos ») :
  aucune police n'imite correctement le modèle de l'école. Si une police
  devait un jour s'imposer, la piste retenue est *Marelle* (cursive
  soutenue par la DNE, licence SIL OFL) — pas Belle Allure ni Cursive
  Dumont, qui excluent l'usage commercial.

## Les règles du papier

1. **Une fiche = une page A4.** Vérifié au PDF par
   `scripts/verifier-pagination.py` (skill [`imprimer-pdf`](../imprimer-pdf/SKILL.md)),
   jamais à l'œil sur le HTML. Une fiche qui déborde se resserre **localement**
   (un `style` sur ses éléments), pas dans `fiches.css`, qui déplacerait les
   autres.
2. **Les mots que l'enfant lit sont en Andika** (`--police-enfant`), avec les
   classes existantes (`.case`, `.item`, `.al`, `.carte-lettre`…). Un mot
   nouveau dans un élément qui n'en a pas : l'envelopper dans un `.case` ou
   ajouter la classe à la liste en fin de `fiches.css`.
3. **Des cases où une main de cinq ans peut écrire** : lettres ≥ 10 × 12 mm,
   chiffres ≥ 13 × 15 mm (`.lettre-case`, `.chiffre-case`).
4. **Des images, jamais d'émoji ni de dessin fait main.** Pictogrammes Mulberry
   d'abord, ARASAAC sinon, Openverse en dernier recours — toute la procédure
   (et ses pièges : « chicken » était un poulet rôti) est dans
   [`fiches-illustrations`](../fiches-illustrations/SKILL.md). `scripts/remplace-emojis.py`
   convertit les anciens émojis en `<img class="pic">`.
5. **Le matériel existe.** Ce que la fiche suppose (cartes, étiquettes de tri,
   lettres à découper) doit être fourni, de la classe, ou à fabriquer avec les
   élèves — et nommé dans « Où le trouver » de la fiche d'évaluation.

## Après une modification

```sh
python3 scripts/generer-credits.py          # la page des crédits suit les images employées
python3 scripts/chercher-pictos.py verifier # licence de chaque crédit (ND exclu, NC = ARASAAC seulement)
```

puis le PDF du cahier et `verifier-pagination.py`, puis un regard sur la page
rendue (`pdftoppm`). Si la fiche correspond à une fiche d'évaluation, relire
celle-ci dans `04-evaluations/` : même numérotation, même matériel, mêmes
critères.
