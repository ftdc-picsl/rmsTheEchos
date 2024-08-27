#!/bin/bash

wrkDir=/project/ftdc_misc/colm/rmsWrkDir
group=pennftdcenter
project=HUP6

if [[ $# != 2 ]] ; then
    echo "USAGE: ./download_create_upload_rms.sh <subjectLabel> <sessionLabel> "
    echo " this script is to account for when the scanner didn't create the RMS image by default for whatever reason. This creates the RMS and gets it into the flywheel project so we can do everything we need with it."
    echo " finds the subject and session of interest in flywheel project $project from group $group "
    echo "  1. downloads the 4 echos of the T1 vNavs that are distortion corrected to $wrkDir (download_t1vnav_echoes.py) "
    echo "  2. creates an RMS nii image and accompanying json from the echoes in $wrkDir (create_rms.py)"
    echo "  3. uploads the RMS nii image and accompanying json to flywheel project $project from group $group (upload_rms.py)"
    echo "note that if the scanner did create the RMS and you run this, you'll have two nearly identical (but not) identical images to contend with. The \"imposter\" is the one with no dicoms."
    exit 1
fi
subjectLabel=$1
sessionLabel=$2

module unload python
module load python/3.9

#   1. downloads echos of the T1 vNavs that are distortion corrected to $wrkDir (download_t1vnav_echoes.py) 
python ./download_t1vnav_echoes.py $subjectLabel $sessionLabel $wrkDir $group $project 
#   2. creates an RMS nii image and accompanying json from the echoes in $wrkDir (create_rms.py)
python ./create_rms.py $subjectLabel $sessionLabel $wrkDir $group $project 
#   3. uploads the RMS nii image and accompanying json to flywheel project $project from group $group (upload_rms.py)
python ./upload_rms.py $subjectLabel $sessionLabel $wrkDir $group $project