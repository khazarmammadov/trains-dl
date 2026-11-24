#!/usr/bin/env bash
# Build the Moodle archive: report + code + ontologies + DL-Learner .conf files.
# Usage: ./make_submission.sh [group-name]
set -euo pipefail
cd "$(dirname "$0")"
NAME="${1:-trains-concept-induction}"
OUT="submission/$NAME"
rm -rf submission && mkdir -p "$OUT"
cp -R README.md requirements.txt make_submission.sh src ontology conf data tools "$OUT"/
rm -rf "$OUT/tools/dllearner-1.5.0" "$OUT"/src/__pycache__
mkdir -p "$OUT/results"
cp results/*.csv results/*.md results/*.png results/*.txt "$OUT/results/" 2>/dev/null || true
mkdir -p "$OUT/report"
cp report/*.pdf "$OUT/report/" 2>/dev/null || cp report/*.md "$OUT/report/"
(cd submission && zip -qr "$NAME.zip" "$NAME")
echo "created submission/$NAME.zip ($(du -h "submission/$NAME.zip" | cut -f1))"
