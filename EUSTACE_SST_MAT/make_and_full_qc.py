#!/usr/local/sci/bin/python2.7
'''
# KW changed make_and_qc_db.py to make_and_full_qc.py
# KW changed by adding --month1 and --month2
make_and_full_qc.py invoked by typing::

  python2.7 make_and_full_qc.py -i configuration.txt --year1 1850 --year2 1855 --month 1 --month2 12

# KW edited to reflect that code now produces QC'd ascii files rather than setting up a database
This builds an ascii database for the chosen years. The location 
of the data base, the locations of the climatology files are 
all to be specified in the configuration files.
'''

import gzip
from netCDF4 import Dataset
import qc
# KW This isn't used here but is called by Extended_IMMA.py
import qc_new_track_check as tc
# KW I don't think this is used
#import qc_buddy_check as bc
import spherical_geometry as sph
from IMMA2 import IMMA
import Extended_IMMA as ex
import sys, getopt
import time
# KW Added for debugging
import pdb # pdb.set_trace() or c

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
# KW Could noval = 0 be a value that is present in IMMA but actually a missing data indicator e.g. -99.9 or 99.9?
    rep.set_qc('SST', 'noval', qc.value_check(rep.getvar('SST'))) 
    rep.set_qc('SST', 'freez', 
               qc.sst_freeze_check(rep.getvar('SST'), 0.0))
    rep.set_qc('SST', 'clim', 
               qc.climatology_check(rep.getvar('SST'), rep.getnorm('SST'), 8.0))
    rep.set_qc('SST', 'nonorm', qc.no_normal_check(rep.getnorm('SST')))

#MAT base QC
# KW Could noval = 0 be a value that is present in IMMA but actually a missing data indicator e.g. -99.9 or 99.9?
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
    
    #KW added para
    The database is now just a set of ascii files for each year/month. Later it may be the SQL database.

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
# KW Querying second instance of inputfile - I have commented this out for now    
#    inputfile = 'configuration_local.txt'
    
    try:
        opts, args = getopt.getopt(argv, "hi:", 
                                   ["ifile=", 
                                    "year1=", 
                                    "year2=",
                                    "month1=",
                                    "month2="])
    except getopt.GetoptError:
# KW changed Make_DB.py to make_and_full_qc.py
        print 'Usage make_and_full_qc.py -i <configuration_file> '+\
        '--year1 <start year> --year2 <end year> '+\
        '--month1 <start month> --month2 <end month>'
        sys.exit(2)

    inputfile, year1, year2, month1, month2 = qc.get_arguments(opts)

    print 'Input file is ', inputfile
    print 'Running from ', year1, ' to ', year2
    print ''

    config = qc.get_config(inputfile)

# KW Added a 'switch' to tell the code whether to run in HadISDH only (HadISDHSwitch == True) mode or 
# full mode (HadISDHSwitch == False)
    HadISDHSwitch = config['HadISDHSwitch']

    sst_climatology_file  = config['SST_climatology'] 
    nmat_climatology_file = config['MAT_climatology'] 
# KW Added climatology files for the humidity variables 
#    shu_climatology_file  = config['SHU_climatology']
#    vap_climatology_file  = config['VAP_climatology']
#    crh_climatology_file  = config['CRH_climatology']
#    cwb_climatology_file  = config['CWB_climatology']
#    dpd_climatology_file  = config['DPD_climatology']
# KW Added climatology file for the SLP which is needed if no SLP ob exists, the it has failed qc
#    slp_climatology_file  = config['SLP_climatology']
    icoads_dir            = config['ICOADS_dir'] 
    bad_id_file           = config['IDs_to_exclude']
# KW added an item for the database dir to write out the QC'd ascii data to - hijacking SQL data_base_dir for now
    data_base_dir	  = config['data_base_dir']

# KW Noting this is set to read the OLD SST stdevs - nothing reads in the newer OSTIA one yet.       
    sst_stdev_climatology_file  = config['Old_SST_stdev_climatology']
    
    sst_stdev_1_file = config['SST_buddy_one_box_to_buddy_avg']
    sst_stdev_2_file = config['SST_buddy_one_ob_to_box_avg']
    sst_stdev_3_file = config['SST_buddy_avg_sampling']

    print 'SST climatology =', sst_climatology_file
    print 'NMAT climatology =', nmat_climatology_file
# KW Added climatology files for the humidity variables 
#    print 'SHU climatology =', shu_climatology_file
#    print 'VAP climatology =', vap_climatology_file
#    print 'CRH climatology =', crh_climatology_file
#    print 'CWB climatology =', cwb_climatology_file
# KW Added climatology files for SLP for calculation of humidity variables if no good quality SLP ob exists
#    print 'SLP climatology =', slp_climatology_file
    print 'ICOADS directory =', icoads_dir
    print 'List of bad IDs =', bad_id_file 
