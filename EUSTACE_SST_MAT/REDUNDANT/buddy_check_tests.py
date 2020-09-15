import unittest
from spherical_geometry import *
from qc import *
from qc_buddy_check import *
from netCDF4 import Dataset

class TestQCMethods_gridpt(unittest.TestCase):
    
    def test_equality(self):
        g1 = Gridpt(24.2, -171.8, 2003, 12, 28)
        g2 = Gridpt(24.3, -171.9, 2003, 12, 27)
        self.assertEqual(g1,g2)

    def test_non_equality(self):
        g1 = Gridpt(24.2, -171.8, 2003, 11, 28)
        g2 = Gridpt(24.3, -171.9, 2003, 12, 27)
        self.assertNotEqual(g1,g2)

    def test_equal_gridpts_hash_for_each_other(self):
        g1 = Gridpt(24.2, -171.8, 2003, 12, 28)
        g2 = Gridpt(24.3, -171.9, 2003, 12, 27)
        dic = {}
        dic[g2] = 12
        self.assertIn(g1,dic)

class TestQCMethods_grid_super_obs(unittest.TestCase):
#anoms_by_grid = grid_super_obs(reps, type)

    def test_grid_one_ob(self):
        for type in ['SST','AT']:
            badob = MarineReport('',89.5,-179.5,30.0,30.0,2005,1,1,12,None,None,'')
            badob.setnorm(28.0,28.0)
            anoms_by_grid = grid_super_obs([badob],type)
        
            self.assertEqual(len(anoms_by_grid),1,"Something other than one grid cell")
            for key in anoms_by_grid:
                self.assertEqual(anoms_by_grid[key][0], 2.0, "Anomaly incorrect: is "+str(anoms_by_grid[key][0])+' should be 2')
                self.assertEqual(anoms_by_grid[key][1], 1.0, "Number of obs incorrect: is "+str(anoms_by_grid[key][1])+' should be 1')

    def test_grid_two_near_identical_obs_in_different_grid_boxes(self):
        badob1 = MarineReport('',0.0,0.0,30.0,30.0,2005,1,1,12,None,None,'')  #at 0N,0E
        badob1.setnorm(28.0,28.0)
        badob2 = MarineReport('',0.01,0.0,30.0,30.0,2005,1,1,12,None,None,'') #at 0.01N and 0E
        badob2.setnorm(28.0,28.0)
        anoms_by_grid = grid_super_obs([badob1,badob2],'SST')
        self.assertEqual(len(anoms_by_grid),2,"Something other than two grid cells occupied")
        for key in anoms_by_grid:
            self.assertEqual(anoms_by_grid[key][0], 2.0, "Anomaly incorrect: is "+str(anoms_by_grid[key][0])+' should be 2')
            self.assertEqual(anoms_by_grid[key][1], 1.0, "Number of obs incorrect: is "+str(anoms_by_grid[key][1])+' should be 1')

    def test_grid_two_identical_obs(self):
        badob = MarineReport('',89.5,-179.5,30.0,30.0,2005,1,1,12,None,None,'')
        badob.setnorm(28.0,28.0)
        anoms_by_grid = grid_super_obs([badob,badob],'SST')
        
        self.assertEqual(len(anoms_by_grid),1,"Something other than one grid cell")
        for key in anoms_by_grid:
            self.assertEqual(anoms_by_grid[key][0], 2.0, "Anomaly incorrect: is "+str(anoms_by_grid[key][0])+' should be 2')
            self.assertEqual(anoms_by_grid[key][1], 2.0, "Number of obs incorrect: is "+str(anoms_by_grid[key][1])+' should be 2')
    
    @unittest.skip("Skipping the slow test")
    def test_fill_whole_grid(self):
        '''slow test'''
        badobs = []
        for lon in range(0,360):
            for lat in range(0,180):
                badob = MarineReport('',-89.5+lat,-179.5+lon,30.0,30.0,2005,1,1,12,None,None,'')
                badob.setnorm(28.0,28.0)
                badobs.append(badob)
        anoms_by_grid = grid_super_obs(badobs,'SST')
        self.assertEqual(len(anoms_by_grid),360*180,"Something other than 360*180 grid cells filled")
        for key in anoms_by_grid:
            self.assertEqual(anoms_by_grid[key][0], 2.0, "Anomaly incorrect: is "+str(anoms_by_grid[key][0])+' should be 2')
            self.assertEqual(anoms_by_grid[key][1], 1.0, "Number of obs incorrect: is "+str(anoms_by_grid[key][1])+' should be 2')

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

    def test_longer_descending_run_two_outliers(self):
        inarr = [1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,99.,1000.]
        inarr = inarr[::-1]
        self.assertEqual(8.5,winsorised_mean(inarr))

