#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 7/23/2024

@author: co
"""
import pandas as pd
import flywheel
import re
import sys
import os.path
import json
from fwtools import *
fw=flywheel.Client('')


if (args_count := len(sys.argv)) != 6:
	print("USAGE: python3 upload_rms.py sub ses wrkDir group projectLabel")
	raise SystemExit(2)

subLabel = sys.argv[1]
sesLabel = sys.argv[2]
wrkDir = sys.argv[3]
group = sys.argv[4]
projectLabel =  sys.argv[5]

outDir = wrkDir + "/" + subLabel + "/" + sesLabel + "/"

sess = fw.lookup("{}/{}/{}/{}".format(group, projectLabel, subLabel, sesLabel))

# futz with json
def create_rms_acquisition_and_upload(rms_json, rms_nii, sess):
    # Load data from JSON file
    with open(rms_json, 'r') as f:
        rms_info = json.load(f)
    
    acq_name = rms_info["SeriesDescription"]
    acquisition = sess.add_acquisition(label=acq_name)
    print(f"RMS acquisition container created {acq_name}")

    acquisition.upload_file(rms_json)

    # Replace a file's modality and classification
    fw_rms_json = os.path.basename(rms_json)
    acquisition.replace_file_classification(fw_rms_json, {
        'Intent': ['Structural'],
        'Measurement': ['T1'],
        'Features': ['RMS']
        }, modality='MR')
    acquisition.update_file_info(fw_rms_json,rms_info)

    print(f"Uploaded RMS json {rms_json}")

    acquisition.upload_file(rms_nii)
    fw_rms_nii = os.path.basename(rms_nii)
    acquisition.replace_file_classification(fw_rms_nii, {
        'Intent': ['Structural'],
        'Measurement': ['T1'],
        'Features': ['RMS']
        }, modality='MR')
    acquisition.update_file_info(fw_rms_nii,rms_info)

    print(f"Uploaded RMS nii {rms_nii}")

# dumbadum
allFiles = os.listdir(outDir)
# find rms niftis in the session directory 
rms_ends = r".*_rms\.nii\.gz$"
rms_files = [os.path.join(outDir, f) for f in allFiles if re.match(rms_ends, f)]

for rms_nii in rms_files:
    print("creating container for: " + rms_nii)

    rms_json = re.sub("nii.gz", "json", rms_nii)
    
    if os.path.isfile(rms_json):
        create_rms_acquisition_and_upload(rms_json, rms_nii, sess)



