# GPX Proximator

* You have a set of gpx tracks
* You want to display them on a map
* You want color coding depending on how often you passed the same roads

The project does calculate proximity of multiple tracks from gpx files. It does prepare static and mobile friendly html pages, including all gps data.

## Howto

* Download the project from github
* Install dependencies from below
* Put all your gpx tracks in a directory
Run all python commands below. Use --help to learn what arguments to provide
* Run <strong>0-simplify-tracks.py</strong>. This will use gpsbabel to reduce gpx tracks.
* Run <strong>1-gpx2postgis.py</strong> \<source_dir> \<target_dbname> to import gpx tracks to database. The database will be created or overwritten.
* Run <strong>2-proximity-calc.py</strong> to calculate intersections of gpx tracks.
* Run <strong>3-category-calc.py</strong> to calculate color categories.
* Run <strong>4-export-geojson.py</strong> \<database> \<dataset_label> to create json files for html pages. Your geojson dataset will be in subdir html/static/geojson/<dataset_label>
* cd to subdirectory `html` and run `npm run build`. See [details here](html/README.md)

The finished web pages are in subdirectory <strong>html/dist</strong>. Push all files from that folder to a webserver and open it in browser. ( Firefox can open it also locally, but not Chrome. For Chrome you can start local webserver from html directory with <strong>startserver.bat</strong>)

## Platforms

Developed and tested on Windows. Will very likely run on linux too.
## Dependencies

* Install postgres 10 from https://www.postgresql.org
* Install postgis 2.4.2 from https://postgis.net
* Install python 3.6 or higher ( python 2.7 may also work )
* Install psycopg2 python library for postgres access
* Install gpsbabel from https://www.gpsbabel.org/
* Install GDAL from http://www.gdal.org/ ( You need ogr2ogr command line tool )
* Install node.js 10.15.0 ( with npm )
* cd to `html` subdir. Then install all dependencies in [package.json](html/package.json) by running `npm install`
