#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 7/22/2024

@author: co
"""
import sys
import pandas as pd
import os.path
import nibabel as nib
import numpy as np
import re
import json


if (args_count := len(sys.argv)) != 6:
	print("USAGE: python3 create_rms.py sub ses wrkDir group projectLabel")
	raise SystemExit(2)

subLabel = sys.argv[1]
sesLabel = sys.argv[2]
wrkDir = sys.argv[3]
group = sys.argv[4]
projectLabel =  sys.argv[5]

# assemble session level directory
outDir = wrkDir + "/" + subLabel + "/" + sesLabel + "/"

allFiles = os.listdir(outDir)
# find niftis in the session directory 
echoEnds = r".*e[1-4]\.nii\.gz$"
nifti_files = [os.path.join(outDir, f) for f in allFiles if re.match(echoEnds, f)]

# redundant now i guess, but see if the images in list are all niftis
def check_niis(nifti_files):
    for file in nifti_files: 
        if not file.endswith(('.nii','.nii.gz')):
            print(file + " is not a nifti, get your act together")
            sys.exit()

# create a ("virtual") nifti image
def calculate_rms_img(nifti_files):
    # initialize 
    data_arrays = []
    for file_path in nifti_files:
        # read images
        nifti_img = nib.load(file_path)
        # convert image to data frame
        data = nifti_img.get_fdata()
        # combine echo-by-echo into one big array
        data_arrays.append(data)
    
    # Stack the data arrays along a new time dimension to create a 4D array
    data_4d = np.stack(data_arrays, axis=-1)

    # Calculate the RMS value across the time dimension (last dimension)
    rms_valuesdec = np.sqrt(np.mean(np.square(data_4d), axis=-1))
    # for measurement/precision reasons, data is truncated at the scanner, so we do that here
    rms_values = np.floor(rms_valuesdec)
    return rms_values, nifti_img.affine, nifti_img.header

# save the nifti image
def save_rms_as_nifti(rms_values, affine, header, nifti_files):
    # Create a new NIfTI image
    rms_img = nib.Nifti1Image(rms_values, affine, header)
    for e1_name in (e1_name for e1_name in nifti_files if "e1" in e1_name):
        print(e1_name)
        rms_nii_name = re.sub('e1', 'rms', e1_name)    
        # Save the NIfTI image to a file
        nib.save(rms_img, rms_nii_name)
        print(f"RMS values saved to {rms_nii_name}")

# check supposed niftis are niftis
check_niis(nifti_files)

# Calculate the RMS values and get the affine and header from one of the original images
rms_values, affine, header = calculate_rms_img(nifti_files)

# Save the RMS values as a NIfTI file
save_rms_as_nifti(rms_values, affine, header, nifti_files)


# create the rms json based off of the first echo
def create_rms_json(nifti_files):
    for e1_name in (e1_name for e1_name in nifti_files if "e1" in e1_name) :
        e1_json = re.sub('nii.gz', 'json', e1_name)
        rms_json = re.sub('e1', 'rms', e1_json)
        # Load data from JSON file
        with open(e1_json, 'r') as f:
            e1_info = json.load(f)

        # edit specific keys to make it rms-y
        rms_info = e1_info
        rms_info["SeriesDescription"] = rms_info["SeriesDescription"] + " RMS"
        rms_info["NumberOfAverages"] = rms_info.pop("EchoNumber")
        rms_info["NumberOfAverages"] = 4
        rms_info["ImageType"] = ["ORIGINAL", "PRIMARY", "OTHER", "NORM", "DIS3D", "DIS2D", "MEAN"]

        with open(rms_json, 'w') as f:
            json.dump(rms_info, f, indent='\t')

        print(f"RMS json saved to {rms_json}")

# get rms json
create_rms_json(nifti_files)

