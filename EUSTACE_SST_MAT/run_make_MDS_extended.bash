#!/bin/bash
# set -x
# ************************************************************************
# Simple script to create and submit SPICE jobs to Slurm.
#
# Author: hadkw
# Date: 24 June 2019
#
# Does each month/year combination as a separate script.  
#    Polls the queue to not overload the system or quotas (Thanks to JJK for this)
#
# ************************************************************************
# START

year=1973
end=1973
runtype='OBSclim2NBC'

echo "Running all months between ${year} and ${end} inclusive"

#read -p "Have you checked set_vars_and_paths.py for correct settings (y/n)" test
#
#if [ "$test" == "n" ]; then
#    echo "Adjust set_vars_and_paths.py for a standard QC with the buddy check on - third iteration"
#    exit
#fi

while [ $year -le $end ];
do
    # check for number of jobs running at the moment
    n_jobs=`squeue -l | grep hadobs | wc -l`

    # if more than 200 wait and try again in 2 mins
    while [ $n_jobs -gt 200 ];
    do
        echo `date` "  SPICE queue for user hadobs maxed out - sleeping 2mins"
        sleep 2m
        n_jobs=`squeue -l | grep hadobs | wc -l`
    done

    # once sufficient space in the queue
    # submit the next twelve months to run
    for month in 01 02 03 04 05 06 07 08 09 10 11 12;
#    for month in 08;
    do
        # separate file for each job
        spice_script=spice_hadisdh_extended_${year}${month}.bash
        
        echo "#!/bin/bash -l" > ${spice_script}
        echo "#SBATCH --mem=6000" >> ${spice_script}
        echo "#SBATCH --ntasks=1" >> ${spice_script}
        echo "#SBATCH --output=/project/hadobs2/hadisdh/marine/PROGS/Build/LOGFILES/make_extended_${year}${month}.txt" >> ${spice_script}
        echo "#SBATCH --time=360" >> ${spice_script}
        echo "#SBATCH --qos=normal" >> ${spice_script}
        
	echo module load scitools/default_legacy-current
        echo "python MDS_make_extended.py --year1 ${year} --year2 ${year} --month1 ${month} --month2 ${month} --typee ${runtype}" >> ${spice_script}
	
        sbatch ${spice_script}       
    done

    echo "Submitted ${year}"

    let year=${year}+1
    
done

# remove all job files on request
#rm -i ${cwd}/spice_hadisdh_grid_*

#  END
#************************************************************************
