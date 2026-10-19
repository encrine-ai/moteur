---
name: reprendre-ma-classe
description: La première session de l'enseignant après le TRANSFERT de sa classe sur son compte GitHub (une classe préparée pour lui par un accompagnant, puis « Transfer ownership ») — voir que le dépôt a changé de propriétaire, mettre `depot` (et `site`, si besoin) à jour dans classe.yml, régénérer, refaire tous les contrôles jusqu'au PDF, vérifier le réglage de GitHub Pages, publier et voir le site en ligne à sa nouvelle adresse, puis dire ce qui change pour lui (l'ancienne adresse, l'appli du téléphone, les liens donnés) et proposer de garder l'accompagnant comme collaborateur. Se déclenche sur : « je reprends ma classe », « on m'a transféré ma classe », « c'est mon dépôt maintenant », « la classe est sur mon compte », « mets à jour classe.yml avec mon dépôt », « j'ai accepté le transfert », « mon site ne marche plus depuis le transfert ». Ne concerne pas une classe neuve (nouvelle-classe) ni la mise à jour de l'outil (synchroniser-moteur).
---

# Reprendre ma classe

Une classe peut être **préparée pour un enseignant par quelqu'un d'autre**
— l'accompagnant (`accompagnant` dans `classe.yml`, skill nouvelle-classe,
« Pour quelqu'un d'autre ») — puis **transférée** sur le compte GitHub de
l'enseignant (*Settings → General → Transfer ownership*, accepté par
lui). GitHub redirige l'ancien dépôt, **pas l'ancien site** : l'adresse
`https://<ancien>.github.io/<dépôt>/` cesse de répondre. Cette session-ci
est la première de l'enseignant chez lui ; elle lui parle comme le dit
`PRISE-EN-MAIN.md` (« Le premier lancement, après le transfert »), sans
détail technique, et finit par un site en ligne qu'il a vu.

## 1. Voir le changement de propriétaire

```sh
git remote get-url origin                     # …github.com/<nouveau>/<dépôt>(.git)
python3 -c "import yaml;print(yaml.safe_load(open('classe.yml'))['depot'])"
```

