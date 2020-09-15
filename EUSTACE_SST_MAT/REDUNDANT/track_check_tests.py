import unittest
import qc
from spherical_geometry import *
from qc_track_check import *
from netCDF4 import Dataset

class TestQCMethods_xdist(unittest.TestCase):

  def test_xdist_identical_start_and_end(self):
      a,b,c = xdist(0.0,0.0,0.0,0.0)
      self.assertEqual(0.0,a)
      self.assertEqual(0.0,b)
      self.assertEqual(0.0,c)

  def test_xdist_pole_to_pole(self):
      a,b,c = xdist(-90.0,0.0,90.0,0.0)
      self.assertEqual(10800.,a)
      self.assertEqual(10800.,b)
      self.assertEqual(0.0,c)

  def test_xdist_equator(self):
      a,b,c = xdist(0.0,0.0,0.0,180.0)
      self.assertEqual(10800.,a)
      self.assertEqual(0.0,b)
      self.assertEqual(10800.,c)

  def test_xdist_small_longitude_step(self):
      a,b,c = xdist(0.0,2.5,0.0,-2.5)
      self.assertEqual(10800./36,a)
      self.assertEqual(0.0,b)
      self.assertEqual(10800./36,abs(c))

  def test_colins_test(self):
      a,b,c = xdist(0.0,0.0,0.0,5.0)
      a = a * 36
      self.assertEqual(10800.,a)

class TestTrackQCMethods_increment_position(unittest.TestCase):
#increment_position(alat1,alat2,avs,ads,timdif)
    def test_ship_heading_north_at_60knots_goes1degree_in_1hour(self):
        '''
        A ship travelling north at 60 knots will go 1 degree in 1 hour
        '''
        for lat in range(-90,90):
            alat1 = lat
            alat2 = lat
            avs = 60.0
            ads = 0.0
            timdif = 2.0
            aud1,avd1 = increment_position(alat1,alat2,avs,ads,timdif)
            self.assertAlmostEqual(avd1,0,delta=0.000001)
            self.assertAlmostEqual(aud1,1,delta=0.000001)

    def test_ship_heading_east_at_60knots_goes1degree_in_1hour(self):
        '''
        A ship travelling east at 60 knots will go 1 degree in 1 hour
        '''
        alat1 = 0.0
        alat2 = 0.0
        avs = 60.0
        ads = 90.0
        timdif = 2.0
        aud1,avd1 = increment_position(alat1,alat2,avs,ads,timdif)
        self.assertAlmostEqual(avd1,1,delta=0.000001)
        self.assertAlmostEqual(aud1,0,delta=0.000001)

    def test_ship_heading_east_at_60knots_at_latitude60_goes2degrees_in_1hour(self):
        '''
        A ship travelling east at 60 knots will go 2 degrees in 1 hour at 60N
        '''
        alat1 = 60.0
        alat2 = 60.0
        avs = 60.0
        ads = 90.0
        timdif = 2.0
        aud1,avd1 = increment_position(alat1,alat2,avs,ads,timdif)
        self.assertAlmostEqual(avd1,2,delta=0.000001)
        self.assertAlmostEqual(aud1,0,delta=0.000001)

    def test_ship_goes_southwest(self):
        alat1 = 0.0
        alat2 = 0.0
        avs = 60.0
        ads = 225.0
        timdif = 2.0
        aud1,avd1 = increment_position(alat1,alat2,avs,ads,timdif)
        self.assertAlmostEqual(avd1,-1./np.sqrt(2),delta=0.000001)
        self.assertAlmostEqual(aud1,-1./np.sqrt(2),delta=0.000001)

