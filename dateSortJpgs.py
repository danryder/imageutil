#!/usr/bin/env python
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
