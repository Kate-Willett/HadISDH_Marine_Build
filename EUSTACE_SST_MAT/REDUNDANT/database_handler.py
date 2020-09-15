'''
Data base handling methods and functions for the MDS
'''

import MySQLdb
import re
import qc

class Quality_Control_Filter:
    
    def __init__(self):
        
        self.qc_states = {}
        
        self.qc_states['bad_date']      = ['base_qc', -1]
        self.qc_states['bad_position']  = ['base_qc', -1]
        self.qc_states['land']          = ['base_qc', -1]
        self.qc_states['bad_track']     = ['base_qc', -1]
        self.qc_states['fewsome_check'] = ['base_qc', -1]
        self.qc_states['day_check']     = ['base_qc', -1]
        self.qc_states['blacklist']     = ['base_qc', -1]

        self.qc_states['sst_buddy_fail']       = ['sst_qc', -1]
        self.qc_states['no_sst']               = ['sst_qc', -1]
        self.qc_states['sst_below_freezing']   = ['sst_qc', -1]
        self.qc_states['no_sst_normal']        = ['sst_qc', -1]
        self.qc_states['sst_climatology_fail'] = ['sst_qc', -1]
        
        self.qc_states['mat_buddy_fail']       = ['mat_qc', -1]
        self.qc_states['no_mat']               = ['mat_qc', -1]
        self.qc_states['no_mat_normal']        = ['mat_qc', -1]
        self.qc_states['mat_climatology_fail'] = ['mat_qc', -1]

        self.qc_states['new_track_check']          = ['extra_qc', -1]
        self.qc_states['new_buddy_check']          = ['extra_qc', -1]
        self.qc_states['bayesian_sst_buddy_check'] = ['extra_qc', -1]
        self.qc_states['bayesian_mat_buddy_check'] = ['extra_qc', -1]
        self.qc_states['bayesian_track_check']     = ['extra_qc', -1]
        self.qc_states['spike_check']              = ['extra_qc', -1]
        self.qc_states['iquam_spike_check']        = ['extra_qc', -1]
        self.qc_states['repeated_value']           = ['extra_qc', -1]
        
        self.year = None
        self.month = None
        self.id_selection = []
        self.jul1 = None
        self.jul2 = None
    
    def extra_qc_flags_set(self):
        return self.type_qc_flags_set('extra_qc')
    
    def sst_qc_flags_set(self):
        return self.type_qc_flags_set('sst_qc')

    def mat_qc_flags_set(self):
        return self.type_qc_flags_set('mat_qc')
    
    def base_qc_flags_set(self):
        return self.type_qc_flags_set('base_qc')

    def type_qc_flags_set(self,table_name):
        result = False
        for flag_name in self.qc_states:
            if (self.qc_states[flag_name][0] == table_name and 
                self.qc_states[flag_name][1] != -1):
                result = True
        return result
    
    def set_multiple_qc_flags_to_pass(self, flag_names):
        '''
        The input flag_names will all be set to pass
        :param flag_names: list of flag names
        :type flag_names: string
        '''
        for flag_name in flag_names:
            self.set_qc_flag(flag_name, 0)

    def set_multiple_qc_flags_to_fail(self, flag_names):
        '''
        The input flag_names will all be set to fail
        :param flag_names: list of flag names
        :type flag_names: string
        '''
        for flag_name in flag_names:
            self.set_qc_flag(flag_name, 1)

    def get_qc_flag(self, qc_flag_name):
        '''
        Return the qc flag for the filter
        
        :param qc_flag_name: the name of the QC flag to be returned
        :type qc_flag_name: string
        :return: the flag value
        :rtype: int
        '''
        assert qc_flag_name in self.qc_states, "Unknown qc_flag_name "+str(qc_flag_name)
        return self.qc_states[qc_flag_name][1]

    def set_qc_flag(self, qc_flag_name, flag):
        '''
        Set the named qc flag to the flag value
        
        :param qc_flag_name: the name of the QC flag to be returned
        :param flag: the value to which the named flag should be set.
        :type qc_flag_name: string
        :type flag: int
        '''
        assert qc_flag_name in self.qc_states, "Unknown qc_flag_name "+str(qc_flag_name)
        assert flag in [-1,0,1], "Flag not one of -1,0,1 "+str(flag)
        self.qc_states[qc_flag_name][1] = flag

