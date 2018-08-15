
;type = 'NMAT'
;type = 'SST'
;type = 'STDEV'
type = 'OSTIA_STDEV'
;type = 'MATSTDEV'

f=ppa('/project/hadobs1/OBS/marine/HadSST2/norms/HadSST2_pn1d6190.pp',/all)

if type eq 'NMAT' then begin
   g=ppa('/project/hadobs1/OBS/marine/MOHMAT/norms/MOHMATN4_pn1dg6190.pp',/all)
   g.lbcode = 2   
   g=pp_conform(g,f[0])
   f=g
endif

if type eq 'STDEV' then begin
   g = ppa('/net/project/hadobs1/OBS/marine/MOHSST/norms/MOHSST6_sd_pen6190.pp',/all)
   g.lbcode = 2   
   g=pp_conform(g,f[0])
   f=g
endif

if type eq 'OSTIA_STDEV' then begin
   g = ppa('OSTIA_pentad_stdev_climatology.pp', 0) ;/all)
   g.lbcode = 2   
   g=pp_conform(g,f[0])
   f=g
   for i =0,n_elements(f)-1 do begin
      f[i].data[where(f[i].data lt -10)] = -1e30
   endfor
endif

n=n_elements(f)
data = fltarr(360,180,n)
for i = 0,n-1 do data(*,*,i) = f(i).data(*,*)


