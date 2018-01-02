import sys
import argparse
import glob
import os
import subprocess
import psycopg2

if sys.version_info < (3,6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(*sys.version_info[0:3]))

# constants

BABEL="gpsbabel"

def main():

    # pre check system environment
    pre_check()

    # parse args
    (sourcedir, targetdir) = a_parse()

    # get gpx filenames
    gpx_filelist = getfiles(sourcedir)

    print("Number of gpx files: {}".format(len(gpx_filelist)))

    # run conversion
    if not os.path.exists(targetdir):
        print("Creating directory {}".format(targetdir))
        os.makedirs(targetdir)

    for sourcefile in gpx_filelist:

        fname_base = os.path.basename(sourcefile)
        targetfile = os.path.abspath(
                os.path.join(targetdir, fname_base))

        simplify_one(sourcefile, targetfile)
    


#--------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
            description = 
                'Load GPX files in specified directory into postgis database'
            )
    parser.add_argument('source_directory')
    parser.add_argument('target_directory')
    args = parser.parse_args()

    sd = os.path.abspath(args.source_directory)
    td = os.path.abspath(args.target_directory)

    if sd == td:
        print("Source and target directory should not be the same")
        sys.exit(1)
    else:
        return sd, td

#--------------------------------
def getfiles(directory):
    
    normdir = os.path.abspath(directory)
    globexp = os.path.join(normdir, "*.gpx")
    dirs = glob.glob(globexp)

    return dirs

def pre_check():

    try:
        subprocess.call((BABEL, "-?"), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except FileNotFoundError as e:
        print("Error: The command {} could not be found on your system".format(BABEL))
        sys.exit(1)

def simplify_one(sourcefile, targetfile):

    cmd = (
            BABEL,
            "-i", "gpx",
            "-f", sourcefile,
            "-x", "simplify,error=0.01k",
            "-o", "gpx",
            "-F", targetfile
            )

    print("=== Simplifying from {} to {}".format(sourcefile, targetfile))
    subprocess.check_call(cmd)


##############################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
