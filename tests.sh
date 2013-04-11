#!/bin/sh
dir=`dirname $0`
oldpwd="$PWD"
cd "$dir"
for i in tests/*.py; do
	testname=`basename $i .py`
	echo "$testname" | grep "^_" > /dev/null && continue
	echo "Running tests in $testname"
	python -m unittest tests.$testname
	echo
done
cd "$oldpwd"
