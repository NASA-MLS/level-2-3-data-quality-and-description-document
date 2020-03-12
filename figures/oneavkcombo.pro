pro OneAVKCombo, product=product, all=all, $
  noHorizontal=noHorizontal, bonus=bonus

if keyword_set ( all ) then begin
  mainProducts = [  'CH3Cl', 'CH3CN', 'CH3OH', 'ClO', 'CO', 'GPH', 'H2O_HR', 'HCl', $
    'HCN', 'HNO3', 'IWC', 'N2O', 'O3_HR', 'OH', 'SO2', 'Temperature_HR' ]
  bonusProducts = [ 'O3_HR' ]
  noHorizProducts = [ 'BrO', 'HO2', 'HOCl' ]
  ;; for p = 0, n_elements ( mainProducts ) - 1 do OneAvkCombo, product=mainProducts(p)
  for p = 0, n_elements ( bonusProducts ) - 1 do OneAvkCombo, product=bonusProducts(p), /bonus
  ;; for p = 0, n_elements ( noHorizProducts ) - 1 do OneAvkCombo, product=noHorizProducts(p), /noHorizontal
  return
endif

fmt = '($,a)'
outSuffix = ''

;; Read the range table
oneRangeEntry = { product:'', range:fltarr(2)}
openr, unit, 'range-table.txt', /get_lun
while not eof ( unit ) do begin
  line = ''
  readf, unit, line, format='(a)'
  words = strsplit ( line, /extract )
  oneRangeEntry.product = strupcase ( words[0] )
  oneRangeEntry.range = float ( words[1:2] )
  if n_elements ( ranges ) eq 0 then begin
    ranges = oneRangeEntry
  endif else begin
    ranges = [ ranges, oneRangeEntry ]
  endelse
endwhile
free_lun, unit

;; Decide which phases to raid, bail out if none applicable.
print, 'Doing avk for: ' + product
phases = ''
case product of
  ;; Standard products
  'BrO'   : phases = 'CorePlusR4AB14'
  'CH3Cl' : phases = 'CorePlusR4AB14'
  'CH3CN' : phases = 'CorePlusR4AB14'
  'CH3OH' : phases = 'Methanol'
  'ClO'   : phases = 'CorePlusR4AB14'
  'CO'    : phases = 'CorePlusR3'
  'GPH'   : phases = ''
  'H2O_HR': phases = 'CorePlusR2'
  'HCl'   : phases = 'CorePlusR4AB14'
  'HCN'   : phases = 'CorePlusR2'
  'HNO3'  : phases = [ 'CorePlusR3', 'CorePlusR2' ]
  'HO2'   : phases = 'CorePlusR4AB14'
  'HOCl'  : phases = 'CorePlusR4AB14'
  'IWC'   : phases = '' 
  'N2O'   : phases = 'NitrousOxide'
  'O3_HR' : phases = 'OzoneOnly'
  'OH'    : phases = 'CorePlusR5'
  'SO2'   : phases = 'CorePlusR3'
  'Temperature_HR' : phases = 'CorePlusR3'
  ;; Diagnostic products
  'CH3CN-640' : phases = 'CorePlusR4AB14'
  'ClO-190' : phases = 'CorePlusR2'
  'HNO3-190' : phases = 'CorePlusR2'
  'HNO3-240' : phases = 'CorePlusR3'
  'HNO3-640' : phases = 'CorePlusR4AB14'
  'N2O-190' : phases = 'CorePlusR2'
  'N2O-640' : phases = 'CorePlusR4B'
  'O3-190' : phases = 'CorePlusR2'
  'O3-640' : phases = 'CorePlusR4AB14'
  'O3-2T5' : phases = 'CorePlusR5'
  'Temperature-Core' : phases = 'UpdatePtan'
  'Temperature-CorePlusR2' : phases = 'CorePlusR2'
  'Temperature-CorePlusR2' : phases = 'CorePlusR2'
  'Temperature-CorePlusR3'  : phases = 'CorePlusR3'
  'Temperature-CorePlusR4AB14' : phases = 'CorePlusR4AB14'
  'Temperature-CorePlusR4B' : phases = 'CorePlusR4B'
  'Temperature-CorePlusR5'  : phases = 'CorePlusR5'
