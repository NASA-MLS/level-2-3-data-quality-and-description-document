#! /bin/sh
for file in *grid_*.pdf; do
    echo $file
    convert -density 200 +antialias $file ${file%.*}-large.png
    convert -resize 50% -antialias ${file%.*}-large.png ${file%.*}.png
    rm ${file%.*}-large.png
done
    
