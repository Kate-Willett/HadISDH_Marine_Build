
a=1850

python2.7 make_db.py -i configuration.txt --year1 1850 --year2 1850
python2.7 base_qc.py -i configuration.txt --year1 1850 --year2 1850

python2.7 make_db.py -i configuration.txt --year1 1851 --year2 1851
python2.7 base_qc.py -i configuration.txt --year1 1851 --year2 1851

python2.7 track_check.py -i configuration.txt --year1 1850 --year2 1850

while [ $a -lt 1990 ]
do

   echo $a
   b=`expr $a + 1`
   c=`expr $b + 1`

   python2.7 make_db.py -i configuration.txt --year1 $c --year2 $c
   python2.7 base_qc.py -i configuration.txt --year1 $c --year2 $c
   python2.7 track_check.py -i configuration.txt --year1 $b --year2 $b
   python2.7 buddy_check.py -i configuration.txt --year1 $a --year2 $a
   python2.7 extract_from_db.py -i configuration.txt --year1 $a --year2 $a

   a=`expr $a + 1`

done