def get_marine_report_from_db(cursor,year,filter):

    sql_request = build_sql_query(year,filter)

    cursor.execute(sql_request)
#    numrows = cursor.rowcount
    rows = cursor.fetchall()

    reps = []
    for row in rows:
        reps.append(qc.MarineReport.report_from_array(row))

#    reps = []
#    for i in range(numrows):
#        rows = cursor.fetchone()
#        reps.append(qc.MarineReport.report_from_array(rows))

    return reps

def get_unique_ids(cursor,years,months):
    
    cursor.execute('SELECT DISTINCT id FROM marinereports'+str(years)+' WHERE \
    marinereports'+str(years)+'.year=%s AND marinereports'+str(years)+'.month=%s',
    (years, months) )
    
    allids = cursor.fetchall()
    
    return allids

def build_sql_query(year,filter):
    '''
    Get a list of marine reports from the data base which match the QC flags set in the filter
    '''

    sy = str(year)

    sql_request = 'SELECT '+\
    'marinereports'+sy+'.id, '+ \
    'marinereports'+sy+'.lat, '+ \
    'marinereports'+sy+'.lon, '+ \
    'marinereports'+sy+'.sst, '+ \
    'marinereports'+sy+'.mat, '+ \
    'marinereports'+sy+'.year, '+ \
    'marinereports'+sy+'.month, '+ \
    'marinereports'+sy+'.day, '+ \
    'marinereports'+sy+'.hour, '+ \
    'marinereports'+sy+'.icoads_ds, '+ \
    'marinereports'+sy+'.icoads_vs, '+ \
    'marinereports'+sy+'.uid, '+ \
    'marinereports'+sy+'.pt, '+ \
    'marinereports'+sy+'.si, '+ \
    'marinereports'+sy+'.c1, '+ \
    'marinereports'+sy+'.dck, '+ \
    'marinereports'+sy+'.sid, '+ \
    'ob_extras'+sy+'.sst_norm, '+ \
    'ob_extras'+sy+'.mat_norm '+ \
    'FROM marinereports'+sy+''

    sql_request = sql_request +' INNER JOIN ob_extras'+sy+' ON marinereports'+sy+'.uid = ob_extras'+sy+'.uid' 

    if filter.type_qc_flags_set('base_qc'):
        sql_request = sql_request +' INNER JOIN base_qc'+sy+  ' ON marinereports'+sy+'.uid = base_qc'+sy+'.uid'
    
    if filter.type_qc_flags_set('sst_qc'):
        sql_request = sql_request +' INNER JOIN sst_qc'+sy+  ' ON marinereports'+sy+'.uid = sst_qc'+sy+'.uid'

    if filter.type_qc_flags_set('mat_qc'):
        sql_request = sql_request +' INNER JOIN mat_qc'+sy+  ' ON marinereports'+sy+'.uid = mat_qc'+sy+'.uid'

    if filter.type_qc_flags_set('extra_qc'):
        sql_request = sql_request +' INNER JOIN extra_qc'+sy+  ' ON marinereports'+sy+'.uid = extra_qc'+sy+'.uid'

    sql_request = sql_request + ' WHERE '
    
    if filter.year != None and filter.month != None:
        sql_request = sql_request + \
        ' marinereports'+sy+'.year='+str(filter.year)+ \
        ' AND marinereports'+sy+'.month='+str(filter.month)+' AND '

    for flag_name in filter.qc_states:
        if filter.qc_states[flag_name][1] != -1:
            sql_request = sql_request + \
            filter.qc_states[flag_name][0]+sy+'.'+flag_name+' = '+str(filter.qc_states[flag_name][1])+' AND '

    if filter.jul1 != None and filter.jul2 != None: 
        sql_request = sql_request + '\
        marinereports'+sy+'.jul_day > '+str(filter.jul1)+' AND \
        marinereports'+sy+'.jul_day < '+str(filter.jul2)+''

