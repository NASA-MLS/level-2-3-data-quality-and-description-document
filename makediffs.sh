#! /bin/sh
latexpand --keep-comments v4-x-report.tex > expanded.tex
latexdiff previous-version.tex expanded.tex | tee diffs.tex
pdflatex diffs.tex
