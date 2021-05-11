#!/usr/bin/python3
# title			:duplicate_detection.py
# description	:Image detection model for LSDM Group project
# author			:Kevin Barba
# team           :Oscar, Nicole, Kevin
# date			:20210501
# version		:0.1
# usage			:python duplicate_detection.py
# notes			:
# python_version	:3.7
# ==============================================================================
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
# import MySQLdb as mysql
import mysql.connector as mysql

IMAGE_FORMAT = ['jpeg', 'jpg', 'png', 'bmp', 'svg']
DB = None


def detection(dir):
    phasher = PHash()
    encodings = phasher.encode_images(image_dir=dir)
    duplicates = phasher.find_duplicates(encoding_map=encodings, scores=True)
    only_dup = {k: v for k, v in duplicates.items() if len(v) > 0}
    data = {}
    done = []
    for k, v in only_dup.items():
        if len(v) > 0:
            curr = only_dup[k]
            for d in curr:
                dup_name = d[0]
                metric = d[1]
                data = {'user_id': dir[dir.index('/')+1:], 'image_id': k, 'ref_image_id': dup_name, 'similarity': metric}
                signature = str(dup_name)+str(k)+str(metric)
                if signature not in done:
                    _insert_dupimages(data)
                    done.append(str(k)+str(dup_name)+str(metric)) # reverse order!
                else:
                    logging.info("Found same signature for record. Skipped.")
    return


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
    # TAGS for metadata fields and its corresponding meaning
    fields = {256: 'ImageWidth', 257: 'ImageLength', 271: 'Make', 272: 'Model',
              306: 'DateTime'}
    parsed = {}
    for i in images:
        meta = piexif.load(i)
        for k, v in fields.items():
            parsed[v] = meta['0th'][k]
    return parsed


def _insert_dupimages(data: dict):
    global DB
    cursor = DB.cursor()
    table = "duplicate_images"
    query = f"INSERT INTO {table} (user_id, image_id, ref_image_id, similarity) " \
            f"VALUES ({data['user_id']}, {data['image_id']}, {data['ref_image_id']}, {data['similarity']})"
    output = _execute_query(cursor, query)
    return output


def _query_image(table: str, id: str):
    global DB
    cursor = DB.cursor(buffered=True)
    # table = "duplicate_images"
    query = f"SELECT * FROM {table} WHERE id={id}"
    output = _execute_query(cursor, query)
    cursor.close()
    return output


def _execute_query(cursor, query, error_checking=False):
    global DB
    cursor.execute(query)
    DB.commit()
    output = cursor.fetchone()
    if error_checking:
        if not output:
            logging.error(f"Query: {query} return NONE. Continue.")
            return False
        if len(output) > 1:
            logging.warning(f"Query {query} return MORE THAN ONE. Continue.")
            return output
        return output[0]
    return


def main(args):
    global DB
    if not os.path.exists(args.dir):
        logging.error(f"Directory {args.dir} does not exists in current working directory. Exit.")
        exit(1)
    # assume initial dir is empty and wait for submission
    try:
        DB = mysql.connect(host="localhost", user="lsdm", password="A&zRvGuYrp84cett", db="images")
    except mysql.OperationalError:
        logging.error("Error connecting to the database. Exit.")
        exit(1)
    done = []
    queue_dirs = [name for name in os.listdir(args.dir) if os.path.isdir(os.path.join(args.dir, name))]
    existing = True
    while True:
        if existing:
            logging.info("Processing existing directories.")
            for queue in queue_dirs:
                detection(os.path.join(args.dir, queue))
                done.append(queue)
                logging.info(f"Directory {done} was processed.")
            existing = False
        list_dirs = [name for name in os.listdir(args.dir) if os.path.isdir(os.path.join(args.dir, name))]
        diff = list(set(list_dirs) - set(done))
        if len(diff) == 0:
            logging.warning("wait")
            time.sleep(5)
            continue
        to_process = list_dirs.pop()
        duplicated = detection(os.path.join(args.dir, to_process))
        done.append(to_process)
        # done[to_process] = {k: v for k, v in duplicated.items() if len(v) > 0}

        # if args.outputimage:
        # plot_duplicates(image_dir='output', duplicate_map=done[to_process], filename='duplicate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="duplicate_detection")
    parser.add_argument('--dir', metavar='DIR', required=True,
                        help="The directory where the images are located")
    # parser.add_argument('--original', metavar='ORIGINAL', required=True,
    #                     help="Original image to search for duplicates")
    parser.add_argument('--debug', action='store_true', help="Debug mode")
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
        main(parsed)
    else:
        if parsed.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)
        main(parsed)
