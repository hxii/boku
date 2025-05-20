#!/bin/bash
staged_files=$(git diff --name-only --staged)

issues_found=false

for file in $staged_files; do
	output=$(git diff --staged "$file" | grep -nE ".*TODO:\s*.+$")

	if [[ -n "$output" ]]; then
		echo "ERROR: 'TODO:' found in $file:"
		echo "$output"
		issues_found=true
	fi
done

if $issues_found; then
	exit 1
else
	exit 0
fi
