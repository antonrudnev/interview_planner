FROM osrm/osrm-backend:v5.22.0

ARG map_url=https://download.geofabrik.de/north-america/us/district-of-columbia-latest.osm.pbf

RUN mkdir -p /data

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates 

RUN wget -O /data/map.osm.pbf $map_url 

RUN /usr/local/bin/osrm-extract -p /opt/car.lua /data/map.osm.pbf && \
    /usr/local/bin/osrm-partition /data/map.osrm && \
    /usr/local/bin/osrm-customize /data/map.osrm

EXPOSE 5000

WORKDIR /opt

CMD /usr/local/bin/osrm-routed --algorithm mld /data/map.osrm

