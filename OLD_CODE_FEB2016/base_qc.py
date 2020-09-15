#!/usr/local/sci/bin/python2.7
'''
Base QC: run from the command line like so::

  python2.7 base_qc.py -i configuration.txt --year1 1850 --year2 1899
  
'''
import MySQLdb
import numpy as np
import math
from datetime import date, time, datetime
import calendar
import qc
import sys, getopt
import database_handler as db

import time

def main(argv):
    '''
    This is the program that runs the base QC on data in the data base (created by Make_DB.py. The checks are the simpler 
    checks, which can be performed on an observation-by-observation basis.
    '''
    
    print '###############'
    print 'Running base_qc'
    print '###############'
    
    inputfile = 'configuration.txt'
    month1 = 1
    month2 = 12

    try:
        opts, args = getopt.getopt(argv,"hi:",
                                   ["ifile=",
                                    "year1=",
                                    "year2=",
                                    "month1=",
                                    "month2="])
    except getopt.GetoptError:
        print 'Usage Make_DB.py -i <configuration_file> '+\
        '--year1 <start year> --year2 <end year>'+\
        '--month1 <start month> --month2 <end month>'
        sys.exit(2)

    inputfile, year1, year2, month1, month2 = qc.get_arguments(opts)

    print 'Input file is ', inputfile
    print 'Running from ',year1,' to ',year2
    print 'Running from ',month1,' to ',month2
    print ''

    config = qc.get_config(inputfile)

    data_base_host        = config['data_base_host']
    data_base_name        = config['data_base_name'] 

    print 'Data base host =', data_base_host
    print 'Data base name =', data_base_name
    print ''

#connect to data base	
    connection = MySQLdb.connect(host=data_base_host, 
                                 user='root',
                                 db=data_base_name)

    for years,months in qc.year_month_gen(year1, month1, year2, month2):

        print '\nRunning Base QC for',years,months

        cursor = connection.cursor()
        cursor2 = connection.cursor()

        syr = str(years)
        
        '''set up a QC filter and use it to extract obs from the database direct into MarineReport format'''
        filter = db.Quality_Control_Filter()
        filter.year = years
        filter.month = months

        t0 = time.time()
        reps = db.get_marine_report_from_db(cursor,years,filter)
        t1 = time.time()
        total_time = t1-t0
        print "read",total_time

        '''For each report, do all the basic QC checks then update the QC flags in the data base'''
        for rep in reps:

            rep.bad_position = qc.position_check(rep.lat, rep.lon)
            rep.bad_date = qc.date_check(rep.year, rep.month, rep.day, rep.hour)
            if rep.bad_position == 0 and rep.bad_date == 0:
                rep.day_check = qc.day_test(rep.year,rep.month,rep.day,rep.hour,rep.lat,rep.lon)
            else:
                rep.day_check = 1

            rep.no_sst = qc.value_check(rep.sst)
            rep.sst_below_freezing = qc.sst_freeze_check(rep.sst, 0.0)
            rep.sst_climatology_fail = qc.climatology_check(rep.sst,rep.sst_norm,8.0)
            rep.no_sst_normal = qc.no_normal_check(rep.sst_norm)
            
            rep.no_mat = qc.value_check(rep.mat)
            rep.mat_climatology_fail = qc.climatology_check(rep.mat,rep.mat_norm,10.0)
            rep.no_mat_normal = qc.no_normal_check(rep.mat_norm)
            
            rep.blacklist = qc.blacklist(rep.id, rep.dck, rep.year, rep.lat, rep.lon)
            
        t15 = time.time()
        print "qcd",t15-t1
        for rep in reps:
            result = db.update_db_basic_qc_flags(rep,years,cursor2)
            
        t2 = time.time()
        print "added to db",t2-t15
        '''Commit the changes then print a summary'''
        connection.commit()
        #db.report_qc_counts(cursor,years,months)
        t3 = time.time()
        print "commited",t3-t2

    connection.close()

    print "All Done :)"


if __name__ == '__main__':

    main(sys.argv[1:])
