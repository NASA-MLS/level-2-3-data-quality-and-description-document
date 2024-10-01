#! /bin/sh

for file in mls_h2o_v3-v4*.eps mls_rhi_v3-v4*.eps; do
    echo $file
    epstopdf $file
done
