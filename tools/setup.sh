#!/usr/bin/env bash
# Download DL-Learner 1.5.0 into tools/ and create the Python venv.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d dllearner-1.5.0 ]; then
  curl -L -o dllearner.zip https://github.com/SmartDataAnalytics/DL-Learner/releases/download/1.5.0/dllearner-1.5.0.zip
  unzip -q dllearner.zip && rm dllearner.zip
fi
cd ..
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
