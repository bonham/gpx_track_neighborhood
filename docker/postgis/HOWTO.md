## How to run a postgis database
docker volume create postgis_pgdata

docker create --name postgis -e POSTGRES_PASSWORD=xxxxx -p 5432:5432  -v postgis_pgdata:/var/lib/postgis/pgdata --network dn postgis/postgis:12-3.0-alpine

docker start postgis