endcase
if phases(0) eq '' then return
noPhases = n_elements(phases)

if product ne 'OH' then begin
  rootPrefix = 'MLS-Aura_L2MTX-Full_v05-00-'
  rootSuffix = [ $
    'S103a_1996d051.h5', $
    'S103b_1996d051.h5' ]
  paths = [ $
    '/testing/workspace/pwagner/l2tests/avgkrnls/v5.00/SA-103a/103a/', $
    '/testing/workspace/pwagner/l2tests/avgkrnls/v5.00/SA-103b/103b/' ]
  bins = [ 'LAT0N', 'LAT70N' ]
  binNames = bins
  binTitles = [ 'Equator', '70!E0!NN' ]
  noBins = n_elements ( bins )
endif else begin
  paths = [ $
    '/testing/workspace/pwagner/l2tests/avgkrnls/v5.00/SA-103a/103a/', $
    '/testing/workspace/pwagner/l2tests/avgkrnls/v5.00/SA-103n/103n/' ]
  rootPrefix = 'MLS-Aura_L2MTX-Full_v05-00-'
  rootSuffix =  'S103' + [ 'a', 'n' ] + '_1996d051.h5'
  bins = [ 'LAT0N', 'LAT0N' ]
  binTitles = [ 'Day', 'Night' ]
  binNames = binTitles
  noBins = n_elements ( bins )
endelse

bottom = 1000.0
top = 0.001

if keyword_set ( bonus ) then begin
  if product eq 'O3_HR' then outSuffix = '-UTLS'
endif

;; Setup the plot
outName = 'avk-' + product + outSuffix
SetPS, filename=outName + '.eps', /encapsulated, /color
device, xsize=16, ySize=18 - 8 * keyword_set ( noHorizontal )
!p.charsize=0.8

InitColorBoss
col = GetStandardPalette ( /paper, /set, /lightGrey )
colorRange = AllocateRange ( 100 )
LoadCtToRange, 34, colorRange

if keyword_set ( noHorizontal ) then begin
  Array_NewDivision, nx=2, ny=1, $
    xRatio=[1,1], yRatio=[1], $
    xMarginRatio=[0.25,0.05,0.05], $
    yMarginRatio=[0.18,0.14], $
    /byPosition, /reset
endif else begin
  Array_NewDivision, nx=2, ny=2, $
    xRatio=[1,1], yRatio=[1,1], $
    xMarginRatio=[0.3,0.1,0.05], $
    yMarginRatio=[0.18,0.25,0.14], $
    /byPosition, /reset
endelse

