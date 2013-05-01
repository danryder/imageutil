#!/usr/bin/env python

# Copyright (c) 2013, Dan Ryder
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
A parallel wrapper around exiftool and jpegtran.

Losslessly rotate and reset of orientation EXIF for all JPGs in a directory.

requires -- libimage-exiftool-perl: /usr/bin/exiftool
requires -- libjpeg-turbo-progs: /usr/bin/jpegtran
"""

import sys
import os
import errno
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
        infile = path
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
            print "copying %s to backup %s" % (infile, bak_file)
            shutil.copyfile(infile, bak_file)

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
    parser.add_argument("--backupdir", default=None,
                        help="create backup copies here")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        raise Exception("%s not a directory,"% args.dir)

    backup_dir = args.backupdir
    if backup_dir is not None:
        os.makedirs(backup_dir)

    p = Pool(args.processes)
    p.map(checkAndRotate, jpgutil.findJpgs(args.dir))
