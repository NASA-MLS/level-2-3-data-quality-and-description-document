pro CheckBins

rootPrefix = 'MLS-Aura_L2MTX-Full_'
rootSuffix =  '_1996d051.h5'
paths = replicate ( $
  '/testing/emls/l2ak/v3QualDoc/ME-03/071a/outputs/', $
  2 )
bins = [ 'LAT0N', 'LAT70N' ]
binNames = bins
binTitles = [ 'Equator', '70!E0!NN' ]
noBins = n_elements ( bins )
phases = "CorePlusR3"
filenames = paths + rootPrefix + phases + bins + rootSuffix

l2pcs = list ()
for f = 0, n_elements ( filenames ) - 1 do begin
  l2pcs.add, ReadHDF5L2PCFile ( filename=filenames[f], /noBlocks )
endfor

SetPS, /landscape
device, /helvetica
plotprofile, l2pcs[0].col.vec.o3_hr, title="Ozone profiles from L2PC files"
plotprofile, l2pcs[1].col.vec.o3_hr, /linestyle,/overplot

xyouts, 2, 1e-2, strjoin ( ['Solid: ', 'Dashed: ' ] + filenames, '!C' ), charsize=0.8

device, /close


end
