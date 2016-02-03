#!/usr/local/sci/bin/python2.7
'''
Extract obs from database
'''
import MySQLdb
import qc
import sys, getopt

def main(argv):
    '''
    For input year range, extract and print obs from the database.
    '''
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
            print 'Usage Make_DB.py -i <configuration_file> '+\
            '--year1 <start year> --year2 <end year>'
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

    #connect to data base    
    connection = MySQLdb.connect(host=data_base_host, 
                                 user='root',
                                 db=data_base_name)
    #need two cursors, one for reading and one for making QC changes
    cursor = connection.cursor()

    for years, months in qc.year_month_gen(year1, 1, year2, 12):
        
        print years, months
        
        syr = str(years)
        smn = "%02d" % (months,)

        print syr+smn

        outfile = open('/data/local/hadjj/ICOADS.2.5.1/blobs_'+syr+smn+'.txt','w')
        
        sql_request = 'SELECT \
        marinereports'+syr+'.id, \
        marinereports'+syr+'.lat, \
        marinereports'+syr+'.lon, \
        marinereports'+syr+'.sst, \
        marinereports'+syr+'.mat, \
        marinereports'+syr+'.year, \
        marinereports'+syr+'.month, \
        marinereports'+syr+'.day, \
        marinereports'+syr+'.hour, \
        marinereports'+syr+'.icoads_ds, \
        marinereports'+syr+'.icoads_vs, \
        marinereports'+syr+'.uid, \
        base_qc'+syr+'.bad_position , \
        base_qc'+syr+'.bad_date , \
        base_qc'+syr+'.bad_track , \
        sst_qc'+syr+'.no_sst , \
        sst_qc'+syr+'.sst_below_freezing , \
        sst_qc'+syr+'.sst_climatology_fail , \
        sst_qc'+syr+'.no_sst_normal , \
        sst_qc'+syr+'.sst_buddy_fail, \
        mat_qc'+syr+'.no_mat , \
        mat_qc'+syr+'.mat_climatology_fail, \
        mat_qc'+syr+'.no_mat_normal , \
        mat_qc'+syr+'.mat_buddy_fail,  \
        marinereports'+syr+'.dck, \
        marinereports'+syr+'.sid, \
        base_qc'+syr+'.day_check, \
        base_qc'+syr+'.blacklist, \
        base_qc'+syr+'.fewsome_check, \
        extra_qc'+syr+'.new_track_check, \
        extra_qc'+syr+'.bayesian_sst_buddy_check \
        FROM marinereports'+syr+' \
        INNER JOIN base_qc'+syr+' ON \
        marinereports'+syr+'.uid = base_qc'+syr+'.uid \
        INNER JOIN sst_qc'+syr+ ' ON \
        marinereports'+syr+'.uid = sst_qc'+syr+'.uid \
        INNER JOIN mat_qc'+syr+ ' ON \
        marinereports'+syr+'.uid = mat_qc'+syr+'.uid \
        INNER JOIN extra_qc'+syr+ ' ON \
        marinereports'+syr+'.uid = extra_qc'+syr+'.uid \
        WHERE marinereports'+syr+'.month = '+str(months)

        reps = []
        cursor.execute(sql_request)
        numrows = cursor.rowcount
        
        for i in range(numrows):
            rows = cursor.fetchone()
            rep = qc.MarineReport(rows[0], rows[1], rows[2], 
                                  rows[3], rows[4], rows[5],
                                  rows[6], rows[7], rows[8], 
                                  rows[9], rows[10], rows[11])

            rep.bad_position = rows[12]
            rep.bad_time = rows[13]
            rep.bad_track = rows[14]
            
            rep.no_sst = rows[15]
            rep.sst_below_freezing = rows[16]
            rep.sst_climatology_fail = rows[17]
            rep.no_sst_normal = rows[18]
            rep.sst_buddy_fail = rows[19]
            
            rep.no_mat = rows[20]
            rep.mat_climatology_fail = rows[21]
            rep.no_mat_normal = rows[22]
            rep.mat_buddy_fail = rows[23]
            
            rep.dck = rows[24]
            rep.sid = rows[25]
            
            rep.day_check = rows[26]
            rep.blacklist = rows[27]
            
            rep.fewsome_check = rows[28]
            rep.new_track_check = rows[29]
            rep.bayesian_sst_buddy_check = rows[30]
            
            reps.append(rep)

        reps.sort()
        for rep in reps:
            outfile.write(rep.print_report())
        
        outfile.close()
        
        print "out ", years, months
        
    connection.close()


if __name__ == '__main__':
    
    main(sys.argv[1:])
