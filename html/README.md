# How to build the static content

## Background

We are using *parcel* to bundle html, javascript, css. It is generating the smallest possible subset of js code of our dependent libraries to be deployed on production server. This improves performance and stores libraries on our server instead of third party servers.

## Prerequisites

* Install node.js ( Tested with node 10.15.0 and npm 6.4.1 )

## Steps

1. cd to subdirectory `html`
2. Run `npm install`
3. Run `npm run pretest` to run linter
4. Run `npm start` to start development server on port 1234
5. Run `npm run build` to produce packed html / js / css files in `dist` subdirectory
6. Copy contents of `dist` folder to production http server

##
References

* http://openlayers.org/en/latest/doc/tutorials/bundle.html
* https://parceljs.org/
* https://eslint.org/ 