class TestQCMethods_get_neighbours(unittest.TestCase):
    
    def test_longitude_borderline_of_grid_sent_east(self):
        '''point on borderline between grid points should be sent east'''
        g = Gridpt(0.5, 0.0, 2015,5,21)
        result = g.get_neighbours(1,1,1)
        g2 = Gridpt(0.5, 1.5, 2015,5,21)
        self.assertIn(g2,result)

    def test_latitude_borderline_of_grid_sent_south(self):
        '''point on borderline between grid points should be sent east'''
        g  = Gridpt(0.0, 0.5, 2015,5,21)
        result = g.get_neighbours(1,1,1)
        g2 = Gridpt(-1.5, 0.5, 2015,5,21)
        self.assertIn(g2,result)
       
    def test_near_equator_has_26_neighbours_within_1x1x1(self):
        '''a grid cell near the equator should have 3x3x3-1 neighbours within 1degree lat 1degree long and 1 pentad'''
        g = Gridpt(0.5,0.5,2015,1,1)
        result = g.get_neighbours(1,1,1)
        self.assertEqual(26,len(result))
        g = Gridpt(0.5,0.5,2015,12,31)
        result = g.get_neighbours(1,1,1)
        self.assertEqual(26,len(result))

    def test_near_equator_has_124_neighbours_within_2x2x2(self):
        '''a grid cell near the equator should have 5x5x5-1 neighbours within 2degree lat 2degree long and 2 pentads'''
        g = Gridpt(0.5,0.5,2015,1,1)
        result = g.get_neighbours(2,2,2)
        self.assertEqual(124,len(result))

    def test_near_equator_has_80_neighbours_within_1x1x4(self):
        '''a grid cell near the equator should have 3x3x9-1 neighbours within 1degree lat 1degree long and 4 pentads'''
        g = Gridpt(0.5,0.5,2015,1,1)
        result = g.get_neighbours(1,1,4)
        self.assertEqual(80,len(result))

    def test_mid_year_pentads_work(self):
        g = Gridpt(0.5, 0.5, 2015,5,21)
        result = g.get_neighbours(1,1,1)
        g2 = Gridpt(0.5, 0.5, 2015,5,26)
        self.assertIn(g2,result)

    def test_jan_1_gridpt_has_neighbour_in_dec(self):
        g = Gridpt(0.5, 0.5, 2015,1,1)
        result = g.get_neighbours(1,1,1)
        g2 = Gridpt(0.5, 0.5, 2014,12,31)
        self.assertIn(g2,result)

    def test_dec_31_gridpt_has_neighbour_in_jan(self):
        g = Gridpt(0.5, 0.5, 2015,12,31)
        result = g.get_neighbours(1,1,1)
        g2 = Gridpt(0.5, 0.5, 2016,1,1)
        self.assertIn(g2,result)
  
    def test_gridpt_is_not_neighbour_with_itself(self):
        g = Gridpt(0.5, 0.5, 2015,12,31)
        result = g.get_neighbours(1,1,1)
        self.assertNotIn(g,result)

    def test_gridpt_is_not_neighbour_with_mildly_distant_gridpt(self):
        '''if we are searching within 1 degree only, we would not expect there to be a neighbour which is 2 degrees away'''
        g = Gridpt(0.5, 0.5, 2015,1,1)
        result = g.get_neighbours(1,1,1)
        g2 = Gridpt(0.5, 2.5, 2015,1,1)
        self.assertNotIn(g2,result)

    def test_more_neighbours_at_60N(self):
        '''At 60N the longitudinal search radius is double what it is at the equator, so expect 5x3x3-1 = 44 neighbours'''
        g = Gridpt(60.5,0.5,2015,1,1)
        result = g.get_neighbours(1,1,1)
        self.assertEqual(44,len(result))

