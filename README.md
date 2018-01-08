# gpx_track_neighborhood

How close are my gpx tracks?

## Goal

This project does calculate proximity of multiple tracks from gpx files

## Howto

* Set up postgis server on localhost
* Run gpx2postgis.py <source_dir> <target_dbname>. The target db will be created or overwritten
* Run frequency_calc.py
* Result is in frequency table - each trackpoint has a counter on how many other tracks are nearby

## Dependencies

* python 3.6 or higher
* psycopg2 python library for postgres access
* gpsbabel
* GDAL
* posgtres with postgis extension
* Tested on windows, but may run on linux too
