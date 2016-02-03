import unittest
import numpy.ma as ma
from spherical_geometry import *
from qc import *
from netCDF4 import Dataset

class TestQCmethods_marine_reports(unittest.TestCase):
    
    def test_array_init_method(self):
        rep = MarineReport.report_from_array(['',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        self.assertEqual(rep.sst,0)

    def test_shift_day_backone_from_jan1(self):
        rep = MarineReport('r1      ', 0.0,  0.0,  22.0, 22.0, 1935, 1, 1, 12.0, 0, 3, 'ABCDEFGHI')
        rep.shift_day(-1)
        self.assertEqual(rep.day, 31)
        self.assertEqual(rep.year, 1934)
        self.assertEqual(rep.month, 12)

    def test_shift_day_backone_from_mar1_leapyear(self):
        rep = MarineReport('r1      ', 0.0,  0.0,  22.0, 22.0, 1936, 3, 1, 12.0, 0, 3, 'ABCDEFGHI')
        rep.shift_day(-1)
        self.assertEqual(rep.day, 29)
        self.assertEqual(rep.year, 1936)
        self.assertEqual(rep.month, 2)

    def test_shift_day_forward(self):
        rep = MarineReport('r1      ', 0.0,  0.0,  22.0, 22.0, 1936, 3, 1, 12.0, 0, 3, 'ABCDEFGHI')
        rep.shift_day(1)
        self.assertEqual(rep.day, 2)
        self.assertEqual(rep.year, 1936)
        self.assertEqual(rep.month, 3)
        

class TestQCmethods_split_generic(unittest.TestCase):

    def setUp(self):
        self.r1 = ExtendedMarineReport('r1      ', 0.0,  0.0,  22.0, 22.0, 1935, 8, 3, 12.0, 0, 3, 'ABCDEFGHI')
        self.r2 = ExtendedMarineReport('r2      ', 0.1,  0.0,  22.0, 22.0, 1935, 8, 3, 13.0, 0, 3, 'ABCDEFGHI')
        self.r3 = ExtendedMarineReport('r3      ', 0.2,  0.0,  22.0, 22.0, 1935, 8, 3, 14.0, 0, 3, 'ABCDEFGHI')
        self.s1 = ExtendedMarineReport('s1      ', 0.0, 90.0,  22.0, 22.0, 1935, 8, 3, 12.0, 0, 3, 'ABCDEFGHI')
        self.s2 = ExtendedMarineReport('s2      ', 0.1, 90.0,  22.0, 22.0, 1935, 8, 3, 13.0, 0, 3, 'ABCDEFGHI')
        self.t1 = ExtendedMarineReport('t1      ', 0.0, 180.0, 22.0, 22.0, 1935, 8, 3, 12.5, 0, 3, 'ABCDEFGHI')
        self.t2 = ExtendedMarineReport('t2      ', 0.1, 180.0, 22.0, 22.0, 1935, 8, 3, 13.5, 0, 3, 'ABCDEFGHI')
 
        self.invoyage1 = Voyage()
        self.invoyage1.add_report(self.r1)
        self.invoyage1.add_report(self.s1)
        self.invoyage1.add_report(self.r2)
        self.invoyage1.add_report(self.s2)

        self.invoyage2 = Voyage()
        self.invoyage2.add_report(self.r1)
        self.invoyage2.add_report(self.s1)
        self.invoyage2.add_report(self.t1)
        self.invoyage2.add_report(self.r2)
        self.invoyage2.add_report(self.s2)
        self.invoyage2.add_report(self.t2)

    def test_one_track(self):
    
        voy = Voyage()
        voy.add_report(self.r1)
        voy.add_report(self.r2)
        voy.add_report(self.r3)
        
        outvoyages = split_generic_callsign(voy)

        self.assertEqual(len(outvoyages),1)
        self.assertEqual(len(outvoyages[0].reps),len(voy.reps))
        self.assertEqual(len(outvoyages[0].reps),3)
     
    def test_two_widely_separated_tracks(self):
        
        outvoyages = split_generic_callsign(self.invoyage1)

        self.assertEqual(len(outvoyages),2)
        self.assertEqual(outvoyages[0].reps[0].id,'r1      ')
        self.assertEqual(outvoyages[0].reps[1].id,'r2      ')
        self.assertEqual(outvoyages[1].reps[0].id,'s1      ')
        self.assertEqual(outvoyages[1].reps[1].id,'s2      ')

    def test_three_widely_separated_tracks(self):
        
        outvoyages = split_generic_callsign(self.invoyage2)
        
        self.assertEqual(len(outvoyages),3)
        self.assertEqual(outvoyages[0].reps[0].id,'r1      ')
        self.assertEqual(outvoyages[0].reps[1].id,'r2      ')
        self.assertEqual(outvoyages[1].reps[0].id,'s1      ')
        self.assertEqual(outvoyages[1].reps[1].id,'s2      ')
        self.assertEqual(outvoyages[2].reps[0].id,'t1      ')
        self.assertEqual(outvoyages[2].reps[1].id,'t2      ')

    def test_predict_location_one_ob_returns_self(self):
    
        voy = Voyage()
        voy.add_report(self.r1)
        
        lat,lon = voy.predict_next_point(1.0)
        
        self.assertEqual(lat,self.r1.lat)
        self.assertEqual(lon,self.r1.lon)
        
    def test_predict_location_two_obs(self):
        
        voy = Voyage()
        voy.add_report(self.r1)
        voy.add_report(self.r2)
        
        lat,lon = voy.predict_next_point(1.0)
        
        self.assertAlmostEqual(lat,self.r3.lat,delta=0.0000001)
        self.assertAlmostEqual(lon,self.r3.lon,delta=0.0000001)

    def test_predict_two_obs_different_locations_same_time(self):
    
        voy = Voyage()
        voy.add_report(self.r1)
        voy.add_report(self.s1)
        lat,lon = voy.predict_next_point(1.0)

        self.assertEqual(lat,self.s1.lat)
        self.assertEqual(lon,self.s1.lon)
        
class TestQCmethods_voyage(unittest.TestCase):

    def setUp(self):
        self.r1 = ExtendedMarineReport('12345678', 0.0, 0.0, 22.0, 22.0, 1935, 
                                        8, 3, 12.0, 0, 3, 'ABCDEFGHI')
        self.r2 = ExtendedMarineReport('12345678', 1.0, 0.0, 23.0, 23.0, 1935, 
                                        8, 3, 13.0, 0, 3, 'ABCDEFGHI')


    
    def test_basics(self):
        
#        r1 = ExtendedMarineReport(shipid, lat, lon, sst, mat, year, \
#                 month, day, hour, icoads_ds, icoads_vs, uid)
        v = Voyage()
        v.add_report(self.r1)
        v.add_report(self.r2)
        
        self.assertEqual(v.reps[0].ext['distance'], None)
        self.assertEqual(v.reps[0].ext['time_diff'], None)
        self.assertEqual(v.reps[0].ext['speed'], None)
        self.assertEqual(v.reps[0].ext['course'], None)
        
        self.assertAlmostEqual(v.reps[1].ext['distance'], 111., delta = 1)
        self.assertAlmostEqual(v.reps[1].ext['time_diff'], 1, delta = 0.0000001)
        self.assertAlmostEqual(v.reps[1].ext['speed'], 111., delta = 1)
        self.assertAlmostEqual(v.reps[1].ext['course'], 360.0, delta = 0.00001)

    def test_repeated_values_fail_all_same(self):
        
        v = Voyage()
        for i in range(50): v.add_report(self.r1)
        v.find_repeated_values()
        for rep in v.reps:
            self.assertEqual(rep.repeated_value, 1)

    def test_repeated_values_pass(self):
        v = Voyage()
        for i in range(50): v.add_report(self.r1)
        for i in range(50): v.add_report(self.r2)
        v.find_repeated_values()
        for i, rep in enumerate(v.reps):
            self.assertEqual(rep.repeated_value, 0)

    def test_repeated_values_fail_mix(self):
        v = Voyage()
        for i in range(72): v.add_report(self.r1)
        for i in range(28): v.add_report(self.r2)
        v.find_repeated_values()
        for i, rep in enumerate(v.reps):
            if i <= 71: self.assertEqual(rep.repeated_value, 1)
            if i >= 72: self.assertEqual(rep.repeated_value, 0)


class TestQCMethods_getsst(unittest.TestCase):
    
    def setUp(self):
        sst_climatology_file = '/home/h04/hadjj/HadSST2_pentad_climatology.nc'
        climatology = Dataset(sst_climatology_file)
        self.sst = climatology.variables['sst'][:]

        mat_climatology_file = '/home/h04/hadjj/HadNMAT2_pentad_climatology.nc'
        climatology = Dataset(mat_climatology_file)
        self.mat = climatology.variables['nmat'][:]

        stdev_climatology_file = '/home/h04/hadjj/HadSST2_pentad_stdev_climatology.nc'
        climatology = Dataset(stdev_climatology_file)
        self.sdv = climatology.variables['sst'][:]

        self.dummyclim = np.full([73,180,360], 1.13)

    def test_stdev_is_none_at_pole(self):
        val =get_sst(89.9,0.0,1,1,self.sdv)
        self.assertEqual(val,None)

    def test_stdev_known_value(self):
        val =get_sst(-9.5,-179.5,1,1,self.sdv)
        self.assertAlmostEqual(val,2.19,delta=0.0001)
        val =get_sst(-10.5,-179.5,12,31,self.sdv)
        self.assertAlmostEqual(val,0.44,delta=0.0001)

    def test_north_pole_is_freezing_in_january(self):
        val = get_sst(89.9,0.0,1,1,self.sst)
        self.assertAlmostEqual(val,-1.8, delta=0.0001)

        val = get_sst(89.9,0.0,1,1,self.mat)
        self.assertAlmostEqual(val,   0, delta=0.0001)

    def test_known_value(self):
        val = get_sst(0.5,-179.5,1,1,self.sst)
        self.assertAlmostEqual(val,28.2904,delta=0.0001)
        val = get_sst(-0.5,-179.5,1,1,self.sst)
        self.assertAlmostEqual(val,28.4300,delta=0.0001)

        val = get_sst(0.5,-179.5,1,1,self.mat)
        self.assertAlmostEqual(val,27.4615,delta=0.0001)
        val = get_sst(-0.5,-179.5,1,1,self.mat)
        self.assertAlmostEqual(val,27.2693,delta=0.0001)

    def test_south_pole_is_missing(self):
        val = get_sst(-89.9,0.0,1,1,self.sst)
        self.assertEqual(val,None)

    def test_works_with_dummy_arrays(self):
        val = get_sst(0,0,1,1,self.dummyclim)
        self.assertEqual(val,1.13)

class TestQCMethods_julday(unittest.TestCase):
    
    def test_one_day_difference(self):
        j1 = jul_day(2001,1,1)
        j2 = jul_day(2001,1,2)
        self.assertEqual(1.0,j2-j1)

    def test_one_year_difference(self):
        j1 = jul_day(2001,1,1)
        j2 = jul_day(2002,1,1)
        self.assertEqual(365.0,j2-j1)

    def test_one_leapyear_difference(self):
        j1 = jul_day(2004,1,1)
        j2 = jul_day(2005,1,1)
        self.assertEqual(366.0,j2-j1)

class TestQCMethods_time_difference(unittest.TestCase):
    
    def test_missing_hour(self):
        timdif1 = time_difference(2000,1,7,None,2000,1,7,5)
        timdif2 = time_difference(2000,1,7,5,2000,1,7,None)
        timdif3 = time_difference(2000,1,7,None,2000,1,7,None)
        
        self.assertEqual(None,timdif1)
        self.assertEqual(None,timdif2)
        self.assertEqual(None,timdif3)
    
    def test_time_difference_one_hour(self):
        timdif = time_difference(2000,1,7,5,2000,1,7,6)
        self.assertAlmostEqual(1.0,timdif,delta=0.00001)
    
    def test_time_difference_same_time(self):
        timdif = time_difference(2000,1,7,5,2000,1,7,5)
        self.assertEqual(0.0,timdif)

    def test_time_difference_one_day(self):
        timdif = time_difference(2000,1,7,5,2000,1,8,5)
        self.assertAlmostEqual(24.0,timdif,delta=0.00001)

    def test_time_difference_minus_one_day(self):
        timdif = time_difference(2000,1,8,5,2000,1,7,5)
        self.assertAlmostEqual(-24.0,timdif,delta=0.00001)
        
    def test_time_difference_one_year(self):
        timdif = time_difference(2001,1,7,5,2002,1,7,5)
        self.assertEqual(8760.0,timdif)
      
    def test_time_difference_two_years(self):
        timdif = time_difference(2001,1,7,5,2003,1,7,5)
        self.assertEqual(17520.0,timdif)

    def test_time_difference_100_years(self):
        timdif = time_difference(1800,1,1,0,1900,1,1,0)
        self.assertEqual(876576.0,timdif)

class TestQCMethods_which_pentad(unittest.TestCase):
    
    def test_pentad_of_jan_1st(self):
        self.assertEqual(1,which_pentad(1,1))
    
    def test_pentad_of_dec_31st(self):
        self.assertEqual(73,which_pentad(12,31))
    
    def test_pentad_of_feb_29th(self):
        self.assertEqual(12,which_pentad(2,29))

class TestQCMethods_value_check(unittest.TestCase):
    
    def test_value_missing(self):
        self.assertEqual(1,value_check(None))
        
    def test_value_present(self):
        self.assertEqual(0,value_check(5.7))

class TestQCMethods_sst_freeze_check(unittest.TestCase):
    
    def test_exactly_freezing(self):
        self.assertEqual(0,sst_freeze_check(-1.80))
        self.assertEqual(0,sst_freeze_check(-1.80,0.0))
        self.assertEqual(0,sst_freeze_check(-1.80,0.0,-1.80))

    def test_above_freezing(self):
        self.assertEqual(0,sst_freeze_check(3.80))
        self.assertEqual(0,sst_freeze_check(3.80,0.0))
        self.assertEqual(0,sst_freeze_check(3.80,0.0,-1.80))

    def test_below_freezing(self):
        self.assertEqual(1,sst_freeze_check(-3.80))
        self.assertEqual(1,sst_freeze_check(-3.80,0.0))
        self.assertEqual(1,sst_freeze_check(-3.80,0.0,-1.80))

    def test_nonstandard_freezing_point(self):
        self.assertEqual(0,sst_freeze_check(-1.80,0.0,-1.90))
        self.assertEqual(1,sst_freeze_check(-2.00,0.0,-1.90))

class TestQCMethods_climatology_check(unittest.TestCase):
    
    def test_borderline(self):
        self.assertEqual(0,climatology_check(0.0,8.0))
    
    def test_negative_borderlines(self):
        self.assertEqual(0,climatology_check(0.0,-8.0))
    
    def test_should_pass(self):
        self.assertEqual(0,climatology_check(17.0,23.2))
        
    def test_should_fail(self):
        self.assertEqual(1,climatology_check(17.0,17.0+8.1))

    def test_should_fail_negative(self):
        self.assertEqual(1,climatology_check(17.0,17.0-8.1))
    
    def test_should_pass_with_limit(self):
        self.assertEqual(0,climatology_check(17.0,17.3,1.0))

    def test_should_fail_with_limit(self):
        self.assertEqual(1,climatology_check(17.0,17.3,0.2))
    
    def test_missing_climatology(self):
        self.assertEqual(1,climatology_check(20.0,None))

    def test_missing_value(self):
        self.assertEqual(1,climatology_check(None,7.3))
        
    def test_missing_limit(self):
        self.assertEqual(1,climatology_check(0.0,3.0,None))
    
class TestQCMethods_position_check(unittest.TestCase):
    
    def test_good_position(self):
        self.assertEqual(0,position_check(0.0, 0.0))

    def test_bad_latitudes(self):
        self.assertEqual(1,position_check( 91.0, 0.0))
        self.assertEqual(1,position_check(-91.0, 0.0))

    def test_bad_longitudes(self):
        self.assertEqual(1,position_check(0.0, -180.1))
        self.assertEqual(1,position_check(0.0,  360.1))

class TestQCMethods_dayinyear(unittest.TestCase):
    
    def test_jan1(self):
        self.assertEqual(1,dayinyear(1999,1,1))

    def test_dec31(self):
        self.assertEqual(365,dayinyear(1999,12,31))

    def test_dec31_leapyear(self):
        self.assertEqual(366,dayinyear(1984,12,31))

class TestQCMethods_winsorised_mean(unittest.TestCase):
    
    def test_all_zeroes(self):
        inarr = [0,0,0,0,0,0,0,0,0]
        self.assertEqual(0.0,winsorised_mean(inarr))

    def test_all_fours(self):
        inarr = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
        self.assertEqual(4.0,winsorised_mean(inarr))

    def test_three_fours(self):
        inarr = [4.0, 4.0, 4.0]
        self.assertEqual(4.0,winsorised_mean(inarr))

    def test_ascending(self):
        inarr = [3.,4.,5.]
        self.assertEqual(4.0,winsorised_mean(inarr))

    def test_longer_ascending_run(self):
        inarr = [1.,2.,3.,4.,5.,6.,7.]
        self.assertEqual(4.0,winsorised_mean(inarr))

    def test_longer_ascending_run_large_outlier(self):
        inarr = [1.,2.,3.,4.,5.,6.,700.]
        self.assertEqual(4.0,winsorised_mean(inarr))

    def test_longer_ascending_run_two_outliers(self):
        inarr = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,99.,1000.]
        self.assertEqual(8.5,winsorised_mean(inarr))

class TestQCMethods_trimmed_mean(unittest.TestCase):
    
    def test_all_zeroes(self):
        inarr = [0,0,0,0,0,0,0,0,0]
        trim = 10
        self.assertEqual(0.0,trimmed_mean(inarr,trim))

    def test_all_zeroes_one_outlier_trimmed(self):
        inarr = [0,0,0,0,0,0,0,0,0,10.0]
        trim = 4
        self.assertEqual(0.0,trimmed_mean(inarr,trim))
        
    def test_all_zeroes_one_outlier_not_trimmed(self):
        inarr = [0,0,0,0,0,0,0,0,0,10.0]
        trim = 50
        self.assertEqual(1.0,trimmed_mean(inarr,trim))

    def test_trim_zero(self):
        inarr = [1.3,0.7,4.0]
        trim = 0
        self.assertEqual(2.0,trimmed_mean(inarr,trim))

class TestQCMethods_lat_to_yindex(unittest.TestCase):
    
    def test_latitude_too_high(self):
        self.assertEqual(0,lat_to_yindex(99.2))
    
    def test_borderline37(self):
        self.assertEqual(53,lat_to_yindex(37.00))
    
    def test_latitude_too_low(self):
        self.assertEqual(179,lat_to_yindex(-199.3))
    
    def test_borderline(self):
        for i in range(0,180):
            self.assertEqual(i,lat_to_yindex(90-i))

    def test_gridcentres(self):
        for i in range(0,180):
            self.assertEqual(i,lat_to_yindex(90-i-0.5))

class TestQCMethods_lon_to_xindex(unittest.TestCase):
    
    def test_borderline(self):
        self.assertEqual(0,lon_to_xindex(-180))
        self.assertEqual(0,lon_to_xindex(180))

    def test_non180_borderline(self):
        self.assertEqual(106,lon_to_xindex(-74.0))

    def test_gridcentres(self):
        self.assertEqual(0,lon_to_xindex(-179.5))
        self.assertEqual(0,lon_to_xindex(180.5))

    def test_highlong(self):
        self.assertEqual(179, lon_to_xindex(359.5))

    def test_lons_ge_180(self):
        '''test to make sure wrapping works'''
        self.assertEqual(180, lon_to_xindex(360.0))
        self.assertEqual(5,lon_to_xindex(185.1))
        for i in range(0,520):
            self.assertEqual(math.fmod(i,360),lon_to_xindex(-179.5+float(i)))

class TestQCMethods_blacklist(unittest.TestCase):
    
    def test_obvious_pass(self):
        result = blacklist(None, 732, 1850, 0, 0)
        self.assertEqual(result,0)

    def test_obvious_fails(self):
        result = blacklist(None, 732, 1958, 45, -172)
        self.assertEqual(result,1)
        result = blacklist(None, 732, 1974, -47, -60)
        self.assertEqual(result,1)

    def test_right_area_wrong_callsign_passes(self):
        result = blacklist(None, 731, 1958, 45, -172)
        self.assertEqual(result,0)
        result = blacklist(None, 731, 1974, -47, -60)
        self.assertEqual(result,0)

    def test_right_area_wrong_year_passes(self):
        result = blacklist(None, 732, 1957, 45, -172)
        self.assertEqual(result,0)
        result = blacklist(None, 732, 1975, -47, -60)
        self.assertEqual(result,0)

class TestQCMethods_sunangle(unittest.TestCase):
#sunangle(year,day,hour,min,sec,zone,dasvtm,lat,lon)
    def test_looking_through_window(self):
        '''test devised by looking through the window at the sun resting on the horizon at 07:45 15 October 2015'''
        day = dayinyear(2015,10,15)
        a,e,rta,hra,sid,dec = sunangle(2015,day,7.,40.,0,0,1,50.7365,-3.5344)
        self.assertAlmostEqual(0,e,delta=5.00)

    def test_sunrise_summer_solstice_2016_exeter(self):
        day = dayinyear(2016,6,20)
        a,e,rta,hra,sid,dec = sunangle(2016,day,5,1,0,0,1,50.7365,-3.5344)
        self.assertAlmostEqual(0,e,delta=1.5)

    def test_sunrise_in_Lima_March_3_1996(self):
        day = dayinyear(1996,3,3)
        a,e,rta,hra,sid,dec = sunangle(1996,day,6,11,0,5,0,-12.0433,-77.0283)
        self.assertAlmostEqual(0,e,delta=1.5)

    def test_sunset_in_Zanzibar_City_Jan_31_1995(self):
        day = dayinyear(1995,1,31)
        a,e,rta,hra,sid,dec = sunangle(1995,day,18,17,0,21.38,0,-6.1658,39.1992)
        self.assertAlmostEqual(0,e,delta=1.5)

class TestQCMethods_day_test(unittest.TestCase):
        #result = day_test(year,month,day,hour,lat,lon)
    def test_looking_through_window_plus_an_hour_sunup(self):
        result = day_test(2015,10,15,7.8000,50.7365,-3.5344)
        self.assertEqual(1,result)
        
    def test_looking_through_window_plus_an_hour_sunstilldown(self):
        result = day_test(2015,10,15,7.5000,50.7365,-3.5344)
        self.assertEqual(0,result)



if __name__ == '__main__':
    unittest.main()
