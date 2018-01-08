import sys
import argparse
import glob
import os
import subprocess
import psycopg2

if sys.version_info < (3,6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(*sys.version_info[0:3]))

# constants

PG_USER="postgres"
OGR2OGR="ogr2ogr"


def main():

    # pre check system environment
    pre_check()

    # parse args
    (directory, database_name) = a_parse()

    # get gpx filenames
    gpx_filelist = getfiles(directory)
    print("Number of gpx files: {}".format(len(gpx_filelist)))

    # import files into database
    print("(Re-) creating database {}".format(database_name))
    ogrimport(gpx_filelist, database_name)
    


#--------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
            description = 
                'Load GPX files in specified directory into postgis database'
            )
    parser.add_argument('source_directory')
    parser.add_argument('database')
    args = parser.parse_args()

    database_name = args.database
    directory = args.source_directory
    return directory, database_name


#--------------------------------
def getfiles(directory):
    
    normdir = os.path.abspath(directory)
    globexp = os.path.join(normdir, "*.gpx")
    dirs = glob.glob(globexp)

    return dirs

def pre_check():

    try:
        subprocess.call((OGR2OGR, "--help"), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except FileNotFoundError as e:
        print("Error: The command {} could not be found on your system".format(OGR2OGR))
        sys.exit(1)

def ogrimport(filelist, database_name):

    # connect to postgres db
    
    conn = psycopg2.connect(
                "dbname={} user={}".format("postgres", PG_USER))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()

    # sql setup
    sql1 = "drop database if exists {0}".format(database_name)
    sql2 = "create database {0}".format(database_name)

    cur.execute(sql1)
    cur.execute(sql2)
    conn.close()

    # connect to newly created db
    conn = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # create postgis extension
    sql3 = "create extension postgis"
    cur.execute(sql3)

    # ogr
    ogr_connstring = "PG:dbname={} user={}".format(database_name, PG_USER)

    # loop files
    for gpxfile in filelist:

        cmd = (
                OGR2OGR,
                "-append",
                "-f",
                "PostgreSQL",
                ogr_connstring,
                gpxfile
                )

        print("=== Processing {}".format(gpxfile))
        subprocess.check_call(cmd)

        # dirty workaround for a bug: set track_fid

        # determine last track feature id
        cur.execute("select max(ogc_fid) from public.tracks")
        r = cur.fetchone()
        max_track_fid = r[0]
        print("Track fid: {}".format(max_track_fid))

        # set track_fid for all new trackpoints accordingly
        sql = "update track_points set track_fid = {} where track_fid = 0".format(max_track_fid)
        cur.execute(sql)

        # set name of track
        trackname = os.path.basename(gpxfile)
        sql = "update tracks set name = '{}' where ogc_fid = {}".format(trackname, max_track_fid)
        cur.execute(sql)





if __name__ == "__main__":
    # execute only if run as a script
    main()
