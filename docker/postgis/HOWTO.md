## How to run a postgis database

docker create --name postgis -e POSTGRES_PASSWORD=an3fang -p 5432:5432 --network dn postgis/postgis:12-3.0-alpine

docker start postgis

