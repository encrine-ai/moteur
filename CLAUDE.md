@AGENTS.md

## Propre à Claude Code

- Les skills sont lus dans `.claude/skills`, lien symbolique vers
  `.agents/skills` : c'est là qu'on les écrit.
- L'entretien se lance par `/nouvelle-classe` ; les questions à l'enseignant
  passent par `AskUserQuestion`.
- **Ne pas mesurer un skill avec le banc d'essai du skill-creator** : il
  passe par un faux fichier de commande que cette version de Claude Code
  n'expose pas comme un skill, si bien qu'aucune demande ne déclenche jamais
  rien — il annonçait 10/20 là où `scripts/mesurer-declenchement.py` donne
  20/20.
