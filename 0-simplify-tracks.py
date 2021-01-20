import sys
import argparse
import glob
import os
import re
import subprocess
from gpx2db.utils import setup_logging

# constants

BABEL = "gpsbabel"

logger = None


def main():

    # pre check system environment
    pre_check()

    # parse args
    (sourcedir, targetdir, error, distance, debug) = a_parse()

    global logger
    logger = setup_logging(debug)

    # get gpx filenames
    gpx_filelist = getfiles(sourcedir)

    print("Number of gpx files: {}".format(len(gpx_filelist)))

    # run conversion
    if not os.path.exists(targetdir):
        print("Creating directory {}".format(targetdir))
        os.makedirs(targetdir)

    failed = []
    for sourcefile in gpx_filelist:

        fname_base = os.path.basename(sourcefile)
        targetfile = os.path.abspath(
            os.path.join(targetdir, fname_base))

        success = simplify_one(sourcefile, targetfile, error, distance)
        if not success:
            failed.append(sourcefile)

    if failed:
        print("")
        print("Operation failed for the following files:")
        print("")
        print("\n".join(failed))


# --------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
        description=(
            'Load GPX files in specified '
            'directory into postgis database')
    )
    parser.add_argument('source_directory')
    parser.add_argument('target_directory')
    parser.add_argument(
        '--error', default='0.001k',
        help=(
            "Simplification factor. Higher values simplify more. "
            "It corresponds to xx in gpsbabel -x "
            "simplify,error=xx Default value is 0.001k"))
    parser.add_argument(
        '--distance', default='0.05k',
        help=(
            "Interpolation distance. Points will be added whenever "
            "two points are more than distance apart. Default is 0.05k."))
    parser.add_argument(
        '--debug', '-d', help="Enable debug output", action="store_true")
    args = parser.parse_args()

    sd = os.path.abspath(args.source_directory)
    td = os.path.abspath(args.target_directory)

    if sd == td:
        print("Source and target directory should not be the same")
        sys.exit(1)
    else:
        return (sd, td, args.error, args.distance, args.debug)

# --------------------------------


def getfiles(directory):

    normdir = os.path.abspath(directory)
    globexp = os.path.join(normdir, "*.gpx")
    dirs = glob.glob(globexp)

    return dirs


def pre_check():

    try:
        subprocess.call((BABEL, "-?"), stderr=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        print(
            "Error: The command {} could not be found "
            "on your system".format(BABEL))
        sys.exit(1)


def simplify_one(sourcefile, targetfile, error, distance):

    latlon_pairs = read_snip_coords()
    snip_args = babel_gpx_snip_argument(latlon_pairs)

    cmd = [
        BABEL,
        "-i", "gpx",
        "-f", sourcefile,
        "-x", "simplify,error={}".format(error),
        "-x", "interpolate,distance={}".format(distance),
        "-x", "transform,wpt=trk,del"]

    cmd.extend(snip_args)

    cmd.extend((
        "-x", "transform,trk=wpt,del",
        "-o", "gpx",
        "-F", targetfile
    ))

    logger.debug(cmd)
    print("=== Simplifying from {} to {}".format(sourcefile, targetfile))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print("Error with gpsbabel: {}, ignoring...".format(e))
        return False
    else:
        return True


def read_snip_coords():
    "Read list of coordinates from env"
    " "
    "Format: $env:GPX_SNIP_COORDS = 'D.dddd,D.dddd D.dddd,D.dddd'"
    "list of decimal degrees lat,lon separated by comma,"
    "multiple coordinates separated by space. Example"
    " "
    "$env:GPX_SNIP_COORDS = '49.213038,3.553038 49.6739,6.46637' "

    VARNAME = 'GPX_SNIP_COORDS'
    return_list = []

    if VARNAME not in os.environ:
        return []

    # split by whitespace
    pair_list = os.environ[VARNAME].split()

    # regex pattern for pair
    latlon_pattern = re.compile(
        r'^(\d+\.\d+),(\d+\.\d+)$'
    )

    for pair in pair_list:

        m = latlon_pattern.match(pair)
        if m:
            lat = m.group(1)
            lon = m.group(2)
            return_list.append((lat, lon))

    return return_list


def babel_gpx_snip_argument(latlon_pair_list):
    "Convert latlon pairs in a list of babel arguments"
    "To cut out all points 1km around the locations"

    babel_snip_args = []

    for pair in latlon_pair_list:

        argstring = (
            "radius,distance=1k,lat={:s},lon={:s},nosort,exclude"
        ).format(
            pair[0], pair[1]
        )

        babel_snip_args.extend(("-x", argstring))

    return babel_snip_args


    ##############################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
