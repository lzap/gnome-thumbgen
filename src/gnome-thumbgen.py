#!/usr/bin/python
# vim: ai ts=4 sts=4 et sw=4
import sys
import os
import hashlib
import re
from optparse import OptionParser
from PIL import Image

def main():
    parser = OptionParser(usage="%prog [-p] [-e] dir", version="%prog 1.0")

    parser.add_option("-o", 
                      "--output",
                      dest="output_dir", 
                      default=os.path.join(os.path.expanduser('~'), ".thumbnails"),
                      help="output directory (default: ~/.thumbnails)",
                      metavar="DIR")

    parser.add_option("-p", 
                      type="int", 
                      dest="strip_num", 
                      default=0,
                      help="strip n elements from the beginning of the path")

    parser.add_option("-x", 
                      "--prefix",
                      dest="prefix",
                      default="/",
                      help="add directory to the beginning of the path", 
                      metavar="DIR")

    parser.add_option("-e", 
                      "--extensions",
                      dest="extensions",
                      default="bmp|jpe?g|gif|png|tiff|ico|xpm",
                      help="accepted image extensions regular expression (default: jpe?g|png|gif)", 
                      metavar="REGEXP")

    parser.add_option("-l", 
                      "--skip-large",
                      dest="skip_large",
                      action="store_true",
                      default=False,
                      help="do not create large (256x256) thumbnails")

    parser.add_option("-n", 
                      "--no-check",
                      action="store_false",
                      dest="check", 
                      default=True,
                      help="do not check for file existence")

    parser.add_option("-f", 
                      "--force",
                      action="store_true",
                      dest="force", 
                      default=False,
                      help="do not comapre file modification time forcing rewrite all thumbnails")

    parser.add_option("-v", 
                      "--verbose",
                      action="store_true",
                      dest="verbose", 
                      default=False,
                      help="print additional information during processing")

    parser.add_option("-d", 
                      "--debug",
                      action="store_true",
                      dest="debug", 
                      default=False,
                      help="print debugging information")

    (options, args) = parser.parse_args()

    # check params
    if len(args) < 1:
        parser.error("please provide one or more directories")
    if options.check and not os.path.isdir(options.prefix):
        parser.error("prefix must be existing directory")
    if not options.prefix.startswith(os.sep):
        parser.error("prefix must be absolute path (starting with /)")
    if not os.path.isdir(options.output_dir):
        parser.error("output dir must be existing directory")
    if len(options.extensions) == 0:
        parser.error("extensions regexp must be provided")

    # correct params
    if not options.prefix.endswith(os.sep):
        options.prefix = options.prefix + os.sep

    # here we go
    for dir in args:
        for root, subFolders, files in os.walk(dir):
            for filename in files:
                file = os.path.join(root, filename)
                filenamewoext, ext = os.path.splitext(filename)
                if re.match("\.(" + options.extensions + ")", ext, re.I):

                    if options.verbose:
                        print file

                    hashsource = "file://" + filename_transform(file, options)

                    if options.debug:
                        sys.stderr.write('hash source: ' + hashsource + "\n")

                    hash = hashlib.md5(hashsource).hexdigest()

                    size = 128, 128
                    ofname = os.path.join(options.output_dir, "normal", hash) + ".png"
                    create_thumbnail(file, ofname, hash, size, options.debug, options.force)

                    if not options.skip_large:
                        size = 256, 256
                        ofname = os.path.join(options.output_dir, "large", hash) + ".png"
                        create_thumbnail(file, ofname, hash, size, options.debug, options.force)
                else:
                    if options.debug:
                        sys.stderr.write('skipping: ' + file + "\n")

def filename_transform(file, options):
    file = os.path.abspath(file)
    filec = file.split(os.sep)
    filec = filec[1:]
    if options.strip_num > len(filec):
        sys.stderr.write("strip level too big\n")
    if options.strip_num > 0:
        filec = filec[options.strip_num:]
    result = os.sep.join(filec)
    result = options.prefix + result
    #if not result.startswith(os.sep):
        #result = os.sep + result
    if options.check and not os.path.isfile(result):
        sys.stderr.write("non-existing file: %s\n" % result)
    return result

def create_thumbnail(source, target, hashsource, size, debug, force):
    if force or not os.path.isfile(target) or os.stat(source).st_mtime > os.stat(target).st_mtime:
        # create target dir if not exists
        dir = os.path.dirname(target)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        # create the thumbnail
        im = Image.open(source)
        im.thumbnail(size, Image.ANTIALIAS)
        if debug:
            sys.stderr.write('creating: ' + target + "\n")
        im.save(target, "PNG")
    else:
        if debug:
            sys.stderr.write('up to date: ' + target + "\n")

if __name__ == "__main__":
    main()

