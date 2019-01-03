import json
import logging
import re
import time
import urllib.request
from urllib.parse import quote

from flask import Flask, abort, jsonify, redirect, render_template, request

from filelock import FileLock
from settings import MAP_SERVER_HOST, TEST_POINTS, TRIP_SERVER_HOST

app = Flask(__name__)

lock = FileLock("lock")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('usage.log')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(clientip)s - %(httpmethod)s - %(message)s, %(useragent)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def build_trip_url(trip_server_host, geo_points):
    trip_url = f'{trip_server_host}/trip/v1/driving/'
    for p in geo_points:
        trip_url += f'{p[1]},{p[0]};'
    trip_url = trip_url[:-1] + '?roundtrip=true&source=any&destination=any'
    return trip_url


def build_map_url(map_server_host, geo_points):
    map_url = f'{map_server_host}/?'
    for p in geo_points:
        map_url += f'&loc={p[0]}%2C{p[1]}'
    map_url += f'&loc={geo_points[0][0]},{geo_points[0][1]}'
    return map_url


@app.route('/', methods=['GET', 'POST'])
def input_points():
    logger.info(f'Open start page',
                extra={'clientip': request.remote_addr, 'httpmethod': request.method, 'useragent': request.user_agent})
    if request.method == "POST":
        logger.info(f'Invoked "{request.form["action"]}"',
                    extra={'clientip': request.remote_addr, 'httpmethod': request.method,
                           'useragent': request.user_agent})
        geo_points = [re.split(r'[^0-9.-]', v)
                      for k, v in request.form.to_dict().items() if k.startswith('point') and v]
        if request.form['action'] == 'view':
            view_input_url = build_map_url(MAP_SERVER_HOST, geo_points)
            return redirect(view_input_url)
        elif request.form['action'] == 'optimize':
            trip_url = build_trip_url(TRIP_SERVER_HOST, geo_points)
            with urllib.request.urlopen(trip_url) as response:
                way_points = json.loads(response.read())['waypoints']
                trip_points = [{'index': i, 'order': w['waypoint_index']} for i, w in enumerate(way_points)]
                sorted_geo_points = [geo_points[p['index']] for p in sorted(trip_points, key=lambda x: x['order'])]
                view_trip_url = build_map_url(MAP_SERVER_HOST, sorted_geo_points)
                return redirect(view_trip_url)
    return render_template('input_points.html', geo_points=TEST_POINTS)


def search_nominatim(query):
    quoted = quote(query)
    url = f'https://nominatim.openstreetmap.org/search/{quoted}?limit=1&viewbox=-83.75,36.52,-74.96,39.73&bounded=1&addressdetails=1&countrycodes=us&format=json'
    with lock:
        with urllib.request.urlopen(url) as response:
            geo = json.loads(response.read())
            time.sleep(1)
            return geo


@app.route('/api/search/<query>', methods=['GET'])
def geocoding(query):
    try:
        logger.info(f'Geocoding for "{query}"', extra={'clientip': request.remote_addr, 'httpmethod': request.method,
                                                       'useragent': request.user_agent})
        location = search_nominatim(query)[0]
        lat = location['lat']
        lon = location['lon']
        address = location['address']
        if address['state'] not in ['D.C.', 'Maryland', 'Virginia']:
            raise Exception('Only DC, MD, and VA are supported now')
        display_address = ', '.join(p for p in [address.pop('house_number',
                                                            address.pop(next(iter(address.keys())), None)),
                                                address.pop('road', address.pop('pedestrian', None)),
                                                address.pop('city', address.pop('locality', None)),
                                                address.pop('state', None)] if p)
        return jsonify({'lat': lat, 'lon': lon, 'address': display_address})
    except Exception as e:
        abort(404)


if __name__ == '__main__':
    app.run()