# KW added an item for the database dir to write out the QC'd ascii data to - hijacking SQL data_base_dir for now
    print 'QCd Database directory =', data_base_dir 
    print ''

    ids_to_exclude = process_bad_id_file(bad_id_file)

#read in climatology files
    climsst = read_climatology(sst_climatology_file, 'sst')
    climnmat = read_climatology(nmat_climatology_file, 'nmat')
# KW Added climatology read in files for the humidity variables
#    climshu = read_climatology(shu_climatology_file, 'hussclim')
#    climvap = read_climatology(vap_climatology_file, 'vapclim')
#    climcrh = read_climatology(hurs_climatology_file, 'hursclim')
#    climcwb = read_climatology(twet_climatology_file, 'twetclim')
#    climdpd = read_climatology(dpd_climatology_file, 'dpdclim')
# KW Added climatology read in files for SLP for calculating humidity variabls if no SLP value exists
#    climslp = read_climatology(slp_climatology_file, 'slpclim')

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
            last_year = 1850 # KW don't understand why last year forced to be 1850 yet
            last_month = 1

        print last_year, last_month, next_year, next_month

        reps = ex.Deck()
        count = 0

# KW This takes a long time to read in each year/month and process
# For every candidate year/month the year/month before and after are also read in
# Can we store the candidate year/month and following year/month for the next loop?
# Hopefully there will be enough memory on spice

        for readyear, readmonth in qc.year_month_gen(last_year, 
                                                     last_month, 
                                                     next_year, 
                                                     next_month):

            print readyear, readmonth

            syr = str(readyear)
            smn = "%02d" % (readmonth)
    
            filename = icoads_dir+'/R2.5.1.'+syr+'.'+smn+'.gz'
# KW FOUND A BUG - changed 'year' to 'readyear' below because it was trying to 
# read R2.5.2.2007.12.gz because 'year'=2008, 'month'=1
            if readyear > 2007:
                filename = icoads_dir+'/R2.5.2.'+syr+'.'+smn+'.gz'
    
            icoads_file = gzip.open(filename,"r")

# KW Noted that this creates an object of whole month of IMMA data separated into all available parameters from all available attachments
# The rec.read bit later could be speeded up by ignoring the attachments we are not interested in in the first place?    
# The rec object has a .data dictionary of all variables (see IMMA2.py for variable IDs/keys
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
                        # KW are we sure this isn't doing anything silly later when rec is overwritten with a new rec - could
			# this overwrite ids_to_exclude[0]?
			rec.data['ID'] = ids_to_exclude[0]
                except:
                    rec.data['ID'] = ids_to_exclude[0]


                if not(rec.data['ID'] in ids_to_exclude):

#strip everything out of the IMMA record except what we # KW (Kate Robert and John)# need
                    keys = []
                    for key in rec.data:
                        keys.append(key)
                    for key in keys:
# KW Added quite a few things in here - assume these don't have to be all from attachment 0 because UID isn't
# Assume they don't have to be in a particular order either
# I've put them in the order they appear in the attachments
# See: RequiredIMMAColumnsforHadISDH.xlsx
# Only a few of these will be written out but they are useful in the QC and bias adjustment process
# May remove some of these later if they are not useful - to save time/memory
#                        if not(key in ['YR','MO','DY','HR','LAT','LON',
#                                       'SST','AT','DCK','ID','PT','SI',
#                                       'SIM','DS','VS','SLP','UID','SID']):
                        if not(key in ['YR','MO','DY','HR','LAT','LON',
				       'DS','VS','II','ID','C1',
				       'DI','D','WI','W','VI','VV','SLP','RH','RHI',
				       'IT','AT','WBTI','WBT','DPTI','DPT','SI','SST',
				       'DCK','SID','PT','DUPS','RH','RHI',
				       'COR','TOB','TOT','EOT','LOT','TOH','EOH',
				       'SIM','LOV','HOP','HOT','HOB','HOA','SMF',
				       'UID']):
                            if key in rec.data: del rec.data[key]
							
                    rep = ex.MarineReport(rec)
                    del rec

#************HadISDH ONLY*******************************
# KW Added a catch here to check the platform type and whether there is both a T (AT) and DPT  present.
# Only keep the ob if it is from a ship (0,1,2,3,4,5) or moored platform/buoy (6,8,9,10,14,15) and has 
# AT and DPT present.
# This may not be desirable for a full run but should save time/memory for HadISDH
# If HadISDHSwitch == True then the ob needs to pass the test else all obs are processed
# No QC performed yet so cannot call get_qc - qc.value_check returns 0 if present and 1 if noval
		    if (not (HadISDHSwitch)) | ((rep.data['PT']  in [0,1,2,3,4,5,6,8,9,10,14,15]) & 
		                                (qc.value_check(rep.getvar('AT')) == 0) & 
						(qc.value_check(rep.getvar('DPT')) == 0)):

# KW TESTED: WORKS IF VALUES ARE BLANK AT LEAST
# KW CHECK THAT THIS KICKS OUT OBS WITH REPORTED MISSING VALUES (e.g. -99.9 or 99.9) FOR AT or DPT		    
#*******************************************************

