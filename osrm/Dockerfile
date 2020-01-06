FROM osrm/osrm-backend:v5.22.0 as prep

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates osmium-tool 

WORKDIR /data

COPY urls.txt .

RUN wget -i urls.txt

RUN find -name '*.osm.pbf' | xargs osmium merge -o map.osm.pbf 

RUN /usr/local/bin/osrm-extract -p /opt/car.lua map.osm.pbf && \
    /usr/local/bin/osrm-partition map.osrm && \
    /usr/local/bin/osrm-customize map.osrm

RUN rm *.osm.pbf

FROM osrm/osrm-backend:v5.22.0

COPY --from=prep /data /data

EXPOSE 5000

WORKDIR /opt

CMD /usr/local/bin/osrm-routed --algorithm mld /data/map.osrm

