import unittest
import sqlite3
import database_handler as db
import qc
import re

class TestDBHandler_QCFilter(unittest.TestCase):
    
    def setUp(self):
        
        self.filter = db.Quality_Control_Filter()
        self.allnames = ['bad_date','bad_position',
                         'land','bad_track','fewsome_check',
                         'day_check','blacklist',
                         'sst_buddy_fail','no_sst',
                         'sst_below_freezing','no_sst_normal',
                         'sst_climatology_fail','mat_buddy_fail','no_mat',
                         'no_mat_normal','mat_climatology_fail']
        
    def test_default_flags_all_minus_one(self):
        for name in self.allnames:
            self.assertEqual(self.filter.get_qc_flag(name),-1)

    def test_set_flags_and_get_flags(self):
        for flag in [-1,0,1]:
            for name in self.allnames:
                self.filter.set_qc_flag(name,flag)
                self.assertEqual(self.filter.get_qc_flag(name),flag)

    def test_set_multiple_flags(self):
        
        self.filter.set_multiple_qc_flags_to_pass(['bad_date','bad_position'])
        self.assertEqual(self.filter.get_qc_flag('bad_date'),0)
        self.assertEqual(self.filter.get_qc_flag('bad_position'),0)  

    def test_sst_flags_not_set(self):
        self.assertFalse(self.filter.sst_qc_flags_set())

    def test_sst_flags_set(self):
        self.filter.set_qc_flag('no_sst',0)
        self.assertTrue(self.filter.sst_qc_flags_set())

class TestDBHandler_build_sql_query(unittest.TestCase):
    
    def setUp(self):
        self.filter = db.Quality_Control_Filter()
        self.allnames = ['bad_date','bad_position',
                         'land','bad_track','fewsome_check',
                         'day_check','blacklist',
                         'sst_buddy_fail','no_sst',
                         'sst_below_freezing','no_sst_normal',
                         'sst_climatology_fail','mat_buddy_fail','no_mat',
                         'no_mat_normal','mat_climatology_fail']

    def test_setting_no_sst_has_no_sst_in_output(self):
        for name in self.allnames:
            self.filter.set_qc_flag(name, 0)
            result = db.build_sql_query(2012,self.filter)
            self.assertNotEqual(re.search(name, result),None)

    def test_empty_filter_does_not_match_specific_qc_name(self):
        result = db.build_sql_query(2012,self.filter)
        for name in self.allnames:
            self.assertEqual(re.search(name, result),None)

    def test_year_and_month_built(self):
        self.filter.year = 2012
        self.filter.month = 3
        result = db.build_sql_query(2012,self.filter)
        self.assertNotEqual(re.search('year=2012', result),None)
        self.assertNotEqual(re.search('month=3', result),None)

class TestDBHandler_make_tables_for_year(unittest.TestCase):
    
    def setUp(self):
        self.connection=sqlite3.connect(':memory:')
    
    def tearDown(self):
        self.connection.close()
        
    def test_make_single_table(self):
        cursor  = self.connection.cursor() 
        db.make_tables_for_year(cursor, 2015)
        self.connection.commit()

class TestDBHandler_add_marine_report_to_db(unittest.TestCase):
    
    def setUp(self):
        self.connection=sqlite3.connect(':memory:')
        cursor  = self.connection.cursor() 
        db.make_tables_for_year(cursor, 2015)
        db.make_additional_qc_table_for_year(cursor, 2015)
        self.connection.commit()
        
    def tearDown(self):
        self.connection.close()

    def test_add_simple_report(self):
        cursor  = self.connection.cursor() 
        rep = qc.MarineReport.report_from_array([0,0,0,0,0,2015,1,1,0,0,0,0,0,0,0,0,0,0,0])
        db.add_marine_report_to_db(cursor,2015,rep)
        self.connection.commit()

if __name__ == '__main__':
    unittest.main()
