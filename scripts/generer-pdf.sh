#!/usr/bin/env bash
# Génère tous les PDF du site dans <dossier-site>/pdf/ :
#  - un PDF par document, aux dates de la zone de la classe (classe.yml,
#    `calendrier.zone`), via la vue imprimer.html, et ses extraits par période
#  - un PDF par cahier du matériel et par période qui l'a (classe.yml,
#    `materiel` : entraînement, évaluation, imagier, cartes-corpus)
# Usage : scripts/generer-pdf.sh <dossier-site-assemblé>
# Variables : CHROME_BIN (défaut : google-chrome, ou le Chromium de Playwright), PORT (défaut : 8931)
# Ensuite : python3 scripts/verifier-pagination.py <dossier-site-assemblé>
set -euo pipefail

SITE_DIR=${1:?"dossier du site assemblé requis"}
# google-chrome sur le runner GitHub ; dans une session Claude Code, le Chromium
# de Playwright (/opt/pw-browsers) s'il est là.
if [ -z "${CHROME_BIN:-}" ]; then
  CHROME_BIN=$(command -v google-chrome || ls /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 || true)
fi
CHROME_BIN=${CHROME_BIN:-google-chrome}
PORT=${PORT:-8931}
OUT="$SITE_DIR/pdf"

python3 -m http.server "$PORT" --directory "$SITE_DIR" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1

imprime() { # imprime <url> <fichier-pdf> [budget-temps-ms]
  "$CHROME_BIN" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --no-pdf-header-footer --virtual-time-budget="${3:-10000}" \
    --print-to-pdf="$2" "$1" 2>/dev/null
  [ -s "$2" ] || { echo "ÉCHEC : $2" >&2; exit 1; }
}

# Les documents et la zone viennent de la classe (classe.yml, via site/classe.json).
classe() { python3 -c "import json,sys; c=json.load(open('$SITE_DIR/classe.json')); print(' '.join($1))"; }
DOCS=$(classe "d['id'] for d in c['documents'] if d.get('md')")
PROGRESSIONS=$(classe "d['id'] for d in c['documents'] if d.get('par_periode')")
ZONE=$(classe "[c['calendrier']['zone']]")
PERIODES=$(classe "str(i + 1) for i in range(len(c['periodes']))")
mkdir -p "$OUT"
NDOCS=0
for D in $DOCS; do
  imprime "http://127.0.0.1:$PORT/imprimer.html?doc=$D" "$OUT/$D.pdf"
  NDOCS=$((NDOCS + 1))
done
# Extraits par période des progressions, pour l'affichage en classe
for D in $PROGRESSIONS; do
  for N in $PERIODES; do
    imprime "http://127.0.0.1:$PORT/imprimer.html?doc=$D&periode=$N" "$OUT/$D-periode-$N.pdf"
    NDOCS=$((NDOCS + 1))
  done
done
echo "Documents (zone $ZONE) : $NDOCS PDF"

# Les cahiers : ceux que déclare le matériel, période par période. L'imagier
# et les cartes-corpus, lourds en photographies, laissent plus de temps au
# rendu avant l'impression (le budget vient de scripts/classe.py).
CAHIERS=$(classe "'%s|%s|%s|%s' % (m['cle'], m['source'].replace('{n}', str(n)), m['pdf'].replace('{n}', str(n)), m['budget']) for m in c['materiel'] if 'source' in m for n in m['periodes']")
for C in $CAHIERS; do
  IFS='|' read -r CLE SRC PDF BUDGET <<< "$C"
  imprime "http://127.0.0.1:$PORT/$SRC" "$SITE_DIR/$PDF" "$BUDGET"
done
python3 -c "import json,collections; c=json.load(open('$SITE_DIR/classe.json')); n=collections.Counter(m['titre'] for m in c['materiel'] for _ in m.get('periodes', [])); print('Cahiers : ' + (', '.join('%s %d PDF' % kv for kv in n.items()) or 'aucun'))"
echo "Total : $(find "$OUT" -name '*.pdf' | wc -l) PDF générés dans $OUT"
