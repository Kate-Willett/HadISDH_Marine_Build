#!/bin/sh

# Shell script to run the python code make_and_full_qc.py with read in values

# Work out what the name of the script is
echo "Command: $0 $*"
progtorun='make_and_full_qc.py
echo "Program to run: $progtorun"

config='configuration.txt'
echo "config to run: $config"

y1=$1
echo "year1 to run: $y1"

y2=$2
echo "year2 to run: $y2"

m1=$3
echo "month1 to run: $m1"

m2=$4
echo "month2 to run: $m2"

# run the IDL code 
python2.7 $progtorun -i $config --year1 $y1 --year2 $y2 --month1 $m1 --month2 $m2
