#!/usr/local/sci/bin/python2.7
'''
make_and_qc_db.py invoked by typing::

  python2.7 make_and_qc_db.py -i configuration.txt --year1 1850 --year2 1855

This builds a database for the chosen years. The location 
of the data base, the locations of the climatology files are 
all to be specified in the configuration files.
'''

import gzip
from netCDF4 import Dataset
import qc
import qc_new_track_check as tc
import qc_buddy_check as bc
import spherical_geometry as sph
from IMMA2 import IMMA
import Extended_IMMA as ex
import sys, getopt
import time

def base_qc_report(rep):
    '''
    Take a marine report and do some base qc on it.
    '''
#Basic positional QC
    rep.set_qc('POS', 'pos', 
                qc.position_check(rep.getvar('LAT'), 
                                  rep.getvar('LON')))
    
    rep.set_qc('POS', 'date', 
                qc.date_check(rep.getvar('YR'), rep.getvar('MO'),
                              rep.getvar('DY'), rep.getvar('HR')))
    
    if (rep.get_qc('POS', 'pos') == 0 and 
        rep.get_qc('POS', 'date') == 0):
        rep.set_qc('POS', 'day', 
                   qc.day_test(rep.getvar('YR'),
                               rep.getvar('MO'),
                               rep.getvar('DY'),
                               rep.getvar('HR'),
                               rep.getvar('LAT'),
                               rep.getvar('LON')))
    else:
        rep.set_qc('POS', 'day', 1)

    rep.set_qc('POS', 'blklst', 
                qc.blacklist(rep.getvar('ID'),
                             rep.getvar('DCK'), 
                             rep.getvar('YR'), 
                             rep.getvar('LAT'), 
                             rep.getvar('LON')))

#SST base QC
    rep.set_qc('SST', 'noval', qc.value_check(rep.getvar('SST')))
    rep.set_qc('SST', 'freez', 
               qc.sst_freeze_check(rep.getvar('SST'), 0.0))
    rep.set_qc('SST', 'clim', 
               qc.climatology_check(rep.getvar('SST'), rep.getnorm('SST'), 8.0))
    rep.set_qc('SST', 'nonorm', qc.no_normal_check(rep.getnorm('SST')))

#MAT base QC
    rep.set_qc('AT', 'noval', qc.value_check(rep.getvar('AT')))
    rep.set_qc('AT', 'clim', 
               qc.climatology_check(rep.getvar('AT'), rep.getnorm('AT'), 10.0))
    rep.set_qc('AT', 'nonorm', qc.no_normal_check(rep.getnorm('AT')))

    return rep

def process_bad_id_file(bad_id_file):
    '''
    Read in each entry in the bad id file and if it is shorter than 9 characters 
    pad with white space at the end of the string
    '''
    idfile = open(bad_id_file, 'r')
    ids_to_exclude = []
    for line in idfile:
        line = line.rstrip()
        while len(line) < 9:
            line = line+' '
        if line != '         ':
            ids_to_exclude.append(line)
    idfile.close()
    return ids_to_exclude

def split_generic_callsign(invoyage):
    '''
    Prototype function to identify when a callsign is being used by multiple ships 
    and to split the observations into pseudo IDs that each represents a different ship
    
    :param invoyage: a voyage object containing marine reports
    :type invoyage: Voyage
    :return: list of separate Voyages that the input Voyage has been split into.
    :return type: Voyage
    
    The function works by comparing consecutive observations in the input lists 
    and calculating the implied speed. If it is greater than 40 knots, a new ship 
    is generated. Each subsequent observation is assigned to the closest ship 
    unless the speed exceed 40 knots. If it does, a new ship is generated. 
    '''

    knots_conversion     = 0.539957
    
    if len(invoyage) <= 0:
        return []
    
    result = [1]
    n_ships = 1

    outvoyages = [ex.Voyage()]
    outvoyages[0].add_report(invoyage.getrep(0))
    
    ntimes = len(invoyage)

    if ntimes > 1:
        for i in range(1, ntimes):
            #calculate speeds from last position for each ship
            speeds = []
            distances = []
            for j in range(0, n_ships):
                
                last_rep = outvoyages[j].last_rep()
                
                speed, distance, course, timediff = invoyage.getrep(i)-last_rep
                
#calc predicted position and distance of new ob from predicted position
                pred_lat, pred_lon = outvoyages[j].predict_next_point(timediff)
                dist = sph.sphere_distance(invoyage.getvar(i, 'LAT'), 
                                           invoyage.getvar(i, 'LON'), 
                                           pred_lat, 
                                           pred_lon)
            
                distances.append(dist)
                if timediff != 0:
                    speeds.append(speed)
                else:
                    speeds.append(10000.)
                                                     
            #if all speeds exceed 40 knots then create new ship
            if min(speeds) > 40.0 / knots_conversion:
                n_ships = n_ships + 1
                voy = ex.Voyage()
                voy.add_report(invoyage.getrep(i))
                outvoyages.append(voy)
                result.append(n_ships)

