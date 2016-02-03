#!/usr/local/sci/bin/python2.7
'''
Track Check

Run from the command line like so::
  
  python2.7 track_check.py -i configuration.txt --year1 1850 --year2 1898

'''
import MySQLdb
import qc
import qc_track_check
import sys, getopt
import database_handler as db

def main(argv):
    
    '''
    The track check program. First the program gets a list of all unique IDs in the month 
    that is to be track checked. It then reads in three months of data at a time: the month 
    you want to track check, a month before and a month after. For each unique ID, the track 
    check is run.
    
    Track check comprises as set of related tests
    
    This program checks positional data for individual ships and buoys for internal consistency; 
    checking reported positions against positions calculated using reported speeds and directions.
    
    The obs are sorted by call-sign then date. Obs can only be checked if they have a valid call-sign 
    that is unique to one ship or buoy, so obs with no call-sign or with the generic call-signs 'SHIP' 
    or 'PLAT' are passed unchecked. The call-sign '0102' was apparently shared by several ships, so obs 
    with this call-sign are also passed unchecked.
    '''
    
    print '###################'
    print 'Running Track Check'
    print '###################'
    
    inputfile = 'configuration.txt'
    
    try:
        opts, args = getopt.getopt(argv, 
                                   "hi:", 
                                   ["ifile=", 
                                    "year1=", 
                                    "year2="])
    except getopt.GetoptError:
        print 'Usage Make_DB.py -i <configuration_file>'+\
        ' --year1 <start year> --year2 <end year>'
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
    
    data_base_host        = config['data_base_host']
    data_base_name        = config['data_base_name'] 

    print 'Data base host =', data_base_host
    print 'Data base name =', data_base_name

    print ''

    connection = MySQLdb.connect(host=data_base_host, 
                                 user='root',
                                 db=data_base_name)

    #need two cursors, one for reading and one for making QC changes
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    
    for years, months in qc.year_month_gen(year1, 1, year2, 12):
    
    #want to get a month either side of the target month, 
    #which may be in different years
        last_year, last_month = qc.last_month_was(years, months)
        next_year, next_month = qc.next_month_is(years, months)
        
        print years, months
        
        first_year = min([last_year, years, next_year])
        final_year = max([last_year, years, next_year])
    
        if first_year < 1850:
            first_year = 1850
        if final_year > 1990:
            final_year = 1990
    
    #first and last julian days are +- approximately one month
        month_lengths = qc.month_lengths(years)
        jul1 = qc.jul_day(years, months, 1)-10
        jul2 = qc.jul_day(years, months, month_lengths[months-1])+10
        
        '''Get all unique IDs for this month and fill a dictionary 
        with all the distinct ids that we want to QC as keys and an 
        empty list for each key'''
        allids = db.get_unique_ids(cursor, years, months)
        reps = {}
        for idrows in allids:
            thisid = idrows[0]
            reps[thisid] = []
            
    #extract all data for this month and a month either side
        for yyy in range(first_year, final_year+1):
            
            '''
            Build filter for extracting data from data base and then extract. 
            In this case, we want observations between jul1 and jul2 which pass 
            the base QC checks. 
            '''
            qcfilter = db.Quality_Control_Filter()
            qcfilter.jul1 = jul1
            qcfilter.jul2 = jul2
            qcfilter.set_multiple_qc_flags_to_pass(['bad_position',
                                                    'bad_date',
                                                    'blacklist'])
            
            sql_request = db.build_sql_query(yyy, qcfilter)
            
            cursor.execute(sql_request)
            numrows = cursor.rowcount

    #put each ob into the dictionary if there is a key for it
            for i in range(numrows):
                rows = cursor.fetchone()
                rep = qc.MarineReport.report_from_array(rows)
                if rep.id in reps:
                    reps[rep.id].append(rep)
    
   
    #loop over all the distinct callsigns, extract the obs 
    #where the callsign matches and track check them
        for idrows in allids:
            thisid = idrows[0]
            matches = reps[thisid]
            matches.sort()

            qcs = qc_track_check.mds_full_track_check(matches)
    
    #update QC in the data base but only for the target month
            for rep in matches:
                if rep.month == months:
                    result = db.update_db_qc_single_flag(rep,
                                                         rep.bad_track,
                                                         'base_qc',
                                                         'bad_track',
                                                         years,
                                                         cursor2)
    

        connection.commit()

        #db.report_qc_counts(cursor, years, months)
    
    connection.close()
    
    print "All Done :)"


if __name__ == '__main__':
    
    main(sys.argv[1:])
