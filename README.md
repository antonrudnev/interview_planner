# Interviewers assignment and navigation

List visiting points (supports geocoding):
![](/images/points.png)

Output optimal route and navigation details:
![](/images/route.png)


## Startup guide:

1. Download openstreetmap data in [.osm.pbf](https://download.geofabrik.de/) format
2. Use [osmium-merge](https://docs.osmcode.org/osmium/latest/osmium-merge.html) to merge several files .osm.pbf if they are
3. Follow detailed [osrm-project](https://hub.docker.com/r/osrm/osrm-backend/) instructions to startup osrm-backend and osrm-frontend docker containers:

```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/dc-md-va.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/dc-md-va.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/dc-md-va.osrm
```
```bash
docker run -d -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/dc-md-va.osrm
docker run -d -p 9966:9966 osrm/osrm-frontend
```
4. Start flask application