class TestQCMethods_get_neighbour_anomalies(unittest.TestCase):
#get_neighbour_anomalies(search_radius,key,anoms_by_grid)

    def setUp(self):
        self.search_ranges = [[1,1,2],[1,1,4],[2,2,2],[2,2,4]] 

    def test_one_pair_of_neighbours_in_dec(self):
        
        ob1 = MarineReport('',0.5,0.5,30.0,30.0,2004,12,25,12,None,None,'')  #at 0N,0E
        ob1.setnorm(28.0,28.0)
        ob2 = MarineReport('',0.5,0.5,30.0,30.0,2004,12,31,12,None,None,'') #at 0.01N and 0E
        ob2.setnorm(28.0,28.0)
        anoms_by_grid = grid_super_obs([ob1,ob2],'SST')

        for key in anoms_by_grid:
            for search in self.search_ranges:
                temp_anom, temp_nobs = get_neighbour_anomalies(search,key,anoms_by_grid)
                self.assertEqual(temp_anom[0],2.0)
                self.assertEqual(temp_nobs[0],1.0)
                self.assertEqual(len(temp_anom),1)
                self.assertEqual(len(temp_nobs),1)
       

    def test_one_pair_of_neighbours(self):
        
        ob1 = MarineReport('',0.5,0.5,30.0,30.0,2005,1,1,12,None,None,'')  #at 0N,0E
        ob1.setnorm(28.0,28.0)
        ob2 = MarineReport('',0.5,0.5,30.0,30.0,2004,12,31,12,None,None,'') #at 0.01N and 0E
        ob2.setnorm(28.0,28.0)
        anoms_by_grid = grid_super_obs([ob1,ob2],'SST')

        for key in anoms_by_grid:
            for search in self.search_ranges:
                temp_anom, temp_nobs = get_neighbour_anomalies(search,key,anoms_by_grid)
                self.assertEqual(temp_anom[0],2.0)
                self.assertEqual(temp_nobs[0],1.0)
                self.assertEqual(len(temp_anom),1)
                self.assertEqual(len(temp_nobs),1)

    def test_one_pair_of_very_distant_neighbours(self):
        
        ob1 = MarineReport('',3.5,0.5,30.0,30.0,2005,1,1,12,None,None,'')  #at 0N,0E
        ob1.setnorm(28.0,28.0)
        ob2 = MarineReport('',0.5,0.5,30.0,30.0,2004,12,31,12,None,None,'') #at 0.01N and 0E
        ob2.setnorm(28.0,28.0)
        anoms_by_grid = grid_super_obs([ob1,ob2],'SST')
        for key in anoms_by_grid:
            for search in self.search_ranges:
                temp_anom, temp_nobs = get_neighbour_anomalies(search,key,anoms_by_grid)
                self.assertEqual(len(temp_anom),0)
                self.assertEqual(temp_anom,[])
                self.assertEqual(len(temp_nobs),0)
                self.assertEqual(temp_nobs,[])

class TestQCMethods_get_threshold_multiplier(unittest.TestCase):

#multiplier = get_threshold_multiplier(total_nobs,nob_limits,multiplier_values)
    def test_nobs_limits_not_ascending(self):
        with self.assertRaises(AssertionError):
            multiplier = get_threshold_multiplier(0,[10,5,0],[4,3,2])

    def test_lowest_nobs_limit_not_zero(self):
        with self.assertRaises(AssertionError):
            multiplier = get_threshold_multiplier(1,[1,5,10],[4,3,2])
        
    def test_simple(self):
        for n in range(1,20):
            multiplier = get_threshold_multiplier(n,[0,5,10],[4,3,2])
            if n >=1 and n <=5:
                self.assertEqual(multiplier,4.0)
            elif n >5 and n<=10:
                self.assertEqual(multiplier,3.0)
            else:
                self.assertEqual(multiplier,2.0)