#if string ends in 'WHERE ' or 'AND ' then trim them off.
    p = re.compile( 'WHERE $')
    sql_request = p.sub( '', sql_request)
    p = re.compile( 'AND $')
    sql_request = p.sub( '', sql_request)
    
    return sql_request

def make_additional_qc_table_for_year(cursor, year):
    '''
    Given a data base cursor this function will create a set of tables for the specified year.
    
    :param cursor: data base cursor for SQLite3 data base
    :param year: year to build the tables for
    :type cursor: unknown
    :type year: integer

    make the tables which will hold additional QC flags besides the original MDS 
    '''

    sy = str(year)
    
    cursor.execute('DROP TABLE IF EXISTS extra_qc'+sy)  
    cursor.execute('CREATE TABLE extra_qc'+sy+' LIKE extra_qc')

    return

def make_tables_for_year(cursor, year):
    '''
    Given a data base cursor this function will create a set of tables for the specified year.
    
    :param cursor: data base cursor for SQLite3 data base
    :param year: year to build the tables for
    :type cursor: unknown
    :type year: integer
    
    The contents of the tables are
    '''
    sy = str(year)

    cursor.execute('DROP TABLE IF EXISTS marinereports'+sy)  
    cursor.execute('DROP TABLE IF EXISTS base_qc'+sy)  
    cursor.execute('DROP TABLE IF EXISTS sst_qc'+sy)  
    cursor.execute('DROP TABLE IF EXISTS mat_qc'+sy)  
    cursor.execute('DROP TABLE IF EXISTS ob_extras'+sy)  
   
    cursor.execute('CREATE TABLE marinereports'+sy+' LIKE marinereports')
    cursor.execute('CREATE TABLE base_qc'+sy+' LIKE base_qc')
    cursor.execute('CREATE TABLE sst_qc'+sy+' LIKE sst_qc')
    cursor.execute('CREATE TABLE mat_qc'+sy+' LIKE mat_qc')
    cursor.execute('CREATE TABLE ob_extras'+sy+' LIKE ob_extras')

    return

