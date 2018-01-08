psql -c "drop database if exists gistest;"
psql -c "create database gistest;"
psql -d gistest -c "create extension postgis;"