;start_julian = juldat((Month, Day, Year, Hour, Minute, Second) 
    start_julian = JULDAY(1, 1, 1850, 0, 0, 0) 
    fjulian = JULDAY(f(*).lbmon, f(*).lbdat, 1961, 0, 0, 0)-start_julian
    ljulian = JULDAY(f(*).lbmond, f(*).lbdatd, 1961, 23, 59, 59)-start_julian

if type eq 'SST' then id = NCDF_CREATE('HadSST2_pentad_climatology.nc',/clobber)
if type eq 'NMAT' then id = NCDF_CREATE('HadNMAT2_pentad_climatology.nc',/clobber)
if type eq 'STDEV' then id = NCDF_CREATE('HadSST2_pentad_stdev_climatology.nc',/clobber)
if type eq 'OSTIA_STDEV' then id = NCDF_CREATE('OSTIA_pentad_stdev_climatology.nc',/clobber)

NCDF_CONTROL, id, /FILL

;Define dimensions of problem
    zid   = NCDF_DIMDEF(id, 'time', /UNLIMITED)
    latid = NCDF_DIMDEF(id, 'latitude', 180)
    lonid = NCDF_DIMDEF(id, 'longitude', 360)
    nvid  = NCDF_DIMDEF(id, 'nv', 2)

    if type eq 'SST'  then tempvid = NCDF_VARDEF(id, 'sst', [lonid,latid,zid], /FLOAT)
    if type eq 'NMAT' then tempvid = NCDF_VARDEF(id, 'nmat', [lonid,latid,zid], /FLOAT)
    if type eq 'STDEV' then tempvid = NCDF_VARDEF(id, 'sst', [lonid,latid,zid], /FLOAT)
    if type eq 'OSTIA_STDEV' then tempvid = NCDF_VARDEF(id, 'sst', [lonid,latid,zid], /FLOAT)

;Define variables
    hid           = NCDF_VARDEF(id, 'time',         [zid],             /FLOAT)
    time_bnds_vid = NCDF_VARDEF(id, 'time_bnds',    [nvid,zid],        /FLOAT)
    latvid        = NCDF_VARDEF(id, 'latitude',     [latid],           /FLOAT)
    lonvid        = NCDF_VARDEF(id, 'longitude',    [lonid],           /FLOAT)
    
if type eq 'SST' or type eq 'STDEV' or type eq 'OSTIA_STDEV' then begin
    NCDF_ATTPUT, id, tempvid, '_FillValue', -1.e+30
    NCDF_ATTPUT, id, tempvid, 'standard_name', 'sea_surface_temperature'
    NCDF_ATTPUT, id, tempvid, 'long_name', 'SST'
    NCDF_ATTPUT, id, tempvid, 'units', 'K'
    NCDF_ATTPUT, id, tempvid, 'cell_methods', 'time: lat: lon: mean'
    NCDF_ATTPUT, id, tempvid, 'missing_value', -1.e+30
endif else if type eq 'NMAT' then begin
    NCDF_ATTPUT, id, tempvid, '_FillValue', -1.e+30
    NCDF_ATTPUT, id, tempvid, 'standard_name', 'night marine_air_temperature'
    NCDF_ATTPUT, id, tempvid, 'long_name', 'NMAT'
    NCDF_ATTPUT, id, tempvid, 'units', 'K'
    NCDF_ATTPUT, id, tempvid, 'cell_methods', 'time: lat: lon: mean'
    NCDF_ATTPUT, id, tempvid, 'missing_value', -1.e+30
endif

;define time attributes
    NCDF_ATTPUT, id, hid, 'units', 'days since 1850-1-1 0:0:0'
    NCDF_ATTPUT, id, hid, 'calendar', 'gregorian'
    NCDF_ATTPUT, id, hid, 'long_name', 'Time'
    NCDF_ATTPUT, id, hid, 'standard_name', 'time'
    
;define latitude attributes
    NCDF_ATTPUT, id, latvid, 'units', 'degrees_north'
    NCDF_ATTPUT, id, latvid, 'long_name', 'Latitude'
    NCDF_ATTPUT, id, latvid, 'standard_name', 'latitude'
    
    
;define latitude attributes
    NCDF_ATTPUT, id, lonvid, 'units', 'degrees_east'
    NCDF_ATTPUT, id, lonvid, 'long_name', 'Longitude'
    NCDF_ATTPUT, id, lonvid, 'standard_name', 'longitude'

;define global attributes
       NCDF_ATTPUT, id, /GLOBAL, 'Title', 'Petnad 1 degree climatology'
       NCDF_ATTPUT, id, /GLOBAL, 'source', 'Based on ICOADS 2.1'
       NCDF_ATTPUT, id, /GLOBAL, 'Conventions', 'CF-1.0'
       NCDF_ATTPUT, id, /GLOBAL, 'history', ' converted to netcdf'
       if type eq 'SST'  then NCDF_ATTPUT, id, /GLOBAL, 'supplementary_information', 'HadSST2 climatology'
       if type eq 'NMAT' then NCDF_ATTPUT, id, /GLOBAL, 'supplementary_information', 'HadNMAT2 climatology'
       if type eq 'STDEV' then NCDF_ATTPUT, id, /GLOBAL, 'supplementary_information', 'HadSST2 standard deviation climatology'
       if type eq 'OSTIA_STDEV' then NCDF_ATTPUT, id, /GLOBAL, 'supplementary_information', 'OSTIA-based standard deviation climatology'

;Finished definitions
    NCDF_CONTROL, id, /ENDEF


    NCDF_VARPUT, id, hid, (fjulian+ljulian)/2.
    
    FOR I=0,n-1 DO NCDF_VARPUT, id, time_bnds_vid, fjulian(i), OFFSET=[0,I]
    FOR I=0,n-1 DO NCDF_VARPUT, id, time_bnds_vid, ljulian(i), OFFSET=[1,I]
    
    NCDF_VARPUT, id, latvid, (1+findgen(180))*f(0).bdy + f(0).bzy
    NCDF_VARPUT, id, lonvid, (1+findgen(360))*f(0).bdx + f(0).bzx
    
    FOR i=0,n-1 DO BEGIN
       FOR XX=0,359 DO BEGIN
          FOR YY=0,179 DO BEGIN
             NCDF_VARPUT, id, tempvid, REFORM(data(XX,YY,i)), OFFSET=[XX,YY,i]
          ENDFOR
       ENDFOR
    ENDFOR
    
    NCDF_CLOSE,id
    

end
