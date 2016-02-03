echo "Testing basic QC routines"
python2.7 qc_tests.py
echo "Testing track check routines"
python2.7 track_check_tests.py
echo "Testing buddy check routines"
python2.7 buddy_check_tests.py
echo "Testing spherical geometry routines"
python2.7 test_spherical_geometry.py
echo "Testing database handling routines"
python2.7 test_database_handler.py