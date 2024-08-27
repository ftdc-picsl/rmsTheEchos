#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 7/19/2024

@author: co
"""
import pandas as pd
import flywheel
import sys
import pytz
import os.path
from fwtools import *
fw=flywheel.Client('')

if (args_count := len(sys.argv)) != 6:
	print("USAGE: python3 download_t1vnav_echoes.py sub ses wrkDir group projectLabel")
	raise SystemExit(2)

subLabel = sys.argv[1]
sesLabel = sys.argv[2]
wrkDir = sys.argv[3]
group = sys.arg[4]
projectLabel =  sys.arg[5]

outDir = wrkDir + "/" + subLabel + "/" + sesLabel + "/"

if not os.path.exists(outDir):
    os.makedirs(outDir)

sess = fw.lookup("{}/{}/{}/{}".format(group, projectLabel, subLabel, sesLabel))

def find_echos(sess):
    t1_acq = []
    # use iter_find to grab only vnavs that aren't non-distortion corrected
    for acq in sess.acquisitions.iter_find('label=~vNav(?!ND)'):
        acq = acq.reload()
        echo_objs = [file_obj for file_obj in acq.files if (file_obj.name.endswith('.nii.gz') or file_obj.name.endswith('.json')) \
                     and not "ph" in file_obj.name \
                        and 'T1' in file_obj.classification['Measurement'] \
                            and not 'ND' in file_obj.info['ImageType']]
        for file in echo_objs:
            outFile = outDir + file.name
            print("downloading: " + outFile)
            file.download(outFile)

find_echos(sess)
