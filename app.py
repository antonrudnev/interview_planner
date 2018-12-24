import re
import json
import webbrowser
import urllib.request
from flask import Flask, request, render_template

from settings import MAP_SERVER_HOST, TRIP_SERVER_HOST, TEST_POINTS

app = Flask(__name__)


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
    if request.method == "POST":
        geo_points = [re.split(r'[^0-9.-]', p) for p in request.form.to_dict().values()]
        trip_url = build_trip_url(TRIP_SERVER_HOST, geo_points)
        view_input_url = build_map_url(MAP_SERVER_HOST, geo_points)
        webbrowser.open_new_tab(view_input_url)

        with urllib.request.urlopen(trip_url) as response:
            way_points = json.loads(response.read())['waypoints']
            trip_points = [{'index': i, 'order': w['waypoint_index']} for i, w in enumerate(way_points)]
            sorted_geo_points = [geo_points[p['index']] for p in sorted(trip_points, key=lambda x: x['order'])]
            view_trip_url = build_map_url(MAP_SERVER_HOST, sorted_geo_points)
            webbrowser.open_new_tab(view_trip_url)

    return render_template('input_points.html', geo_points=TEST_POINTS)


if __name__ == '__main__':
    app.run()
