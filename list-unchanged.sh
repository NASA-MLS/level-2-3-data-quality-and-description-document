#! /bin/sh

# Identify the files that haven't changed since the v5-revb tag
comm -23 \
  <(git ls-tree -r --name-only v5-revb | sort) \
  <(git diff --name-only v5-revb | sort)