- `origin` et `depot` désignent le **même** dépôt : rien n'a été transféré
  (ou c'est déjà fait). Le dire, et vérifier seulement que le site est en
  ligne (étapes 4 et 5).
- Ils diffèrent **par le propriétaire** : c'est le transfert. Retenir
  l'ancien `depot` (pour l'ancienne adresse et l'accompagnant).
- Ils diffèrent **par le nom du dépôt aussi** : un renommage, à traiter de
  même (la nouvelle adresse change de nom).
- `origin` est dans `encrine-ai/` : c'est une copie relue de la galerie,
  pas une classe reprise — ne rien changer, et le dire.

Travailler sur `main` (Pages publie la branche par défaut), à jour :
`git fetch origin && git status`.

## 2. Mettre la classe à son nom

Dans `classe.yml`, et rien d'autre du contenu :

- **`depot`** ← `<nouveau>/<dépôt>`, tel que `origin` l'écrit.
- **`site`** : s'il pointait vers l'ancien compte
  (`https://<ancien>.github.io/…`), le retirer — l'adresse se tire alors
  de `depot`. Un domaine propre (ni l'ancien compte, ni `encrine.ai`) se
  garde, mais le domaine doit être reconfiguré dans *Settings → Pages* du
  nouveau dépôt : le dire.
- **`partage.carte`** (la carte de la classe dans la galerie, si elle a
  été partagée) : l'adresse de la carte ne change pas, mais la galerie
  nomme le dépôt de l'auteur. Proposer, sans le faire seul, de mettre la
  copie à jour (skill partager-ma-classe, « mise à jour »).
- **`enseignant.signature`** et `enseignant.contact` : les mentions légales
  du site (#/mentions-legales) prennent pour éditeur la signature et pour
  contact le compte GitHub du propriétaire de `depot` — désormais le
  sien. Ne rien changer sauf s'il le demande.
- **`accompagnant`** reste : il nomme qui a préparé la classe, et
  `PRISE-EN-MAIN.md` dit de lui demander de l'aide.

Puis `python3 scripts/classe.py generer` (le bloc du README, le lien du
site, `PRISE-EN-MAIN.md`, l'aperçu de lien) et `python3 scripts/classe.py
verifier`.

**`AGENTS.md`** : s'il parle encore à l'accompagnant comme au propriétaire,
ou porte une consigne pour la reprise (« à la reprise, passer à la voix de
l'enseignant… »), le réécrire à la voix du nouveau propriétaire —
« c'est la classe de <signature>, son enseignant et le propriétaire de ce
dépôt » ; l'accompagnant devient « collaborateur, qui peut aider ; les
décisions restent les siennes ». Ne toucher qu'à ces passages.

## 3. Tous les contrôles, jusqu'au PDF

Comme pour toute publication (AGENTS.md) : `classe.py verifier`,
`verifier-theme.py`, `verifier-partage.py`, `chemins_moteur.py verifier`,
`couverture.py` (code 0), puis le site assemblé, `generer-pdf.sh` et
`verifier-pagination.py` (skill imprimer-pdf). Rien n'est publié tant
qu'un contrôle est rouge.

## 4. Le réglage de GitHub Pages

Le transfert ne garde pas toujours le réglage. Il faut *Source : GitHub
Actions* :

```sh
gh api repos/<nouveau>/<dépôt>/pages --jq .build_type        # « workflow » attendu
gh api -X POST repos/<nouveau>/<dépôt>/pages -f build_type=workflow   # s'il n'existe pas (404)
gh api -X PUT  repos/<nouveau>/<dépôt>/pages -f build_type=workflow   # s'il est sur « legacy »
```

Si l'API refuse (droits, proxy de la session), ne pas contourner : lui
donner le lien exact, `https://github.com/<nouveau>/<dépôt>/settings/pages`,
et le geste (*Build and deployment* → *Source* → **GitHub Actions**), puis
attendre qu'il dise que c'est fait.

## 5. Publier, et le voir en ligne

Un commit (auteur `Claude <noreply@anthropic.com>`, jamais l'adresse de
l'enseignant) qui dit le transfert, sur `main`, poussé. Puis suivre le
déploiement (`gh run list --workflow pages.yml`, `gh run watch`) et
**ouvrir la nouvelle adresse** : la page d'accueil répond, un PDF répond,
les mentions légales nomment le bon contact. Ne dire « c'est en ligne »
qu'après l'avoir vu ; donner le lien.

## 6. Ce qui change pour lui, en mots simples

- **L'ancienne adresse ne marche plus** (GitHub ne redirige pas les sites) :
  l'appli installée sur son téléphone ou sa tablette est à réinstaller
  depuis la nouvelle adresse ; les liens donnés (collègues, familles, code
  QR, ENT) sont à redonner.
- Son site, ses PDF et son dépôt sont désormais **à lui** ; la suite est
  dans `PRISE-EN-MAIN.md` (« Ce que tu peux dire ensuite »).

## 7. L'accompagnant, s'il doit continuer à aider

Le transfert retire à l'ancien propriétaire ses droits sur le dépôt.
Demander à l'enseignant (une question, `AskUserQuestion`) s'il veut que
`accompagnant` reste collaborateur. Sur un oui :

```sh
gh api -X PUT repos/<nouveau>/<dépôt>/collaborators/<accompagnant.github> -f permission=push
```

L'accompagnant accepte l'invitation de son côté. Si l'API refuse : *Settings
→ Collaborators → Add people*, avec le lien exact.

## Ce qu'il ne faut pas faire

- Toucher au contenu de la classe (progressions, fiches, images, textes) :
  la reprise ne change que l'adresse.
- Garder `site` sur l'ancien compte « pour ne rien casser » : le README,
  l'aperçu de lien et l'appli pointeraient vers une adresse morte.
- Annoncer la nouvelle adresse avant d'avoir vu le site y répondre.
