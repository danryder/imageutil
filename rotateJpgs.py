#!/usr/bin/env python
#
# Losslessly rotate and reset of orientation EXIF
# for all JPGs in a directory
#  
# requires -- libimage-exiftool-perl: /usr/bin/exiftool
# requires -- libjpeg-turbo-progs: /usr/bin/jpegtran
#
#

import sys
import os
import subprocess
import shutil
from multiprocessing import Pool
import argparse
import jpgutil

backup_dir = None

def checkAndRotate(path):
    """
    Check the Orientation of an image
    If it's not normal, rotate and reset orientation
    """
    if not jpgutil.is_jpg(path):
        return

    cmd = [ 'exiftool', '-Orientation', '-S', path ]
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    retval = subproc.wait()
    if retval != 0:
        raise Exception("error occurred in exiftool command to check orientation - returned %d" % retval)
        return

    orientation = subproc.communicate()[0]

    rotate = None
    if orientation.find('Rotate 90') >= 0:
        rotate = '90'
    elif orientation.find('Rotate 270') >= 0:
        rotate = '270'
    elif orientation.find('Rotate 180') >= 0:
        rotate = '180'

    if rotate is not None:
        if backup_dir is not None:
            # parallel backup directory
            bak_dir = os.path.join(backup_dir, os.path.dirname(path))
            try:
                os.makedirs(bak_dir)
            except OSError, e:
                if e.errno == errno.EEXIST:
                    pass
                else:
                    raise e

            bak_file = os.path.join(bak_dir, os.path.basename(path))
            shutil.copyfile(infile, bak_file)

        infile = path
        rotfile = path + '.rotated'
        cmd = ['jpegtran', '-copy', 'all', '-rotate', rotate, '-outfile', rotfile, infile ]

        retval = subprocess.Popen(cmd).wait()
        if retval != 0:
            raise Exception("error occurred in jpegtran command - returned %d" % retval)

        cmd = [ "exiftool", "-S", "-n", "-Orientation=1", "-overwrite_original", rotfile ]
        subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        retval = subproc.wait()
        if retval != 0:
            raise Exception("error occurred in exiftool command to reset orientation - returned %d" % retval)

        # if no errors, overwrite original file
        os.rename(rotfile, infile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir")
    parser.add_argument("--processes", type=int, default=8,
                        help="use this many concurrent processes")
    parser.add_argument("--backup", default=None,
                        help="create backup copies here")
    args = parser.parse_args()
    backup = args.backup
    if backup is not None:
        os.makedirs(backup)

    if args.processes > 1:
        p = Pool(args.processes)
        p.map(checkAndRotate, jpgutil.findJpgs(args.dir))
    else:
        for j in jpgutil.findJpgs(args.dir):
            checkAndRotate(j)
