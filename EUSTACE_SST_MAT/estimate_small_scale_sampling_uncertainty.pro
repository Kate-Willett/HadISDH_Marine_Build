@gridder_subs.pro

out_dir = '/data/cr2/hadjj/HadSST.3.2.0.0/auxiliary_fields/'


month_lengths = [31,28,31,30,31,30,31,31,30,31,30,31]

g = makeppfield(fltarr(360,180,20))
g.bzx = -180.5
g.bdx = 1.0
g.bzy = -90.5
g.bdy = 1.0

ak = g
qk = g
k = g

restore_colors,'spectrum'

;read in data for one one by one 5 day window
for year = 2014,2012,-1 do begin
   for pentad = 0,72 do begin
      
      spawn,'> $LOCALDATA/UKMO-L4LRfnd-GLOB-v01-fv02-OSTIAanom_TMP.pp'
  
;get all days for this pentad and write to pp    
      for month = 1,12 do begin
         for day = 1,month_lengths[month-1] do begin
      
            if which_pentad(year,month,day) eq pentad then begin
               
               print,year,pentad,month,day

               ystr = string(year,  format='(i4.4)')
               mstr = string(month, format='(i2.2)')
               dstr = string(day,   format='(i2.2)')
               
               dir = '/project/ofrd/ostia/data/netcdf/'+ystr+'/'+mstr+'/'
               file = dir+ystr+mstr+dstr+'120000-UKMO-L4_GHRSST-SSTfnd-OSTIA-GLOB-v02.0-fv02.0.nc'
               
               h = ncassoc(file, /quiet)
               sst = ppa(h, /all)
               sst = sst(where(sst.title eq 'sea_surface_foundation_temperature'))
               sst.bmdi = min(sst(0).data)
               
               ppw,sst,'$LOCALDATA/UKMO-L4LRfnd-GLOB-v01-fv02-OSTIAanom_TMP.pp',/append
               
            endif
            
         endfor
      endfor
      
      sst = 'a'
      
      
      nreals = 10
      restore_colors,'spectrum'

      f = ppa('$LOCALDATA/UKMO-L4LRfnd-GLOB-v01-fv02-OSTIAanom_TMP.pp',/all)
      

      for xx = 0L,359 do begin
         print,xx
         for yy = 0L,179 do begin
            
            hold = f[*].data[xx*20:xx*20+19,yy*20:yy*20+19]
            ind = where(hold ne f[0].bmdi,ct)
            
            if ct gt 0 then begin
               
               fullav = avg(hold[ind])
               for n =1,ct,10 do begin
                  if (n-1)/10 lt 20 then begin
                     for real = 0,nreals-1 do begin
                        noise = randomn(seed,ct)
                        order = sort(noise)
                        Result = hold[ind[order[0:n-1]]]
                        
                        xk = (avg(result) - fullav)
                        k[(n-1)/10].data[xx,yy] = k[(n-1)/10].data[xx,yy] + 1
                        qk[(n-1)/10].data[xx,yy] = qk[(n-1)/10].data[xx,yy] + $
                                                   ((k[(n-1)/10].data[xx,yy]-1)/k[(n-1)/10].data[xx,yy]) * (xk-ak[(n-1)/10].data[xx,yy])^2
                        ak[(n-1)/10].data[xx,yy] = ak[(n-1)/10].data[xx,yy] + (xk-ak[(n-1)/10].data[xx,yy])/k[(n-1)/10].data[xx,yy]
                        
                     endfor
                  endif
               endfor

            endif
            
            
         endfor 
      endfor 

      g = pp_ff('sqrt(a/(b-1))',qk,k,/quiet,/math_fix)
      !p.multi=[0,3,4,0,0]
      pp_contour,g[indgen(12)*10],/block,bstyle=style(/interp),levels=findgen(21)/20

   endfor 
endfor   

g = pp_ff('sqrt(a/(b-1))',qk,k,/quiet,/math_fix)
pp_contour,g[0],/block,bstyle=style(/interp),levels=findgen(21)/20

ppw,g[0],out_dir+'/OSTIA_small_scale_sampling_uncertainty.pp'

end