class TestTrackQCMethods_speed1(unittest.TestCase):
    
    def test_zero_speed(self):
        shpspd, shpdis, shpdir, side1, side2 = speed1(33.0,33.0,159.0,159.0,33.0)
        self.assertEqual(0.0,shpspd)

    def test_direction_for_zero_speed(self):
        shpspd, shpdis, shpdir, side1, side2 = speed1(33.0,33.0,159.0,159.0,33.0)
        self.assertEqual(None,shpdir)

    def test_direction_for_due_north(self):
        shpspd, shpdis, shpdir, side1, side2 = speed1(33.0,34.0,159.0,159.0,33.0)
        self.assertAlmostEqual(0.0,shpdir,delta=0.01)

    def test_direction_for_due_northeast(self):
        shpspd, shpdis, shpdir, side1, side2 = speed1(-1,1,2,4,3.0)
        self.assertAlmostEqual(45.0,shpdir,delta=0.01)

    def test_direction_for_due_northwest(self):
        shpspd, shpdis, shpdir, side1, side2 = speed1(-1,1,4,2,3.0)
        self.assertAlmostEqual(315.0,shpdir,delta=0.01)

    def test_direction_for_due_southhwest(self):
        shpspd, shpdis, shpdir, side1, side2 = speed1(1,-1,4,2,3.0)
        self.assertAlmostEqual(225.0,shpdir,delta=0.0001)

class TestTrackQCMethods_modesp(unittest.TestCase):
    
    def test_noinput(self):
        m = modesp([])
        self.assertEqual(None, m)
        
    def test_one_input(self):
        m = modesp([17.0])
        self.assertEqual(None, m)

    def test_single_speed_input_over8point5(self):
        m = modesp([20.0,20.0,20.0,20.0,20.0,20.0])
        self.assertEqual(19.5,m)

    def test_single_speed_input_under8point5(self):
        m = modesp([2.0,2.0,2.0,2.0,2.0,2.0])
        self.assertEqual(8.5,m)

    def test_single_speed_input_overmaximum(self):
        m = modesp([200.0,200.0,200.0,200.0,200.0,200.0])
        self.assertEqual(34.5,m)

    def test_one_of_each_speed_input_min_under8point5(self):
        m = modesp(range(1,20))
        self.assertEqual(8.5,m)