# KW Call my rep.setvar routine that I built into the MarineReport in Extended_IMMA.py
# Use this to add blank var containers for the humidity variables that are calculated 
# later
                        rep.setvar(['SHU','VAP','CRH','CWB','DPD'])
					
                        rep_sst_clim = get_clim(rep, climsst)
                        rep.add_climate_variable('SST', rep_sst_clim)

                        rep_mat_clim = get_clim(rep, climnmat)
                        rep.add_climate_variable('AT', rep_mat_clim)

# KW Get climatologies for the humidity variables so that you can create anomalies later
#                        rep_shu_clim = get_clim(rep, climshu)
#                        rep.add_climate_variable('SHU', rep_shu_clim)

#			 rep_vap_clim = get_clim(rep, climvap)
#                        rep.add_climate_variable('VAP', rep_vap_clim)

#		         rep_crh_clim = get_clim(rep, climcrh)
#                        rep.add_climate_variable('CRH', rep_crh_clim)

#			 rep_cwb_clim = get_clim(rep, climcwb)
#                        rep.add_climate_variable('CWB', rep_cwb_clim)

#			 rep_dpd_clim = get_clim(rep, climdpd)
#                        rep.add_climate_variable('DPD', rep_dpd_clim)

# KW Get climatologies for slp to calculate humidity values later if no good quality qc ob exists
#                        rep_slp_clim = get_clim(rep, climslp)
#                        rep.add_climate_variable('SLP', rep_slp_clim)
					
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
# KW NOtes that this uses the month before and after to apply track check - and so actually spends time applying
# track check to the month before and month after too, which will then be ignored and redone later, with its following month
# Is there scope to save effort here by only checking the candidate month while still passing the surrounding months for info
        reps.sort()
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        passes, reps = filt.split_reports(reps)
        passes.sort()

        tim2 = time.time()
        print "obs filtered and sorted in ", tim2-tim1, len(reps)+len(passes)

# KW So in here we could put some kind of parsing loop to say that if you are looping through more than one month
# then you could save the candidate and previous month

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
# KW NOtes that this uses the month before and after to apply track check - and so actually spends time applying
# track check to the month before and month after too, which will then be ignored and redone later, with its following month
# Is there scope to save effort here by only checking the candidate month while still passing the surrounding months for info
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk',    0)
        filt.add_qc_filter('SST', 'noval',  0)
        filt.add_qc_filter('SST', 'freez',  0)
        filt.add_qc_filter('SST', 'clim',   0)
        filt.add_qc_filter('SST', 'nonorm', 0)

# KW Notes splitting marine obs into passes and fails
        passes, reps = filt.split_reports(reps)

# KW Thinks this only buddy checks those obs that pass the filter of QC above
        passes.bayesian_buddy_check('SST', sst_stdev_1, sst_stdev_2, sst_stdev_3)
        passes.mds_buddy_check('SST', sst_pentad_stdev)

# KW Thinks all fails obs that do not pass teh QC filter above are not buddy checked - they are set to 0
# which means pass but should not be used later because they fail one of the other basic checks
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
# KW NOtes that this uses the month before and after to apply track check - and so actually spends time applying
# track check to the month before and month after too, which will then be ignored and redone later, with its following month
# Is there scope to save effort here by only checking the candidate month while still passing the surrounding months for info
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date',   0)
        filt.add_qc_filter('POS', 'pos',    0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk',    0)
        filt.add_qc_filter('POS', 'day',    0)
        filt.add_qc_filter('AT',  'noval',  0)
        filt.add_qc_filter('AT',  'clim',   0)
        filt.add_qc_filter('AT',  'nonorm', 0)
# KW Notes that 'reps' are those obs that have failed one of the tests in the filter above
        passes, reps = filt.split_reports(reps)

# KW Notes that passes is an object containing a months worth of marine obs that pass (flag=0) for all above filters
# Both the bayesian buddy check and the mds buddy check test for distance to neighbours in space and time and flag
# with a 1 where it is too great/fails.
        passes.bayesian_buddy_check('AT', sst_stdev_1, sst_stdev_2, sst_stdev_3)
        passes.mds_buddy_check('AT', sst_pentad_stdev)

# KW - all fails (reps) are set to have a flag of 0 which means to pass the buddy checks.because there is no point in spending
# further time buddy checking them, same as for track checks
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
# KW changed outfile from icoards_dir to data_base_dir so that it writes to a different place to where the original 
# data are stored - don't want to mess with John's working version.
        outfile = open(data_base_dir+'/new_suite_'+syr+smn+'.txt', 'w')
        for rep in reps.reps:
            if rep.data['YR'] == year and rep.data['MO'] == month:
                outfile.write(rep.print_report())
        outfile.close()

        del reps

        tim11 = time.time()
        print year, " so far in ", tim11-tim00

if __name__ == '__main__':
    
    main(sys.argv[1:])