#else ob is assigned to ship whose predicted location is closest to the ob
            else:
                winner = distances.index(min(distances))
                outvoyages[winner].add_report(invoyage.getrep(i))
                result.append(winner+1)
    
    return outvoyages

def get_clim(rep, clim):
    '''
    Get the climatological value for this particular observation
    
    :param rep: a MarineReport
    :param clim: a masked array containing the climatological averages
    :type rep: MarineReport
    :type clim: numpy array
    '''
    try: 
        rep_clim = qc.get_sst(rep.getvar('LAT'), 
                              rep.getvar('LON'), 
                              rep.getvar('MO'),
                              rep.getvar('DY'), 
                              clim)
        rep_clim = float(rep_clim)
    except:
        rep_clim = None

    return rep_clim

def read_climatology(infile, var):
    '''
    Read in the climatology for variable var from infile
    
    :param infile: filename of a netcdf file
    :param var: the variable name to be extracted from the netcdf file
    :type infile: string
    :type var: string
    '''
    climatology = Dataset(infile)
    return climatology.variables[var][:]

def main(argv):
    '''
    This program builds the marine data base which will be used to store the subset of ICOADS used in QC and 
    other data processing. The current version reads in IMMA1 data from ICOADS.2.5.1 and the UID is used as the 
    primary key for the data base so that it can be easily matched to individual obs if need be.

    The first step of the process is to read in the SST and MAT climatologies from file. These are 1degree latitude 
    by 1 degree longitude by 73 pentad fields in NetCDF format. The data are read into numpy arrays.

    Next a connection is made to the data base, which may or may not already exist. If it does not exist, a database 
    will be created.
    
    The program then loops over all years and months and DROPs existing tables for each year if they already exist and 
    then recreates them. It then loops over all months in the year, opens the appropriate IMMA file and reads in 
    the data one observation at a time.
    '''
    
    print '########################'
    print 'Running make_and_full_qc'
    print '########################'
    
    inputfile = 'configuration.txt'
    month1 = 1
    month2 = 1
    year1 = 1880
    year2 = 1880
    inputfile = 'configuration_local.txt'
    
    try:
        opts, args = getopt.getopt(argv, "hi:", 
                                   ["ifile=", 
                                    "year1=", 
                                    "year2=",
                                    "month1=",
                                    "month2="])
    except getopt.GetoptError:
        print 'Usage Make_DB.py -i <configuration_file> '+\
        '--year1 <start year> --year2 <end year> '+\
        '--month1 <start month> --month2 <end month>'
        sys.exit(2)

    inputfile, year1, year2, month1, month2 = qc.get_arguments(opts)

    print 'Input file is ', inputfile
    print 'Running from ', year1, ' to ', year2
    print ''

    config = qc.get_config(inputfile)

    sst_climatology_file  = config['SST_climatology'] 
    nmat_climatology_file = config['MAT_climatology'] 
    icoads_dir            = config['ICOADS_dir'] 
    bad_id_file           = config['IDs_to_exclude']
        
    sst_stdev_climatology_file  = config['Old_SST_stdev_climatology']
    
    sst_stdev_1_file = config['SST_buddy_one_box_to_buddy_avg']
    sst_stdev_2_file = config['SST_buddy_one_ob_to_box_avg']
    sst_stdev_3_file = config['SST_buddy_avg_sampling']

    print 'SST climatology =', sst_climatology_file
    print 'NMAT climatology =', nmat_climatology_file
    print 'ICOADS directory =', icoads_dir
    print 'List of bad IDs =', bad_id_file 
    print ''

    ids_to_exclude = process_bad_id_file(bad_id_file)

#read in climatology files
    climsst = read_climatology(sst_climatology_file, 'sst')
    climnmat = read_climatology(nmat_climatology_file, 'nmat')

    sst_pentad_stdev = read_climatology(sst_stdev_climatology_file, 'sst')
    
    sst_stdev_1 = read_climatology(sst_stdev_1_file, 'sst')
    sst_stdev_2 = read_climatology(sst_stdev_2_file, 'sst')
    sst_stdev_3 = read_climatology(sst_stdev_3_file, 'sst')

    print 'Read climatology files'

    tim00 = time.time()

    for year, month in qc.year_month_gen(year1, month1, year2, month2):

        tim0 = time.time()

        print year, month

        last_year, last_month = qc.last_month_was(year, month)
        next_year, next_month = qc.next_month_is(year, month)

        if last_year < 1850:
            last_year = 1850
            last_month = 1

        print last_year, last_month, next_year, next_month

        reps = ex.Deck()
        count = 0

        for readyear, readmonth in qc.year_month_gen(last_year, 
                                                     last_month, 
                                                     next_year, 
                                                     next_month):

            print readyear, readmonth

            syr = str(readyear)
            smn = "%02d" % (readmonth)
    
            filename = icoads_dir+'/R2.5.1.'+syr+'.'+smn+'.gz'
            if year > 2007:
                filename = icoads_dir+'/R2.5.2.'+syr+'.'+smn+'.gz'
    
            icoads_file = gzip.open(filename,"r")
    
            rec = IMMA()
   
            EOF = False
    
            while not(EOF):

