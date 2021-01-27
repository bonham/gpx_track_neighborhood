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
* Define env variable GPX_SNIP_COORDS with space separated list of lat lon locations for all points in 1km distance to cut out: 'D.dddd,D.dddd D.dddd,D.dddd'
* Run <strong>1-proximity-calc.py</strong> to calculate intersections of gpx tracks.kk
* Run <strong>2-export-geojson.py</strong> \<database> \<dataset_label> to create json files for html pages. Your geojson dataset will be in subdir html/static/geojson/<dataset_label>. Read about different export [modes](MODES.md)
* Repeat steps from above for each dataset you have. Each new dataset_label will create a new subdirectory and a new button on the webpage.
* cd to subdirectory `html` and run `npm run build`. See [details here](html/README.md)

The finished web pages are in subdirectory <strong>html/dist</strong>. Push all files from that folder to a webserver and open it in browser. To view the files locally, use npm start. This will start the parcel server.

## Platforms

Developed and tested on Windows. Will very likely run on linux too.
## Dependencies

* Install postgres from https://www.postgresql.org ( tested with version 12, should also run with 10 or 11)
* Install postgis 3.0.3 from https://postgis.net. Should also work with older versions e.g. 2.4.2
* Install python 3.6 or higher
* Install python requirements with "pip install -r requirements.txt"
* Install node.js 12.x.x ( with npm )
* cd to `html` subdir. Then install all dependencies in [package.json](html/package.json) by running `npm install`
