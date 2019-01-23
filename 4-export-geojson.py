import sys
import argparse
import glob
import os
import subprocess
import psycopg2
import json
import shutil
import json

if sys.version_info < (3,6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(*sys.version_info[0:3]))

# constants

PG_USER="postgres"
METADATA_FNAME="datasets.json"
BASEDIR=os.path.normpath("html/static/geojson")

def main():

    # parse args
    (database_name, outputDir) = a_parse()

    # connect to db
    conn = psycopg2.connect(
                "dbname={} user={}".format(database_name, PG_USER))
    cur = conn.cursor()

    geodir = os.path.join(BASEDIR, outputDir)

    # remove directory if exists
    print("Removing {}".format(geodir))
    if os.path.exists(geodir) and os.path.isdir(geodir):
        shutil.rmtree(geodir)
    
    # recreate directory ( including parents )
    os.makedirs(geodir, exist_ok=True)

    # create or extend metadata file
    create_extend_metadata(BASEDIR, METADATA_FNAME, outputDir)

    # read geojson
    cur.execute("select category, ST_AsGeoJSON(ST_Collect(wkb_geometry)), min(freq), max(freq) from track_segment_freq_categories group by category order by category")
    r = cur.fetchall()

    # Attention: with low numbers, categories can have gaps. E.g. we could have category 0 2 3 4, but not 1

    cat_frequencies = []

    i = 0
    for row in r:
        (realcat, js, minfreq, maxfreq) = row

        # category will be renumbered to i
        cat_frequencies.append( { "category": i, "min": minfreq, "max": maxfreq } )
        
        fname = os.path.join(geodir, "g_{}.json".format(i))
        print("Writing "+fname)
        with open(fname,"w") as f:
            f.write(js)

        i += 1;

    # write file about how many tracks we have
    numTrackFilePath = os.path.join(geodir, "numberOfTracks.json")
    print("Writing {}".format(numTrackFilePath))
    with open(numTrackFilePath, "w") as fp:
       json.dump(
               {"numberOfTrackFiles": len(r)},
               fp
               )
    
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
                'Write gpx tracks as geojson to disk. The output directory will be "html/static/geojson/<dataset_label>/'
            )
    parser.add_argument('database')
    parser.add_argument('dataset_label', help="This should be a unique label of your gpx set. E.g '2019'")
    args = parser.parse_args()

    return (args.database, args.dataset_label)


def create_extend_metadata(directory, filename, label):

    fpath = os.path.join(directory, filename)
    
    # Create file if it is not existing
    if os.path.exists(fpath):

        with open(fpath, 'r') as fp:
            mdata = json.load(fp)

    else:

        mdata = []


    # Insert label at beginning of list if not in list
    if label not in mdata:
        print("Adding {} to {}".format(label, fpath))
        mdata.insert(0, label)
    else:
        print("Label {} is already in {}".format(label, fpath))

    # write file
    print("Writing {}".format(fpath))
    with open(fpath, 'w') as fp:
        json.dump(mdata, fp)


###################################################
if __name__ == "__main__":
    # execute only if run as a script
    main()
