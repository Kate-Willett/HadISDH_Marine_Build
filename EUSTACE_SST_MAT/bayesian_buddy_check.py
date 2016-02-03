#!/usr/local/sci/bin/python2.7

'''
Bayesian Buddy Check - main routine. Extracts observations from database 
between user specified years and runs buddy checks on both SST 
and NMAT.

Run from the command line like so::

  python2.7 bayesian_buddy_check.py -i configuration.txt --year1 1850 --year2 1897

'''

import MySQLdb
import numpy as np
import calendar
from netCDF4 import Dataset
import qc
import qc_buddy_check
import sys, getopt
import database_handler as db

import time

def main(argv):
    '''
    The buddy check compares observations to other nearby observations. If the observation differs 
    substantially from the neighbour-average, the observation will be rejected.
    '''

    print '###################'
    print 'Running bayesian_buddy_check'
    print '###################'
    
    inputfile = 'configuration.txt'
    month1 = 1
    month2 = 12

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
    print 'Running from year  ', year1,  ' to ', year2
    print 'Running from month ', month1, ' to ', month2
    print ''

    config = qc.get_config(inputfile)

    sst_climatology_file  = config['SST_climatology'] 
    nmat_climatology_file = config['MAT_climatology'] 
    data_base_host        = config['data_base_host']
    data_base_name        = config['data_base_name']
    icoads_dir            = config['ICOADS_dir'] 
    sst_stdev_climatology_file  = config['SST_stdev_climatology']

    sst_stdev_1_file = config['SST_buddy_one_box_to_buddy_avg']
    sst_stdev_2_file = config['SST_buddy_one_ob_to_box_avg']
    sst_stdev_3_file = config['SST_buddy_avg_sampling']

    print 'SST climatology =', sst_climatology_file
    print 'NMAT climatology =', nmat_climatology_file
    print 'Data base host =', data_base_host
    print 'Data base name =', data_base_name
    print 'ICOADS directory =', icoads_dir
    print ''

#read in the pentad climatology of standard deviations
    climatology = Dataset(sst_stdev_climatology_file)
    sst_pentad_stdev = climatology.variables['sst'][:]

    climatology = Dataset(sst_stdev_1_file)
    sst_stdev_1 = climatology.variables['sst'][:]
    climatology = Dataset(sst_stdev_2_file)
    sst_stdev_2 = climatology.variables['sst'][:]
    climatology = Dataset(sst_stdev_3_file)
    sst_stdev_3 = climatology.variables['sst'][:]

    connection = MySQLdb.connect(host=data_base_host, 
                                 user='root',
                                 db=data_base_name)
    cursor  = connection.cursor() #read
    cursor2 = connection.cursor() #write

    for years, months in qc.year_month_gen(year1, month1, year2, month2):


#want to get a month either side of the 
#target month, which may be in different years
        last_year, last_month = qc.last_month_was(years, months)
        next_year, next_month = qc.next_month_is(years, months)
        
        print years, months
        
        first_year = min([last_year, years, next_year])
        final_year = max([last_year, years, next_year])
        
        if first_year < 1850:
            first_year = 1850
        if final_year > 2014:
            final_year = 2014

#first and last julian days are +- approximately one month
        month_lengths = qc.month_lengths(years)
        jul1 = qc.jul_day(years, months, 1)-25
        jul2 = qc.jul_day(years, months, month_lengths[months-1])+25
        
        for check_variable in ['SST','MAT']:
            
            t0 = time.time()
        
            reps = []
            for yyy in range(first_year, final_year+1):
                
                qcfilter = db.Quality_Control_Filter()
                qcfilter.jul1 = jul1
                qcfilter.jul2 = jul2
                qcfilter.set_multiple_qc_flags_to_pass(['bad_position',
                                                        'bad_date',
                                                        'blacklist',
                                                        'new_track_check',
                                                        'fewsome_check'])

                if check_variable == 'SST':
                    qcfilter.set_multiple_qc_flags_to_pass(['no_sst',
                                                            'sst_below_freezing',
                                                            'no_sst_normal',
                                                            'sst_climatology_fail'])
                elif check_variable == 'MAT':
                    qcfilter.set_multiple_qc_flags_to_pass(['no_mat',
                                                            'no_mat_normal',
                                                            'mat_climatology_fail'])
                else:
                    print "no such type ", check_variable
                    assert False

                sql_request = db.build_sql_query(yyy, qcfilter)
                 
                cursor.execute(sql_request)
                numrows = cursor.rowcount

                for i in range(numrows):
                    rows = cursor.fetchone()
                    rep = qc.MarineReport.report_from_array(rows)
                    reps.append(rep)

            t1 = time.time()
            print len(reps)," observations read in", t1-t0

#Do the buddy check
            if check_variable == 'SST':
                qcs = qc_buddy_check.bayesian_buddy_check(reps, 
                                                          sst_stdev_1, sst_stdev_2, sst_stdev_3, 
                                                          'SST')
            elif check_variable == 'MAT':
                qcs = qc_buddy_check.bayesian_buddy_check(reps, 
                                                          sst_stdev_1, sst_stdev_2, sst_stdev_3, 
                                                          'MAT')
            else:
                print "no such type ", check_variable
                assert False

            t2 = time.time()
            print "done check ",t2-t1
            
#put updated QC flags into data base
            for rep in reps:
                if rep.month == months:
                    if check_variable == 'SST':
                        result = db.update_db_qc_single_flag(rep,
                                                             rep.bayesian_sst_buddy_check,
                                                             'extra_qc',
                                                             'bayesian_sst_buddy_check',
                                                             years,
                                                             cursor2)
                    elif check_variable == 'MAT':
                        result = db.update_db_qc_single_flag(rep,
                                                             rep.bayesian_mat_buddy_check,
                                                             'extra_qc',
                                                             'bayesian_mat_buddy_check',
                                                             years,
                                                             cursor2)
                    else:
                        print "no such type ", check_variable
                        assert False

            t3 = time.time()
            print "Of "+str(len(qcs))+" observations "+\
            str(np.sum(qcs))+" failed "+check_variable+\
            " buddy check",t3-t2

        connection.commit() #Each month
        db.report_qc_counts(cursor, years, months)
            
    connection.close()

    print "All Done :)"

if __name__ == '__main__':
    
    main(sys.argv[1:])
    
