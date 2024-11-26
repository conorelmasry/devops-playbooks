#!/usr/bin/env python3

# PURPOSE
# add metadata about a new box version to the metadata file
# should also work with python2

import json
import argparse
import os
import sys
from time import strftime
import shutil

# Parsing the command line. Use -h to print help
parser = argparse.ArgumentParser()
parser.add_argument("version",       help="the new version of the vagrant box to be added. Must be unique")
parser.add_argument("sha256sum",     help="the sha256 sum of the newly created package.box")
parser.add_argument("box_file",      help="full path to the package.box, eg /vagrant/boxes/ol8_8.4.1.box")
parser.add_argument("metadata_file", help="full path to the metadata file, eg /vagrant/boxes/ol8.json")
args = parser.parse_args()

# this is the JSON element to add
new_box_version = {
    "version": args.version,
    "release_date": strftime("%d-%b-%Y"),
    "providers": [
        {
            "name": "virtualbox",
            "url": "file://" + args.box_file,
            "checksum": args.sha256sum,
            "checksum_type": "sha256"
        }
    ]
}

...

# check if the box_file exists
if (not os.path.isfile(args.box_file)):
    sys.exit("FATAL: Vagrant box file {} does not exist".format(args.box_file))

# read the existing metadata file
try:
    with open(args.metadata_file, 'r+') as f:
        metadata = json.load(f)
except OSError as err:
    sys.exit ("FATAL: Cannot open the metadata file {} for reading: {}".format(args.metadata_file, err))

# check if the version to be added exists already. 
all_versions =  metadata["versions"]
if args.version in all_versions.__str__():
    sys.exit ("FATAL: new version {} to be added is a duplicate".format(args.version))

# if the new box doesn't exist already, it's ok to add it
#metadata['versions'].append(new_box_version)
metadata['versions'].insert(0, new_box_version)
# create a backup of the existing file before writing
try:
    bkpfile = args.metadata_file + "_" + strftime("%y%m%d_%H%M%S")
    shutil.copy(args.metadata_file, bkpfile)
except OSError as err:
    sys.exit ("FATAL: cannot create a backup of the metadata file {}".format(err))

# ... and write changes to disk
try:
    with open(args.metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
except OSError as err:
    sys.exit ("FATAL: cannot save metadata to {}: {}".format(args.metadata_file, err))

print("INFO: process completed successfully")