def add_multiple_marine_reports_to_db(cursor, year, reps):

    datas_marinereports = []
    datas_base_qc = []
    datas_sst_qc = []
    datas_mat_qc = []
    datas_ob_extras = []
    datas_extra_qc = []

    for rep in reps:
        jultime = None
        if rep.year != None and rep.month != None and rep.day != None:
            jultime = qc.jul_day(rep.year,rep.month,rep.day)
 
        datas_marinereports.append((rep.uid, rep.id,  rep.year, rep.month, rep.day, 
                                    rep.hour, rep.lat, rep.lon,  rep.sst,  rep.mat,
                                    rep.c1,   rep.si,  rep.dck,  rep.sid,   rep.pt, 
                                    rep.ds,   rep.vs,  jultime))

        datas_base_qc.append((rep.uid, rep.bad_date, rep.bad_position, 
                             rep.land, rep.bad_track, rep.fewsome_check, 
                             rep.day_check, rep.blacklist))

        datas_sst_qc.append((rep.uid, rep.sst_buddy_fail, rep.no_sst, 
                             rep.sst_below_freezing, rep.no_sst_normal, 
                             rep.sst_climatology_fail))

        datas_mat_qc.append((rep.uid, rep.mat_buddy_fail, rep.no_mat, 
                             rep.no_mat_normal, rep.mat_climatology_fail))

        datas_extra_qc.append((rep.uid, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        
#ship       
        if rep.pt <= 5:
            datas_ob_extras.append((rep.uid, 
                                    0.7, 0.0, 0.8, 0.0, 0.0, rep.sst_norm, 
                                    0.9, 0.0, 0.6, 0.0, 0.0, rep.mat_norm))
#Moored buoy
        if rep.pt == 7:
            datas_ob_extras.append((rep.uid, 
                                    0.5, 0.0, 0.3, 0.0, 0.0, rep.sst_norm, 
                                    0.3, 0.0, 0.5, 0.0, 0.0, rep.mat_norm))
#Drifting buoy
        if rep.pt == 6:
            datas_ob_extras.append((rep.uid, 
                                    0.5, 0.0, 0.3, 0.0, 0.0, rep.sst_norm, 
                                    1.0, 0.0, 0.9, 0.0, 0.0, rep.mat_norm))

    cursor.executemany('INSERT INTO marinereports'+str(year)+
                   ' (uid,id, year,month,day,hour,lat,lon,sst,mat,c1,si,dck,sid,pt,icoads_ds,icoads_vs,jul_day)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    datas_marinereports)

    cursor.executemany('INSERT INTO base_qc'+str(year)+
                   ' (uid,bad_date,bad_position,land,bad_track,fewsome_check,day_check,blacklist)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                   ,datas_base_qc)
    
    cursor.executemany('INSERT INTO sst_qc'+str(year)+
                   ' (uid, sst_buddy_fail, no_sst, sst_below_freezing, no_sst_normal, sst_climatology_fail)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s)'
                   ,datas_sst_qc)
    
    cursor.executemany('INSERT INTO mat_qc'+str(year)+
                   ' (uid, mat_buddy_fail, no_mat, no_mat_normal, mat_climatology_fail)'+
                   ' VALUES (%s,%s,%s,%s,%s)'
                   ,datas_mat_qc)

    cursor.executemany('INSERT INTO extra_qc'+str(year)+
                   ' (uid,new_track_check,fewsome_check,new_buddy_check,'+
                   'bayesian_sst_buddy_check,bayesian_mat_buddy_check,'+
                   'bayesian_track_check,spike_check,iquam_spike_check,repeated_value)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                   ,datas_extra_qc)
    
    cursor.executemany('INSERT INTO ob_extras'+str(year)+
                   ' (uid,'+
                   ' random_unc_sst, micro_bias_sst, micro_bias_sst_unc, bias_sst,bias_unc_sst,sst_norm,'+
                   ' random_unc_mat, micro_bias_mat, micro_bias_mat_unc, bias_mat,bias_unc_mat,mat_norm)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                   ,datas_ob_extras)


    return

def add_marine_report_to_db(cursor,year,rep):
    '''
    Add a marine report to the data base
    
    :param cursor: Database cursor for adding the report to the database
    :param year: year of the observation
    :param rep: :class:`.MarineReport`
    :type cursor: database cursor
    :type year: integer
    :type rep: :class:`.MarineReport`
    '''
    
    #calculate the Julian day of the observattion   
    jultime = None
    if rep.year != None and rep.month != None and rep.day != None:
        jultime = qc.jul_day(rep.year,rep.month,rep.day)

    cursor.execute('INSERT INTO marinereports'+str(year)+
                   ' (uid,id, year,month,day,hour,lat,lon,sst,mat,c1,si,dck,sid,pt,icoads_ds,icoads_vs,jul_day)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                   (rep.uid, rep.id,  rep.year, rep.month, rep.day, 
                    rep.hour, rep.lat, rep.lon,  rep.sst,  rep.mat,
                    rep.c1,   rep.si,  rep.dck,  rep.sid,   rep.pt, 
                    rep.ds,   rep.vs,  jultime))

#initialise QC flags to be null - neither pass nor fail
    cursor.execute('INSERT INTO base_qc'+str(year)+
                   ' (uid,bad_date,bad_position,land,bad_track,fewsome_check,day_check,blacklist)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                   ,(rep.uid, rep.bad_date, rep.bad_position, 
                     rep.land, rep.bad_track, rep.fewsome_check, 
                     rep.day_check, rep.blacklist))
    
    cursor.execute('INSERT INTO sst_qc'+str(year)+
                   ' (uid, sst_buddy_fail, no_sst, sst_below_freezing, no_sst_normal, sst_climatology_fail)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s)'
                   ,(rep.uid, rep.sst_buddy_fail, rep.no_sst, 
                     rep.sst_below_freezing, rep.no_sst_normal, 
                     rep.sst_climatology_fail))
    
    cursor.execute('INSERT INTO mat_qc'+str(year)+
                   ' (uid, mat_buddy_fail, no_mat, no_mat_normal, mat_climatology_fail)'+
                   ' VALUES (%s,%s,%s,%s,%s)'
                   ,(rep.uid, rep.mat_buddy_fail, rep.no_mat, 
                     rep.no_mat_normal, rep.mat_climatology_fail))

    cursor.execute('INSERT INTO extra_qc'+str(year)+
                   ' (uid,new_track_check,fewsome_check,new_buddy_check,'+
                   'bayesian_sst_buddy_check,bayesian_mat_buddy_check,'+
                   'bayesian_track_check,spike_check,iquam_spike_check,repeated_value)'+
                   ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                   ,(rep.uid, 0, 0, 0, 0, 0, 0, 0, 0, 0))

#set some default values for the ob extra table from Kent and Berry ASMOS report
    if rep.pt <= 5:
        cursor.execute('INSERT INTO ob_extras'+str(year)+
                       ' (uid,'+
                       ' random_unc_sst, micro_bias_sst, micro_bias_sst_unc, bias_sst,bias_unc_sst,sst_norm,'+
                       ' random_unc_mat, micro_bias_mat, micro_bias_mat_unc, bias_mat,bias_unc_mat,mat_norm)'+
                       ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                       ,(rep.uid, 
                         0.7, 0.0, 0.8, 0.0, 0.0, rep.sst_norm, 
                         0.9, 0.0, 0.6, 0.0, 0.0, rep.mat_norm))
#Moored buoy
    if rep.pt == 7:
        cursor.execute('INSERT INTO ob_extras'+str(year)+
                       ' (uid,'+
                       ' random_unc_sst, micro_bias_sst, micro_bias_sst_unc, bias_sst,bias_unc_sst,sst_norm,'+
                       ' random_unc_mat, micro_bias_mat, micro_bias_mat_unc, bias_mat,bias_unc_mat,mat_norm)'+
                       ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                       ,(rep.uid, 
                         0.5, 0.0, 0.3, 0.0, 0.0, rep.sst_norm, 
                         0.3, 0.0, 0.5, 0.0, 0.0, rep.mat_norm))
#Drifting buoy
    if rep.pt == 6:
        cursor.execute('INSERT INTO ob_extras'+str(year)+
                       ' (uid,'+
                       ' random_unc_sst, micro_bias_sst, micro_bias_sst_unc, bias_sst,bias_unc_sst,sst_norm,'+
                       ' random_unc_mat, micro_bias_mat, micro_bias_mat_unc, bias_mat,bias_unc_mat,mat_norm)'+
                       ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                       ,(rep.uid, 
                         0.5, 0.0, 0.3, 0.0, 0.0, rep.sst_norm, 
                         1.0, 0.0, 0.9, 0.0, 0.0, rep.mat_norm))

    return

def add_imma1_record_to_db(cursor, year, x, climsst, climnmat):
    '''
    Given a database cursor and an IMMA report it will populate the appropriate table in the data base.
    
    :param cursor: data base cursor for SQLite3 data base
    :param year: year of the table to which the observation is to be added
    :param x: IMMA report to be added to the data base
    :param climsst: SST climatology
    :param climnmat: NMAT climatology
    :type cursor: unknown
    :type year: integer
    :type x: IMMA report
    :type climsst: numpy array
    :type climnmat: numpy array
    
    A feature of the current version is that, in line with MDS3 and earlier, the hour defaults to zero UTC when 
    hour is missing from the report.
    '''
    
    rep = qc.MarineReport.report_from_imma(x)

    inyear = year
    
#Deck 201 GMT midnights are assigned to the wrong day, see Carella, Kent, Berry 2015 Appendix A3 
#Reports from deck 201 before 1899 taken at the GMT midnight were moved one day before the reported date.
    if rep.dck == 201 and rep.year < 1899 and rep.hour == 0:
        rep.shift_day(-1)
        inyear = rep.year #make sure it goes in the right table

#Deck 701 prior to 1857ish has lots of obs with no hour set
    if rep.dck == 701 and rep.year < 1860 and rep.hour == None:
        rep.hour = 12.

    try:
        sst_climav  = qc.get_sst(rep.lat,rep.lon,rep.month,rep.day,climsst)
    except:
        sst_climav = None
    if sst_climav != None:
        sst_climav = float(sst_climav)

    try:
        mat_climav = qc.get_sst(rep.lat,rep.lon,rep.month,rep.day,climnmat)
    except:
        mat_climav = None
    if mat_climav != None:
        mat_climav = float(mat_climav)

    rep.setnorm(sst_climav, mat_climav)

    add_marine_report_to_db(cursor,inyear,rep)


    return

def update_db_qc_single_flag(rep,repval,tablename,flagname,year,cursor2):
    '''
    Update a single QC flag (repval, tablename, flagname) from (rep) in the database.
    
    :param rep: :class:`.MarineReport` containing the QC flag to be set
    :param repval: value from the report to be set
    :param tablename: name of the table to be modified
    :param flagname: name of the qc flag in the database to be set.
    :param year: year of the report to be set
    :param cursor2: database cursor
    :type rep: :class:`.MarineReport` 
    :type repval: integer
    :type tablename: string
    :type flagname: string
    :type year: integer
    :type cursor2: database cursor
    '''
    uid = rep.uid
    syr = str(year)
    
    if repval == 1:
        cursor2.execute('UPDATE '+tablename+syr+' SET '+flagname+'=1 WHERE uid=%s', (uid) )
    if repval == 0:
        cursor2.execute('UPDATE '+tablename+syr+' SET '+flagname+'=0 WHERE uid=%s', (uid) )
    if repval != 1 and repval != 0:
        cursor2.execute('UPDATE '+tablename+syr+' SET '+flagname+'='+str(repval)+' WHERE uid=%s', (uid) )

    return True

def update_db_basic_qc_flags(rep,year,cursor2):
    '''
    Update the basic QC flags in the data base.
    
    :param rep: marine report whose QC flags we wish to add to the database.
    :param year: year of the ob
    :param cursor2: database cursor
    :type rep: :class:`.MarineReport`
    :type year: integer
    :type cursor2: database cursor
    '''
#Basic
    result = update_db_qc_single_flag(rep, rep.day_check,    'base_qc', 'day_check',    year,cursor2)
    result = update_db_qc_single_flag(rep, rep.bad_position, 'base_qc', 'bad_position', year,cursor2)
    result = update_db_qc_single_flag(rep, rep.bad_date,     'base_qc', 'bad_date',     year,cursor2)
    result = update_db_qc_single_flag(rep, rep.blacklist,    'base_qc', 'blacklist',    year,cursor2)
       
#SST            
    result = update_db_qc_single_flag(rep, rep.no_sst,               'sst_qc',  'no_sst',               year,cursor2)
    result = update_db_qc_single_flag(rep, rep.sst_below_freezing,   'sst_qc',  'sst_below_freezing',   year,cursor2)
    result = update_db_qc_single_flag(rep, rep.sst_climatology_fail, 'sst_qc',  'sst_climatology_fail', year,cursor2)
    result = update_db_qc_single_flag(rep, rep.no_sst_normal,        'sst_qc',  'no_sst_normal',        year,cursor2)

#MAT
    result = update_db_qc_single_flag(rep, rep.no_mat,               'mat_qc',  'no_mat',               year,cursor2)
    result = update_db_qc_single_flag(rep, rep.mat_climatology_fail, 'mat_qc',  'mat_climatology_fail', year,cursor2)
    result = update_db_qc_single_flag(rep, rep.no_mat_normal,        'mat_qc',  'no_mat_normal',        year,cursor2)

    return True

def report_qc_counts(cursor,year,month):
    '''
    Print out QC outcomes for the given year and month
    
    :param cursor: data base cursor
    :param year: year to extract
    :param month: month to extract
    :type cursor: database cursor
    :type year: integer
    :type month: integer
    '''
    assert year >= 1850 and year <=2015
    assert month >=1 and month <=12
    
    print "Report"
    
    tables = {}
    
    tables['base_qc'] = ['bad_date','bad_position','land','bad_track','fewsome_check','day_check','blacklist']
    tables['sst_qc'] = ['sst_buddy_fail','no_sst','sst_below_freezing','no_sst_normal','sst_climatology_fail']
    tables['mat_qc'] = ['mat_buddy_fail','no_mat','no_mat_normal','mat_climatology_fail']
    tables['extra_qc'] = ['new_track_check','fewsome_check','new_buddy_check',
                          'bayesian_sst_buddy_check','bayesian_mat_buddy_check','bayesian_track_check',
                          'spike_check','iquam_spike_check','repeated_value'
                          ]

    syr = str(year)
  
    for tablename in tables:
        for name in tables[tablename]:
            cursor.execute("SELECT COUNT(*) FROM "+tablename+syr+
                           " INNER JOIN marinereports"+syr+
                           " ON "+tablename+syr+".uid = marinereports"+syr+
                           ".uid WHERE "+name+" = 1 AND marinereports"+syr+
                           ".year=%s AND marinereports"+syr+
                           ".month=%s", (year, month) )
            fails = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM "+tablename+syr+
                           " INNER JOIN marinereports"+syr+
                           " ON "+tablename+syr+".uid = marinereports"+syr+
                           ".uid WHERE "+name+" = 0 AND marinereports"+syr+
                           ".year=%s AND marinereports"+syr+
                           ".month=%s",(year, month))
            passes = cursor.fetchone()[0]
            print '{:7.7}:{:20.20}: Failed={:8.8}, Passed={:8.8}'.format(tablename, name, str(fails), str(passes))

    dink=1
    return dink


def disable_keys(cursor, year):
    
    syr = str(year)
    
    cursor.execute('ALTER TABLE marinereports'+syr+' DISABLE KEYS')
    cursor.execute('ALTER TABLE base_qc'+syr+' DISABLE KEYS')
    cursor.execute('ALTER TABLE sst_qc'+syr+' DISABLE KEYS')
    cursor.execute('ALTER TABLE mat_qc'+syr+' DISABLE KEYS')
    cursor.execute('ALTER TABLE extra_qc'+syr+' DISABLE KEYS')
    cursor.execute('ALTER TABLE ob_extras'+syr+' DISABLE KEYS')
    
def enable_keys(cursor, year):
    
    syr = str(year)
    
    cursor.execute('ALTER TABLE marinereports'+syr+' ENABLE KEYS')
    cursor.execute('ALTER TABLE base_qc'+syr+' ENABLE KEYS')
    cursor.execute('ALTER TABLE sst_qc'+syr+' ENABLE KEYS')
    cursor.execute('ALTER TABLE mat_qc'+syr+' ENABLE KEYS')
    cursor.execute('ALTER TABLE extra_qc'+syr+' ENABLE KEYS')
    cursor.execute('ALTER TABLE ob_extras'+syr+' ENABLE KEYS')
    