class TestQCMethods_get_buddy_limits(unittest.TestCase):
#buddy_anom_by_grid, buddy_multiplier_by_grid = get_buddy_limits(anoms_by_grid,pentad_stdev)
    def setUp(self):
        obs = []
        for lat in [-2,-1,0,1,2]:
            for lon in [-2,-1,0,1,2]:
                ob = MarineReport('',0.5+lat,0.5+lon,30.0,30.0,2005,1,1,12,None,None,'')
                ob.setnorm(28.0,28.0)
                obs.append(ob)
        self.anoms_by_grid = grid_super_obs(obs,'SST')
        self.dummy_pentad_stdev = np.full([73,180,360], 1.0)

    def test_single_ob_has_wide_limit(self):
        ob = MarineReport('',0.5,0.5,30.0,30.0,2005,1,1,12,None,None,'')
        ob.setnorm(28.0,28.0) 
        anoms_by_grid = grid_super_obs([ob],'SST')
        
        buddy_anom_by_grid, buddy_multiplier_by_grid = get_buddy_limits(anoms_by_grid,self.dummy_pentad_stdev)
        
        self.assertEqual(len(buddy_anom_by_grid),1)
        for key in buddy_anom_by_grid:
            self.assertEqual(buddy_anom_by_grid[key],0.0)
            self.assertEqual(buddy_multiplier_by_grid[key],500.0)

    def test_multiple_obs(self):
        buddy_anom_by_grid, buddy_multiplier_by_grid = get_buddy_limits(self.anoms_by_grid,self.dummy_pentad_stdev)
        for key in buddy_anom_by_grid:
            self.assertEqual(buddy_anom_by_grid[key],2.0)
            self.assertIn(buddy_multiplier_by_grid[key],[2.5,3,3.5,4])

class TestQCMethods_buddy_check(unittest.TestCase):
    
    def setUp(self):
        
        badob   = MarineReport('',30.5,-40.5,30.0,30.0,2005,1,1,12,None,None,'')
        goodoba = MarineReport('',30.5,-40.5,20.0,20.0,2005,1,1,12,None,None,'')
        goodobb = MarineReport('',30.5,-41.5,20.0,20.0,2005,1,1,12,None,None,'')

        badob.setnorm(30.0,30.0)
        goodoba.setnorm(30.0,30.0)
        goodobb.setnorm(30.0,30.0)

        self.obs = []
        self.obs.append(badob)
        for i in range(0,100):
            self.obs.append(goodoba)
            self.obs.append(goodobb)

        baddecob   = MarineReport('',30.5,-40.5,30.0,30.0,2005,12,31,12,None,None,'')
        gooddecoba = MarineReport('',30.5,-40.5,20.0,20.0,2005,12,31,12,None,None,'')
        gooddecobb = MarineReport('',30.5,-41.5,20.0,20.0,2005,12,31,12,None,None,'')

        baddecob.setnorm(30.0,30.0)
        gooddecoba.setnorm(30.0,30.0)
        gooddecobb.setnorm(30.0,30.0)

        self.decobs = []
        self.decobs.append(baddecob)
        for i in range(0,100):
            self.decobs.append(gooddecoba)
            self.decobs.append(gooddecobb)