class TestTrackQCMethods_1step_speeds(unittest.TestCase):

    def setUp(self):
        self.trip1 = []
        self.speed1 = 18.
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))

    def test_1step_speed_first_entry_missing(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        self.assertEqual(None, speeds[0])
        
    def test_1step_speed_speeds(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        self.assertAlmostEqual(self.speed1, speeds[1],delta=0.00001)
        
    def test_1step_speed_time_differences(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        self.assertAlmostEqual(1.0, time_differences[1],delta=0.00001)

    def test_1step_speed_distances(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        self.assertAlmostEqual(self.speed1, distances[1],delta=0.00001)
    
    def test_1step_speed_directions(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        self.assertAlmostEqual(0.0,ship_directions[1],delta=0.01)

    def test_1step_speed_noinput(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds([])
        self.assertEqual([],time_differences)

class TestTrackQCMethods_alternate_step_speeds(unittest.TestCase):
#time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds(inreps)
    def setUp(self):
        #trip1 is ship travelling north from equator at 18 knots - vs = 4 and ds = 8
        self.trip1 = []
        self.speed1 = 18.
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
 
    def test_alternate_step_speed_first_entry_missing(self):
        time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds(self.trip1)
        self.assertEqual(None, speeds[0])
        
    def test_alternate_step_speed_speeds(self):
        time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds(self.trip1)
        self.assertAlmostEqual(self.speed1, speeds[1],delta=0.00001)
        
    def test_alternate_step_speed_time_differences(self):
        time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds(self.trip1)
        self.assertAlmostEqual(2.0, time_differences[1],delta=0.00001)

    def test_alternate_step_speed_distances(self):
        time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds(self.trip1)
        self.assertAlmostEqual(2.0*self.speed1, distances[1],delta=0.00001)
    
    def test_alternate_step_speed_directions(self):
        time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds(self.trip1)
        self.assertAlmostEqual(0.0,ship_directions[1],delta=0.01)

    def test_alternate_step_speed_noinput(self):
        time_differences,speeds,distances,ship_directions = calc_alternate_step_speeds([])
        self.assertEqual([],time_differences)
    
class TestTrackQCMethods_distr1(unittest.TestCase):
    
    def setUp(self):
        self.trip1 = []
        self.speed1 = 18.
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))

        self.trip2 = []
        self.speed1 = 18.
        for hour in range(0,3):
           self.trip2.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
        self.trip2[1].lon = 1.0

    def test_first_entry_missing(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        difference_from_estimated_location = distr1(self.trip1,time_differences)
        self.assertEqual(difference_from_estimated_location[0],None)

    def test_ship_is_at_computed_location(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        difference_from_estimated_location = distr1(self.trip1,time_differences)
        for i, diff in enumerate(difference_from_estimated_location):
            if i > 0 and i < len(difference_from_estimated_location)-1:
                self.assertAlmostEqual(diff,0,delta=0.00001)

    def test_misplaced_ob_out_by_1degree_times_coslat(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip2)
        difference_from_estimated_location = distr1(self.trip2,time_differences)
        self.assertAlmostEqual(difference_from_estimated_location[1],60.*np.cos(self.trip2[1].lat*np.pi/180.),delta=0.00001)
       
class TestTrackQCMethods_distr2(unittest.TestCase):
    
    def setUp(self):
        self.trip1 = []
        self.speed1 = 18.
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))

        self.trip2 = []
        self.speed1 = 18.
        for hour in range(0,3):
           self.trip2.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
        self.trip2[1].lon = 1.0

    def test_last_entry_missing(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        difference_from_estimated_location = distr2(self.trip1,time_differences)
        self.assertEqual(difference_from_estimated_location[-1],None)

    def test_ship_is_at_computed_location(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        difference_from_estimated_location = distr2(self.trip1,time_differences)
        for i, diff in enumerate(difference_from_estimated_location):
            if i > 0 and i < len(difference_from_estimated_location)-1:
                self.assertAlmostEqual(diff,0,delta=0.00001)

    def test_misplaced_ob_out_by_1degree_times_coslat(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip2)
        difference_from_estimated_location = distr2(self.trip2,time_differences)
        self.assertAlmostEqual(difference_from_estimated_location[1],60.*np.cos(self.trip2[1].lat*np.pi/180.),delta=0.00001)
       
class TestTrackQCMethods_midpt(unittest.TestCase):
    #midpoint_discrepancies = midpt(inreps,time_differences)
    def setUp(self):
        self.trip1 = []
        self.speed1 = 18.
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))

        self.trip2 = []
        self.speed1 = 18.
        for hour in range(0,3):
           self.trip2.append(qc.MarineReport('SHIP1    ',hour*self.speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
        self.trip2[1].lon = 1.0

    def test_first_and_last_are_missing(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        midpoint_discrepancies = midpt(self.trip1,time_differences)
        self.assertEqual(midpoint_discrepancies[0],None)
        self.assertEqual(midpoint_discrepancies[-1],None)
    
    def test_midpt_1_deg_error_out_by_60coslat(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip2)
        midpoint_discrepancies = midpt(self.trip2,time_differences)
        self.assertAlmostEqual(midpoint_discrepancies[1],60.*math.cos(self.trip2[1].lat*np.pi/180),delta=0.00001)

    def test_midpt_at_computed_location(self):
        time_differences,speeds,distances,ship_directions = calc_1step_speeds(self.trip1)
        midpoint_discrepancies = midpt(self.trip1,time_differences)
        for i,pt in enumerate(midpoint_discrepancies):
            if i > 0 and i < len(midpoint_discrepancies)-1:
                self.assertNotEqual(pt,None,'Failed at '+str(i)+' out of '+str(len(midpoint_discrepancies)))
                self.assertAlmostEqual(pt,0,msg='Failed at '+str(i)+' with mid point = '+str(pt),delta=0.00001)

class TestTrackQCMethods_direction_continuity(unittest.TestCase):
#result = direction_continuity(dsi,dsi_previous,ship_directions)
    def test_just_pass_and_just_fail(self):
        for angle in [0,45,90,135,180,225,270,315,360]:
            self.assertEqual(10, direction_continuity(angle,angle,angle+60.1))
            self.assertEqual( 0, direction_continuity(angle,angle,angle+59.9))

class TestTrackQCMethods_speed_continuity(unittest.TestCase):

    def test_1(self):
        result = speed_continuity(12,12,12)
        self.assertEqual(0,result)
    
    def test_just_fails(self):
        result = speed_continuity(12,12,12+10.01)
        self.assertEqual(10,result)
    
    def test_just_passes(self):
        result = speed_continuity(12,12,12+9.99)
        self.assertEqual(0,result)

    def test_input_speed_is_None(self):
        result = speed_continuity(12,12,None)
        self.assertEqual(0,result)

class TestQCMethods_track_check(unittest.TestCase):

    def setUp(self):

        self.trip1 = [] # ship travelling north from 0lat0lon at 18 knots taking hourly obs
        self.trip2 = [] # ship travelling north from 0lat0lon at 18 knots taking hourly obs with one misplaced ob
        self.generic_id = [] #ship with generic ID
        self.all_pass = [] # array of zeroes to compare QC outcomes to
        self.some_fail = [] # array of zeroes and one one at time of misplaced ob
                
        speed1 = 18.
        
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport(     'SHIP1    ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
            self.trip2.append(qc.MarineReport(     'SHIP1    ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
            self.generic_id.append(qc.MarineReport('SHIP     ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
            self.all_pass.append(0)
            self.some_fail.append(0)
        
        #trip2 has one bad longitude at the 12th time step
        self.trip2[12].lon = 3.0
        self.some_fail[12] = 1
 
 #Route of the Titanic (sort of).
        self.titanic = []  #titanic sailed from Queenstown (now Cobh) to NewYork
        #Cobh 51.851 N 8.2967 W according to Wikipedia
        lat1 = 51.851
        lon1 = -8.2967
        #New Yoik 40.7127 N, 74.0059 W according to Google
        lat2 = 40.7127
        lon2 = -74.0059
        
        for f in range(0,24):
            lat,lon = intermediate_point(lat1,lon1,lat2,lon2,f/23.)
            self.titanic.append(qc.MarineReport('TITANIC  ',lat,lon,None,None,1912,4,10,hour,8,4,'UIDFORSHIP1'))


    def test_no_obs(self):
        qcs = mds_track_check([])
        self.assertListEqual([],qcs)

    def test_generic_id(self):
        qcs = mds_track_check(self.generic_id)
        self.assertListEqual(self.all_pass,qcs)

    def test_speed(self):
        self.assertEqual(360,self.trip1[0].dsi)
        self.assertEqual(18,self.trip1[0].vsi)

    def test_track_check(self):
        qcs = mds_track_check(self.trip1)
        self.assertListEqual(self.all_pass,qcs)

    def test_track_check_reports(self):
        qcs = mds_track_check(self.trip1)
        for rep in self.trip1:
            self.assertEqual(0,rep.bad_track)

    def test_track_check_fail(self):
        qcs = mds_track_check(self.trip2)
        self.assertListEqual(self.some_fail,qcs)

    def test_track_check_fail_reports(self):
        qcs = mds_track_check(self.trip2)
        for i in range(0,24):
            if i != 12:
                self.assertEqual(0,self.trip2[i].bad_track)
            else:
                self.assertEqual(1,self.trip2[i].bad_track)
        self.assertEqual(1,self.trip2[12].bad_track)

class TestQCMethods_full_track_check(unittest.TestCase):

    def setUp(self):
        
        #Trip 0 is the February 1850 part of the voyage of the VANDALIA, or, should I say, VANDALIA*s* - it appears there was 
        #more than one. The lats, lons, days and failures are as reported in MDS2. The sole difference is that MDS2 always 
        #failed the first ob, but here we accept it.
        lats=             [ 34.3, -20.0,  34.2, -17.3,  34.5, -15.3,  35.2, -13.3,  35.7, -13.1,  36.0,  36.1,  35.4,  33.2,  34.7,  34.2,  34.5,  35.5,  35.7,  36.7,  34.8,  32.7,  32.5,  31.3,  28.0,  25.2,  23.0,  21.0,  18.7, -11.0,  15.7, -10.8,  12.3,  -9.8,   9.7,  -9.1,   7.3,  -8.3]
        lons=             [-61.7, -75.2, -59.4, -75.7, -56.6, -76.2, -53.3, -77.0, -49.9, -77.1, -48.0, -44.7, -43.4, -42.0, -40.7, -39.8, -39.0, -37.0, -34.4, -31.3, -32.7, -32.5, -32.3, -31.3, -29.7, -29.3, -28.5, -27.7, -26.9, -79.6, -26.4, -79.7, -26.6, -82.2, -26.6, -84.2, -26.5, -86.3]
        day =             [    1,     1,     2,     2,     3,     3,     4,     4,     5,     5,     6,      7,    8,     9,    10,    11,    12,    13,    14,    15,    16,    17,    18,    19,    20,    21,    22,    23,    24,    24,    25,    25,    26,    26,    27,    27,    28,    28]
        self.trip0fails = [    0,     1,     1,     1,     1,     1,     1,     1,     1,     1,     0,      0,    0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1,     1,     1,     1,     1,     1,     1,     1,     0]
        self.trip0 = [] 
        for i in range(0,len(lats)):
            self.trip0.append(qc.MarineReport('VANDALIA ', lats[i], lons[i], None,None,1850,2,day[i],0,None,None,'UIDFORSHIP1'))
        assert len(lats) == len(lons) and len(day) == len(lons) and len(self.trip0fails) == len(lons)
        
        self.trip1 = [] # ship travelling north from 0lat0lon at 18 knots taking hourly obs
        self.trip2 = [] # ship travelling north from 0lat0lon at 18 knots taking hourly obs with one misplaced ob
        self.trip3 = [] # ship travelling north from 0lat0lon at 18 knots taking hourly obs with five misplaced obs
        self.generic_id = [] #ship with generic ID
        self.all_pass = [] # array of zeroes to compare QC outcomes to
        self.some_fail = [] # array of zeroes and one one at time of misplaced ob
        self.lots_fail = [] # array of zeroes and one one at time of misplaced ob
                
        speed1 = 18.
        
        for hour in range(0,24):
            self.trip1.append(qc.MarineReport(     'SHIP1    ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
            self.trip2.append(qc.MarineReport(     'SHIP1    ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
            self.trip3.append(qc.MarineReport(     'SHIP1    ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))

            self.generic_id.append(qc.MarineReport('SHIP     ',hour*speed1/60.,0.0,None,None,2001,1,1,hour,8,4,'UIDFORSHIP1'))
            
            self.all_pass.append(0)
            self.some_fail.append(0)
            self.lots_fail.append(0)
        
        #trip2 has one bad longitude at the 12th time step
        self.trip2[12].lon = 3.0
        self.some_fail[12] = 1

        #trip 3 has a sequence of bad longitudes
        for i in range(12,15):
            self.trip3[i].lon = 10.0
        for i in range(12,17):
            self.lots_fail[i] = 1

    def test_no_obs(self):
        qcs = mds_full_track_check([])
        self.assertListEqual([],qcs)

    def test_generic_id(self):
        qcs = mds_full_track_check(self.generic_id)
        self.assertListEqual(self.all_pass,qcs)

    def test_speed(self):
        self.assertEqual(360,self.trip1[0].dsi)
        self.assertEqual(18,self.trip1[0].vsi)

    def test_full_track_check(self):
        qcs = mds_full_track_check(self.trip1)
        self.assertListEqual(self.all_pass,qcs)

    def test_full_track_check_reports(self):
        qcs = mds_full_track_check(self.trip1)
        for rep in self.trip1:
            self.assertEqual(0,rep.bad_track)

    def test_full_track_check_fail(self):
        qcs = mds_full_track_check(self.trip2)
        self.assertListEqual(self.some_fail,qcs)

    def test_full_track_check_fail_multiple(self):
        qcs = mds_full_track_check(self.trip3)
        self.assertListEqual(self.lots_fail,qcs)

    def test_full_track_check_fail_reports_multiple(self):
        qcs = mds_full_track_check(self.trip3)
        for i in range(0,24):
            self.assertEqual(self.lots_fail[i],self.trip3[i].bad_track,"Failed at "+str(i))

    def test_full_track_check_fail_reports(self):
        qcs = mds_full_track_check(self.trip2)
        for i in range(0,24):
            if i != 12:
                self.assertEqual(0,self.trip2[i].bad_track)
            else:
                self.assertEqual(1,self.trip2[i].bad_track)
        self.assertEqual(1,self.trip2[12].bad_track)

    def test_VANDALIA_fails_as_MDS2(self):
        qcs = mds_full_track_check(self.trip0)
        self.assertListEqual(qcs,self.trip0fails)

if __name__ == '__main__':
    unittest.main()
