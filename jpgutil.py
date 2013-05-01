import os

def is_jpg(path):
    return os.path.splitext(path)[1].lower() in ['.jpg', '.jpeg']

def findJpgs(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if is_jpg(filename):
                yield os.path.join(root, filename)
