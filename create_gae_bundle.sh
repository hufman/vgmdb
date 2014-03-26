#!/bin/bash
# Based off of CauliflowerVest's script
ROOT=$(dirname "$0")
BUNDLE_ROOT="$ROOT"/gae_bundle

[ -e "$BUNDLE_ROOT" ] && rm -rf "$BUNDLE_ROOT"
mkdir -p "$BUNDLE_ROOT"

copiedfiles="app.yaml wsgi.py vgmdb static"
for name in $copiedfiles; do
	ln -s ../"$name" "$BUNDLE_ROOT"/"$name"
done

function find_module() {
	python <<EOF
import imp
try:
  print imp.find_module('$1'.split('.')[0])[1]
except ImportError:
  pass
EOF
}

deps="bottle.py bs4 isodate jinja2 rdflib simplejson yaml amazonproduct concurrent"
for dep in $deps; do
	depdir=$(find_module $dep)
	[ -z "$depdir" ] && echo "Failed to find $dep" && continue
	ln -s "$depdir" "$BUNDLE_ROOT"/$dep
done

