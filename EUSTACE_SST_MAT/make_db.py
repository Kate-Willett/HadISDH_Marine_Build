#!/usr/local/sci/bin/python2.7
'''
make_db.py invoked by typing::

  python2.7 make_db.py -i configuration.txt --year1 1850 --year2 1855

This builds a database for the chosen years. The location 
of the data base, the locations of the climatology files are 
all to be specified in the configuration files.
'''

import MySQLdb
import gzip
from netCDF4 import Dataset
import qc
from IMMA2 import IMMA
import database_handler as db
import sys, getopt

import time

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
    
    print '###############'
    print 'Running Make_DB'
    print '###############'
    
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
    print 'Running from ', year1, ' to ', year2
    print ''

    config = qc.get_config(inputfile)

    sst_climatology_file  = config['SST_climatology'] 
    nmat_climatology_file = config['MAT_climatology'] 
    data_base_host        = config['data_base_host']
    data_base_name        = config['data_base_name'] 
    icoads_dir            = config['ICOADS_dir'] 
    bad_id_file           = config['IDs_to_exclude']

    print 'SST climatology =', sst_climatology_file
    print 'NMAT climatology =', nmat_climatology_file
    print 'Data base host =', data_base_host
    print 'Data base name =', data_base_name
    print 'ICOADS directory =', icoads_dir
    print 'List of bad IDs =', bad_id_file 
    print ''


    idfile = open(bad_id_file, 'r')
    ids_to_exclude = []
    for line in idfile:
        line = line.rstrip()
        while len(line) < 9:
            line = line+' '
        ids_to_exclude.append(line)
    idfile.close()

#read in climatology files
    climatology = Dataset(sst_climatology_file)
    climsst = climatology.variables['sst'][:]

    climatology = Dataset(nmat_climatology_file)
    climnmat = climatology.variables['nmat'][:]

    print 'Read climatology files'

#connect to database
    connection = MySQLdb.connect(host=data_base_host, 
                                 user='root',
                                 db=data_base_name)
    cursor = connection.cursor()

    for year in range(year1, year2+1):

        db.make_tables_for_year(cursor, year)
        db.make_additional_qc_table_for_year(cursor, year)
        
        connection.commit()
        
        for month in range(1, 13):

            t0 = time.time()

            print year, month
            syr = str(year)
            smn = "%02d" % (month,)

            filename = icoads_dir+'/R2.5.1.'+syr+'.'+smn+'.gz'
            if year > 2007:
                filename = icoads_dir+'/R2.5.2.'+syr+'.'+smn+'.gz'

            icoads_file = gzip.open(filename,"r")

            rec = IMMA()

            count = 0
            while rec.read(icoads_file):
                if not(rec.data['ID'] in ids_to_exclude):
                    try:
                        db.add_imma1_record_to_db(cursor, 
                                                  year, 
                                                  rec, 
                                                  climsst, 
                                                  climnmat)
                        count += 1
                    except:
                        assert False, "Failed to add record to database"

            icoads_file.close()
            
            t1 = time.time()
            
            print count," obs ingested.",t1-t0
            
#commit once per month
            connection.commit()

#close the connection to the data base        
    connection.close()

if __name__ == '__main__':
    
    main(sys.argv[1:])