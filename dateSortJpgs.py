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
A parallel wrapper around a specfic invocation of exiftool.

Find all JPGs in a directory and subdirectories, and move them all to a new
directory, organied by date and time of exposure (using EXIF from image)

Destination files are grouped into directories at the year, month and day
level, and have the date and time also encoded in the output filenames.

The output filenames also retain whatever they were before as a suffix.

requires -- libimage-exiftool-perl: /usr/bin/exiftool
"""

import sys
import os
import re
import subprocess
import argparse
import jpgutil
from multiprocessing import Pool

dst = None
moveRaws = False

newname = re.compile(r'''^\s*\+ FileName = '([^']*)'.*''')

def dateMoveJpg(src):
    print "move by date", src, "to", dst
    p = subprocess.Popen(['exiftool', '-v5', '-FileName<DateTimeOriginal',
                          '-d', 
                          '%s/%%Y/%%m/%%d/%%Y%%m%%d_%%H%%M%%S_%%%%f%%%%-c.%%%%e' 
                          % dst, src,],
                          stdout = subprocess.PIPE,
                          stderr = subprocess.PIPE)
    out, err = p.communicate()
    s = p.wait()
    if s:
        print "exiftool returned", s
    if len(err):
        raise Exception("ERROR" + err)
    
    outlines = out.split('\n')
    newfname = None
    for outline in outlines:
        newfname = newname.match(outline)
        if newfname:
            break
    if not newfname:
        raise Exception("Could not find new filename in output")

    newfname = newfname.groups()[0]
    if not os.path.isfile(newfname):
        raise Exception("New file '%s' not found" % newfname)

    # check for any accompanying .NEF
    if moveRaws:
        if src.endswith('.JPG'):
            raw=src[:-3] + 'NEF'
            if os.path.exists(raw):
                newraw = newfname[:-3] + 'NEF'
                print "Moving RAW %s alongside to %s" % (raw, newraw)
                os.rename(raw, newraw)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--processes", type=int, default=8,
                        help="use this many concurrent processes")
    parser.add_argument("--moveraws", action="store_true",
                        help="also move any corresponding RAW images")
    args = parser.parse_args()

    if not os.path.isdir(args.src):
        raise Exception("%s not a directory"% args.src)

    dst = args.dst
    if not os.path.exists(args.dst):
        print "Creating output directory:", args.dst
        os.makedirs(args.dst)

    moveraws = args.moveraws

    p = Pool(args.processes)
    p.map(dateMoveJpg, jpgutil.findJpgs(args.src))
