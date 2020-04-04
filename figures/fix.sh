#! /bin/sh
convert -density 300 +antialias -background white -flatten \
	grid_maps_jfm2009_airsv6-mlsv2-3-4-5.pdf \
	grid_maps_jfm2009_airsv6-mlsv2-3-4-5-large.png
convert -resize 50% \
	grid_maps_jfm2009_airsv6-mlsv2-3-4-5-large.png \
	grid_maps_jfm2009_airsv6-mlsv2-3-4-5.png

convert -density 300 +antialias -background white -flatten \
	grid_maps_jja2009_airsv6-mlsv2-3-4-5.pdf \
	grid_maps_jja2009_airsv6-mlsv2-3-4-5-large.png
convert -resize 50% \
	grid_maps_jja2009_airsv6-mlsv2-3-4-5-large.png \
	grid_maps_jja2009_airsv6-mlsv2-3-4-5.png
rm *-large.png
