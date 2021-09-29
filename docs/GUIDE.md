```shell
ssh root@180.148.1.190 / vnttsneW@1808 /  cd ~/VNTT/BecaGIS_GeoNode

source ~/VNTT/.virtualenvs/BecaGIS_GeoNode/bin/activate

docker-compose -f docker-compose.async.yml -f docker-compose.development.yml -f docker-compose-qgis-server.yml --env-file ./.env.dev up -d
docker-compose -f docker-compose.async.yml -f docker-compose.development.yml --env-file ./.env.dev up -d

docker-compose -f docker-compose.yml -f docker-compose.override.localhost.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.override.geoportal.yml up -d
```