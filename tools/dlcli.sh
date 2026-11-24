#!/usr/bin/env bash
# Wrapper around DL-Learner 1.5.0 CLI that works on Java 17+ (module access flags).
# Usage: tools/dlcli.sh path/to/file.conf
HERE="$(cd "$(dirname "$0")" && pwd)"
export JAVA_OPTS="--add-opens java.base/java.lang.invoke=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED ${JAVA_OPTS:-}"
exec "$HERE/dllearner-1.5.0/bin/cli" "$@"