#read in the pentad climatology of standard deviations
        sst_stdev_climatology_file = '/home/h04/hadjj/HadSST2_pentad_stdev_climatology.nc'
        climatology = Dataset(sst_stdev_climatology_file)
        self.sst_pentad_stdev = climatology.variables['sst'][:]

        #id,lat,lon,sst,mat,year,month,day,hour,ds,vs,uid

    def test_one_bad_dec_ob_with_lots_of_neighbours(self):
        qcs = mds_buddy_check(self.decobs,self.sst_pentad_stdev,'SST')
        self.assertEqual(qcs[0].get_qc('SST','buddy_fail'),1)
        for i in range(1,len(qcs)):
            self.assertEqual(qcs[i].get_qc('SST','buddy_fail'),0)

    def test_one_bad_ob_with_lots_of_neighbours(self):
        qcs = mds_buddy_check(self.obs,self.sst_pentad_stdev,'SST')
        self.assertEqual(qcs[0].get_qc('SST','buddy_fail'),1)
        for i in range(1,len(qcs)):
            self.assertEqual(qcs[i].get_qc('SST','buddy_fail'),0)

    def test_one_bad_ob_with_lots_of_neighbours_mat(self):
        qcs = mds_buddy_check(self.obs,self.sst_pentad_stdev,'AT')
        self.assertEqual(qcs[0].get_qc('AT','buddy_fail'),1)
        for i in range(1,len(qcs)):
            self.assertEqual(qcs[i].get_qc('AT','buddy_fail'),0)

    def test_no_neighbours(self):
        goodoba = MarineReport('',30.5,-40.5,20.0,30.0,2005,1,1,12,None,None,'')
        goodoba.setnorm(30.0,30.0)
        qcs = mds_buddy_check([goodoba], self.sst_pentad_stdev, 'SST')
        self.assertEqual(qcs[0].get_qc('SST','buddy_fail'),0)

    def test_with_two_obs_and_known_climatology_just_passes(self):
        '''
        Make two observations within 1 degree of each other and with an SST difference of 
        3.999. The buddy check should not be triggered.
        '''
        goodob1 = MarineReport('',0.5,0.5,20.0,20.0,2005,3,1,12,None,None,'')
        goodob1.setnorm(20.0,20.0)
        goodob2 = MarineReport('',0.5,1.5,23.999,20.0,2005,3,1,12,None,None,'')
        goodob2.setnorm(20.0,20.0)
        pentad_stdev = np.full([73,180,360], 1.0)
        qcs = mds_buddy_check([goodob1,goodob2], pentad_stdev, 'SST')
        self.assertEqual(qcs[0].get_qc('SST','buddy_fail'),0)
        self.assertEqual(qcs[1].get_qc('SST','buddy_fail'),0)

    def test_with_two_obs_and_known_climatology_just_fails(self):
        '''
        Make two observations within 1 degree of each other and with an SST difference of 
        4.001. The buddy check should just be triggered by this.
        '''
        goodob1 = MarineReport('',0.5,0.5,20.0,20.0,2005,3,1,12,None,None,'')
        goodob1.setnorm(20.0,20.0)
        goodob2 = MarineReport('',0.5,1.5,24.001,20.0,2005,3,1,12,None,None,'')
        goodob2.setnorm(20.0,20.0)
        pentad_stdev = np.full([73,180,360], 1.0)
        qcs = mds_buddy_check([goodob1,goodob2], pentad_stdev, 'SST')
        self.assertEqual(qcs[0].get_qc('SST','buddy_fail'),1)
        self.assertEqual(qcs[1].get_qc('SST','buddy_fail'),1)

    def test_all_thresholds_at_1deg_separation(self):
        '''
        There are a series of thresholds in the buddy check which are triggered with increasing 
        numbers of neighbouring obs. Check that neighbour counts trigger QC at just above the 
        threshold, but do not trigger QC just below it. This is not a good test in so far as it 
        tests implementation rather than interfaces, but sod it.
        '''
        nob_limits = [  6,  15,  16, 100, 101]
        multipliers= [3.5, 3.5, 3.0, 3.0, 2.5]

        pentad_stdev = np.full([73,180,360], 1.0)

        for i in range(0,len(nob_limits)):
            obs_which_pass=[]
            obs_which_fail=[]
            for j in range(0,nob_limits[i]):
                ob = MarineReport('',0.5,0.5,20.0,20.0,2005,3,1,12,None,None,'')
                ob.setnorm(20.0,20.0)
                obs_which_pass.append(ob)
                obs_which_fail.append(ob)

            #one ob just below the threshold
            goodob2 = MarineReport('',0.5,1.5,20.0+multipliers[i]-0.001, 20.0,2005,3,1,12,None,None,'')
            goodob2.setnorm(20.0,20.0)
            obs_which_pass.append(goodob2)
            qcs = mds_buddy_check(obs_which_pass, pentad_stdev, 'SST')
            for qc in qcs: 
                self.assertEqual(qc.get_qc('SST','buddy_fail'),0)  #all obs should pass in this case

            #one ob just above the threshold
            badob2  = MarineReport('',0.5,1.5,20.0+multipliers[i]+0.001, 20.0,2005,3,1,12,None,None,'')
            badob2.setnorm(20.0,20.0)
            obs_which_fail.append(badob2)  
            qcs = mds_buddy_check(obs_which_fail, pentad_stdev, 'SST')
            for j in range(0,nob_limits[i]):
                self.assertEqual(qcs[j].get_qc('SST','buddy_fail'),0, 'incorrect QC decision at ob '+str(j)+' with nob_limit '+\
                                 str(nob_limits[i])+' and threshold of '+str(multipliers[i]))
            self.assertEqual(qcs[nob_limits[i]].get_qc('SST','buddy_fail'),1) #last ob should always fail in this case

if __name__ == '__main__':
    unittest.main()
