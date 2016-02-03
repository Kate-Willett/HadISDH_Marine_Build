#!/usr/local/sci/bin/python2.7
'''
make_db.py invoked by typing::

  python2.7 make_full_db.py -i configuration.txt --year1 1850 --year2 1855

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

def main(argv):
    '''
    This program builds the skeleton marine data base, but doesn't populate the tables
    '''
    
    print '###############'
    print 'Running Make_DB'
    print '###############'

    inputfile = 'configuration.txt'

    try:
        opts, args = getopt.getopt(argv, 
                                   "hi:", 
                                   ["ifile=", 
                                    "year1=", 
                                    "year2="])
    except getopt.GetoptError:
        print 'Usage Make_DB.py -i <configuration_file> '+\
        '--year1 <start year> --year2 <end year>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-x", "--year1"):
            try:
                year1 = int(arg)
            except:
                sys.exit("Failed: year1 not an integer")
        elif opt in ("-y", "--year2"):
            try:
                year2 = int(arg)
            except:
                sys.exit("Failed: year2 not an integer")

    print 'Input file is ', inputfile
    print 'Running from ', year1, ' to ', year2
    print ''

    config = qc.get_config(inputfile)

    data_base_file        = config['data_base_dir']+config['data_base_name'] 
    icoads_dir            = config['ICOADS_dir'] 
    
    print 'Data base file =', data_base_file
    print 'ICOADS directory =', icoads_dir
    print ''

#connect to database
    connection = MySQLdb.connect(host='eld446',user='root',db='had_mdb')
#    connection = sqlite3.connect(data_base_file)
    cursor = connection.cursor()

    for year in range(year1, year2+1):
        print year
        db.make_tables_for_year(cursor, year)
        db.make_additional_qc_table_for_year(cursor, year)
        connection.commit()

#close the connection to the data base        
    connection.close()

if __name__ == '__main__':
    
    main(sys.argv[1:])