#need to wrap the read in a exception catching thingy 
#becasuse there are some IMMA records which contain control 
#characters
                try:
                    result = rec.read(icoads_file)
                    if result == None:
                        EOF = True
                        rec.data['ID'] = ids_to_exclude[0]
                except:
                    rec.data['ID'] = ids_to_exclude[0]


                if not(rec.data['ID'] in ids_to_exclude):

#strip everything out of the IMMA record except what we need
                    keys = []
                    for key in rec.data:
                        keys.append(key)
                    for key in keys:
                        if not(key in ['YR','MO','DY','HR','LAT','LON',
                                       'SST','AT','DCK','ID','PT','SI',
                                       'SIM','DS','VS','SLP','UID','SID']):
                            if key in rec.data: del rec.data[key]

                    rep = ex.MarineReport(rec)
                    del rec

                    rep_sst_clim = get_clim(rep, climsst)
                    rep.add_climate_variable('SST', rep_sst_clim)

                    rep_mat_clim = get_clim(rep, climnmat)
                    rep.add_climate_variable('AT', rep_mat_clim)

#Deck 701 has a whole bunch of otherwise good obs with missing Hours.
#Set to 0000UTC and recalculate the ob time
                    if (rep.getvar('DCK') == 701 and 
                        rep.getvar('YR') < 1860 and 
                        rep.getvar('HR') == None):
                        rep.data['HR'] = 0
                        rep.calculate_dt()

                    rep = base_qc_report(rep)

                    reps.append(rep)
                    count += 1

                rec = IMMA()

            icoads_file.close()

        tim1 = time.time()
        print count, " obs read and base QC ", tim1-tim0
        
#filter the obs into passes and fails of basic positional QC        
        reps.sort()
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        passes, reps = filt.split_reports(reps)
        passes.sort()

        tim2 = time.time()
        print "obs filtered and sorted in ", tim2-tim1, len(reps)+len(passes)

#all fails pass track check 
        reps.set_qc('POS', 'trk', 0)
        reps.set_qc('POS', 'few', 0)
        reps.set_qc('SST', 'rep', 0)
        reps.set_qc('AT',  'rep', 0)


#track check the passes one ship at a time
        for one_ship in passes.get_one_ship_at_a_time():
            one_ship.track_check()
            one_ship.find_repeated_values(threshold=0.7, intype='SST')
            one_ship.find_repeated_values(threshold=0.7, intype='AT')

            for rep in one_ship.rep_feed():
                rep.reset_ext()
                reps.append(rep)

        del passes

        reps.sort()

        tim3 = time.time()
        print "obs track checked in ", tim3-tim2, len(reps)

#SST buddy check
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk',    0)
        filt.add_qc_filter('SST', 'noval',  0)
        filt.add_qc_filter('SST', 'freez',  0)
        filt.add_qc_filter('SST', 'clim',   0)
        filt.add_qc_filter('SST', 'nonorm', 0)

        passes, reps = filt.split_reports(reps)

        passes.bayesian_buddy_check('SST', sst_stdev_1, sst_stdev_2, sst_stdev_3)
        passes.mds_buddy_check('SST', sst_pentad_stdev)

        reps.set_qc('SST', 'bbud', 0)
        reps.set_qc('SST', 'bud',  0)

        for i in range(0, len(passes)):
            rep = passes.pop(0)
            reps.append(rep)

        del passes

        reps.sort()

        tim4 = time.time()
        print "obs SST buddy checked in ", tim4-tim3, len(reps)

#NMAT buddy check
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk',    0)
        filt.add_qc_filter('POS', 'day',    0)
        filt.add_qc_filter('AT',  'noval',  0)
        filt.add_qc_filter('AT',  'clim',   0)
        filt.add_qc_filter('AT',  'nonorm', 0)
        passes, reps = filt.split_reports(reps)

        passes.bayesian_buddy_check('AT', sst_stdev_1, sst_stdev_2, sst_stdev_3)
        passes.mds_buddy_check('AT', sst_pentad_stdev)

        reps.set_qc('AT', 'bbud', 0)
        reps.set_qc('AT', 'bud', 0)

        for i in range(0, len(passes)):
            rep = passes.pop(0)
            reps.append(rep)

        del passes

        reps.sort()

        tim5 = time.time()
        print "obs MAT buddy checked in ", tim5-tim4, len(reps)

        syr = str(year)
        smn = "%02d" % (month)
        outfile = open(icoads_dir+'/new_suite_'+syr+smn+'.txt', 'w')
        for rep in reps.reps:
            if rep.data['YR'] == year and rep.data['MO'] == month:
                outfile.write(rep.print_report())
        outfile.close()

        del reps

        tim11 = time.time()
        print year, " so far in ", tim11-tim00

if __name__ == '__main__':
    
    main(sys.argv[1:])