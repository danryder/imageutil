import os

def is_jpg(path):
    return os.path.splitext(path)[1].lower() in ['.jpg', '.jpeg']

def findJpgs(path):
    print "finding jpgs in", path
    # handle simple case -- files
    if os.path.isfile(path):
        if is_jpg(path):
            yield path

    # crawl directories
    elif os.path.isdir(path):
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if is_jpg(filename):
                    yield os.path.join(root, filename)
    else:
        print "Not a file or directory", path
