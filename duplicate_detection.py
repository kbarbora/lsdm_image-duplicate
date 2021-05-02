#!/usr/bin/python3
#title			:duplicate_detection.py
#description	:Image detection model for LSDM Group project
#author			:Kevin Barba
#team           :Oscar, Nicole, Kevin
#date			:20210501
#version		:0.1
#usage			:python duplicate_detection.py
#notes			:
#python_version	:3.7
#==============================================================================
import sys
import time
from imagededup.methods import PHash
from imagededup.utils import plot_duplicates
from glob import glob
import zipfile
import os
import argparse
import logging
import json
import piexif

IMAGE_FORMAT= [ 'jpeg', 'jpg', 'png', 'bmp', 'svg']
def detection(dir):
    # files = glob(f"{dir}/*")
    # if len(files) < 1:
    #     logging.error(f"There are no files in the directory. Exit.")
    #     exit(1)
    phasher = PHash()
    encodings = phasher.encode_images(image_dir=dir)
    return phasher.find_duplicates(encoding_map=encodings)

def write_output(dir, data):
    out_dir = os.path.join("output", dir)
    # out_files = ['duplicated.json', 'images_metadata.json', 'deleted.json', 'output_data.zip']
    duplicated = os.path.join(out_dir, "duplicated.json")
    with open(duplicated, 'w+') as fh:
        fh.write(json.dumps(data["duplicated"]))

    meta = os.path.join(out_dir, "images_metadata.json")
    with open(meta, 'w+') as fh:
        fh.write(json.dumps(data["metadata"]))

    deleted = os.path.join(out_dir, "deleted.json")
    with open(deleted, 'w+') as fh:
        fh.write(json.dumps(data["deleted"]))

    out_data = os.path.join(out_dir, "output_data.zip")
    with zipfile.ZipFile(out_data, mode='x') as zip:
        for d in data['paths']:
            zip.write(d)
        logging.info(f"Zip created with {len(data['paths'])} images")
    return

def get_metadata(images: list):
    fields = ['ImageWidth', 'ImageLength', 'Make', 'Model',
              'DateTime']
    for i in images:
        meta = piexif.load(i)





def main(args):
    if not os.path.exists(args.dir):
        logging.error(f"Directory {args.dir} does not exists in current working directory. Exit.")
        exit(1)
    # assume initial dir is empty and wait for submission
    done = {}
    while True:
        list_dirs = [name for name in os.listdir(args.dir) if os.path.isdir(os.path.join(args.dir, name))]
        diff = list(set(list_dirs) - set(done.keys()))
        if len(diff) == 0:
            logging.warning("wait")
            time.sleep(5)
            continue
        to_process = list_dirs.pop()
        duplicated = detection(os.path.join(args.dir, to_process))
        done[to_process] = {k: v for k, v in duplicated.items() if len(v) > 0}

        # if args.outputimage:
            # plot_duplicates(image_dir='output', duplicate_map=done[to_process], filename='duplicate')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="duplicate_detection")
    parser.add_argument('--dir', metavar='DIR', required=True,
                        help="The directory where the images are located")
    parser.add_argument('--original', metavar='ORIGINAL', required=True,
                        help="Original image to search for duplicates")
    parser.add_argument('--debug',action='store_true', help="Original image to search for duplicates")
    parser.add_argument('--recursive', '-r', action='store_true',
                        help="Do a recursive search, traversing through all directories inside.")
    parser.add_argument('--delete', action='store_true', help="Delete all the duplicate found without asking the user.")
    parser.add_argument('--log', action='store_true',
                        help="Log to file 'image_detection.log' in append mode instead to STDIN")
    parser.add_argument('--outputimage', '-oi', action='store_true',
                        help="Produce an output image showing the possible duplicates")
    parsed = parser.parse_args()
    if parsed.log:
        logging.basicConfig(filename="image_detection.log", filemode='a+', level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.WARNING)
    if parsed.debug:
        main(parsed)
