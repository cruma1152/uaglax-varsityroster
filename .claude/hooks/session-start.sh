#!/bin/bash
# SessionStart hook for the UAGLAX Varsity Roster site.
#
# This is a static HTML/CSS/JS PWA — there is no package manager manifest,
# test suite, or linter to bootstrap. The one build-time dependency is
# Pillow, used by "Lacrosse Roster/icons/_build_icons.py" to regenerate the
# PWA icons/favicons from the source screenshot. We install it so that
# script is runnable in a fresh web session.
set -euo pipefail

# Only do work in Claude Code on the web; a no-op locally.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "[session-start] Installing Pillow (icon build dependency)..."
pip3 install --quiet --disable-pip-version-check Pillow

echo "[session-start] Done."