for bin = 0, noBins - 1 do begin
  for phase = 0, noPhases - 1 do begin 
    words = strsplit ( product, '-', /extract )
    name = words(0)
    filename = paths [ bin ] + $
      rootPrefix + rootSuffix [ bin ]
    print, '---- ' + filename
    print, format=fmt, '  Reading phase ' + strupcase ( phases[phase] ) + ', A'
    A = ReadHDF5L2PCFile ( filename=filename, $
      matrixName='AVK' + strupcase ( phases[phase] ), $
      singleRowQuantity=name, singleColQuantity=name )
    print, format=fmt, ',S'
    S = ReadHDF5L2PCFile ( filename=filename, $
      matrixName='SOUT' + strupcase ( phases[phase] ), $
      singleRowQuantity=name, singleColQuantity=name )
    print, format=fmt, '; compressing A'
    A = CompressMatrix ( A )
    print, format=fmt, ', S'
    S = CompressMatrix ( S )

    precision = GetPrecisionFromDiagonal ( S )
    DestroyMatrix, S
    FindQty, a.col, name=name, qty=qty
    profile = a.col.vec.(qty).noProfs / 2 
    precision = ExtractProfiles ( precision.(qty), profile )
    ;; print, filename, precision.lat[0], precision.geodAngle[0]
    ;; Work out what range we're showing
    yRange = [ 0 ]
    strictRange = 0
    case product of
      ;; Standard products
      'BrO' : heightRange = [ 10, 0.1 ]
      'CH3Cl' : heightRange = [ 1000.0, 0.1 ]
      'CH3CN' : heightRange = [ 1000.0, 0.1 ]
      'CH3OH' : heightRange = [ 1000.0, 0.1 ]
      'ClO' : heightRange = [ 1000.0, 0.01 ]
      'CO' : heightRange = [ 1000, 0.001 ]
      'H2O_HR' : heightRange = [ 1000, 0.1 ]
      'HCl' : heightRange = [ 200, 0.1 ]
      'HCN' : heightRange = [ 100, 0.1 ]
      'HNO3' : begin
        yRange = [ 1000, 0.1 ]
        if phases[phase] eq 'CorePlusR3' then heightRange = [ 1000, 22.0 ]
        if phases[phase] eq 'CorePlusR2' then heightRange = [ 14.7, 0.1 ]
        strictRange = 1
      end
      'HO2' : heightRange = [ 100, 0.1 ]
      'HOCl' : heightRange = [ 100, 1.0 ]
      'N2O' : begin
        heightRange = [ 100, 0.15 ]
        yRange = [ 100, 0.1]
      end
      'N2O-640' : begin
        heightRange = [ 100, 0.15 ]
        yRange = [ 100, 0.1]
      end
      'O3_HR' : begin
        if keyword_set ( bonus ) then begin
          heightRange = [ 1000.0, 10.0 ]
          
        endif else begin
          heightRange = [ 1000, 0.001 ]
        endelse
      end
      'OH' : heightRange = [ 100, 0.001 ]
      'SO2' : heightRange = [ 1000, 1.0 ]
      'Temperature_HR' : heightRange = [ 1000.0, 0.001 ]
      ;; Diagnostic products
      'CH3CN-640' : heightRange = [ 1000.0, 1.0 ]
      'ClO-190' : heightRange = [ 100, 1.0 ]
      'HNO3-190' : heightRange = [ 100, 0.001 ]
      'HNO3-240' : heightRange = [ 1000, 1.0 ]
      'HNO3-640' : heightRange = [ 1000, 1.0 ]
      'N2O-190' : heightRange = [ 100, 0.1 ]
      'O3-190' : heightRange = [ 1000, 0.01 ]
      'O3-640' : heightRange = [ 1000, 0.01 ]
      'O3-2T5' : heightRange = [ 1000, 0.01 ]
      'Temperature_HR-Core' : heightRange = [ 1000, 0.001 ]
      'Temperature_HR-CorePlusR2' : heightRange = [ 1000, 0.001 ]
      'Temperature_HR-CorePlusR2' : heightRange = [ 1000, 0.001 ]
      'Temperature_HR-CorePlusR3'  : heightRange = [ 1000, 0.001 ]
      'Temperature_HR-CorePlusR4AB14' : heightRange = [ 1000, 0.001 ]
      'Temperature_HR-CorePlusR4B' : heightRange = [ 1000, 0.001 ]
      'Temperature_HR-CorePlusR5'  : heightRange = [ 1000, 0.001 ]
      else : MyMessage, /error, 'Unknown species ' + product
    endcase
    if n_elements(yRange) eq 1 then yRange = heightRange

    ;; -------------------------------- Vertical kernel
    ;; Possibly 'return' to this plot
    if phase ne 0 then SelectDisplay, vertical
    print, format=fmt, '; V'
    avkV = CollapseMatrix ( A )
    if keyword_set ( noHorizontal ) and bin eq 1 then begin
      yTitle = ''
      yTickFormat = 'NothingFormat'
    endif else begin
      yTitle = 'Pressure / hPa'
      yTickFormat = ''
    endelse

    ShowVerticalAVK, avkV, $
      quantity=name, profile=profile, $
      overplot=phase gt 0, $
      colorRange=colorRange, $
      yRange=yRange, $
      xRange=[-0.2,1.2], $
      firstSurf=heightRange(0), $
      lastSurf=heightRange(1), $
      /noErase, /fullColorRange, $
      yTitle=yTitle, yTickFormat=yTickFormat, $
      vertRes=vertRes, strictRange=strictRange
    DestroyMatrix, avkV
    vertical = RecordDisplay()
    
    ;; Put up a label
    BoxedXYOUTs, /normal, $
      !p.position(0)-0.04+0.08*keyword_set(noHorizontal), $
      !p.position(3)+0.03+0.03*keyword_set(noHorizontal), $
      binTitles(bin), background=col.lightGrey, charsize=1.2, align=0.5, $
      fraction=1.0 + (1-bin)*0.2

    ;; -------------------------------- Horizontal kernel
    ;; Either move or return to this plot
    if not keyword_set ( noHorizontal ) then begin
      if phase eq 0 then begin
        Array_NextDivision
      endif else begin
        SelectDisplay, horizontal
      endelse
      print, format=fmt, '; H'
      avkH = VerticallyCollapseMatrix ( A )
      ShowHorizontalAVK, avkH, $
        quantity=name, keyProf=profile, $
        overplot=phase gt 0, $
        colorRange=colorRange, $
        yRange=yRange, $
        xRange=[-4,4], $
        /noErase, $
        yTitle='', $
        yTickFormat='NothingFormat' , $
        firstSurf=heightRange(0), $
        lastSurf=heightRange(1), $
        horizRes=horizRes, $
        strictRange=strictRange
      horizontal = RecordDisplay()
      DestroyMatrix, avkH
    endif
    if phase eq noPhases - 1 then begin
      Array_NextDivision
    endif
    
    ;; Clean up
    DestroyMatrix, A

    print, format=fmt, '; table'
    ;; Write out the resolution summaries
    openw, unit, outName + '-' +binNames[bin] + '-' + phases[phase] + '.txt', /get_lun
    printf, unit, 'Averaging kernel etc. information for: ' + product
    prodWords = strsplit ( product, '-_', /extract )
    prodPrefix = strupcase ( prodWords[0] )
    rangeEntry = FindFirst ( ranges.product eq prodPrefix )
    if rangeEntry ne -1 then begin
      r = ranges [ rangeEntry ]
      altRange = 16.0*(3.0-alog10(r.range))
      printf, unit, 'Useful range: ' + $
        GetNicePres ( r.range[0] ) + ' hPa to ' + $
        GetNicePres ( r.range[1] ) + ' hPa (' + $
        string ( altRange[0], format='(f0.1)' ) + ' to ' + $
        string ( altRange[1], format='(f0.1)' ) + ' km)'

      surfRange = FindSurf ( vertRes, r.range )
      mean = total ( vertRes.val [ 0, surfRange[0]:surfRange[1] ] ) / $
        ( surfRange[1] - surfRange[0] + 1 )
      mn = min ( vertRes.val [ 0, surfRange[0]:surfRange[1] ], max=mx )
      printf, unit, 'Mean vertical resln. over this range: ' + $
        string ( mean, format='(f0.1)' ) + ' km, (' + $
        string ( mn, format='(f0.1)' ) + ' -- ' + $
        string ( mx, format='(f0.1)' ) + ' km)'
    endif
    line = '      p/hPa  ' + string ( 'prec./' + precision.units, format='(a-12)' ) + $
      '  VR/km'
    if n_elements ( horizRes ) ne 0 then line = line + '     HR/km'
    printf, unit, line
    for h = 0, vertRes.noSurfs - 1 do begin
      line = $
        string ( vertRes.surfs[h], format='(f11.5)' ) + $
        '  ' + $
        string ( precision.qual[0,h]/precision.scale, format='(g10.4)' ) + $
        '  ' + $
        string ( vertRes.val[0,h], format='(f7.2)' )
      if n_elements ( horizRes ) ne 0 then line = line + $
        ' ' + $
        string ( horizRes.val[0,h]*165.0, format='(f9.2)' )
      printf, unit, line
    endfor
    free_lun, unit
    print, ', done.'
  endfor
endfor

!p.charsize=1.0
device, /close
spawn, 'epstopdf ' + outName + '.eps'

end
