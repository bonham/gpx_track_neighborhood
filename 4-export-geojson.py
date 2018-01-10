import sys
import argparse
import glob
import os
import subprocess
import psycopg2
import json

if sys.version_info < (3,6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(*sys.version_info[0:3]))

# constants

PG_USER="postgres"

def main():

    # parse args
    database_name = a_parse()

    # connect to db
    conn = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))
    cur = conn.cursor()

    geodir = os.path.normpath("html/geojson")
    oldfiles = glob.glob(os.path.join(geodir,'*'))
    for remove_file in oldfiles:
        print("Deleting {}".format(remove_file))
        os.unlink(remove_file)



    # read geojson
    #cur.execute("select ST_AsGeoJSON(wkb_geometry) from tracks where tracks.ogc_fid = 2")
    cur.execute("select category, ST_AsGeoJSON(ST_Collect(wkb_geometry)), min(freq), max(freq) from track_segment_freq_categories group by category order by category")
    r = cur.fetchall()

    cat_frequencies = []

    for row in r:
        (cat, js, minfreq, maxfreq) = row
        cat_frequencies.append( { "category": cat, "min": minfreq, "max": maxfreq } )
        
        fname = os.path.join(geodir, "g_{}.json".format(cat))
        print("Writing "+fname)
        with open(fname,"w") as f:
            f.write(js)

    # dump file for legend
    fname = os.path.join(geodir, "legend.json")
    print("Writing {}".format(fname))
    legendfile = open(fname, "w")
    json.dump(cat_frequencies, legendfile)

    # print categories 
    for item in cat_frequencies:
        print("Category {}: {:3} - {:3}".format(item["category"], item["min"], item["max"]))



#--------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
            description = 
                'dump geojson'
            )
    parser.add_argument('database')
    args = parser.parse_args()

    database_name = args.database
    return database_name



###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
