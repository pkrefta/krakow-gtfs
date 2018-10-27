import glob
from sys import getsizeof
from pprint import pprint

from departures import get_departures_from_html

from utils import file_get_contents, get_nice_bytes

stops_files = glob.glob('cache/*__*__*.html')

all_departures = {}

stops_files = list(stops_files)

stops_files.sort()

total = len(stops_files)
nr = 1

all_headers = []
all_header_stops = []

for stop_file in stops_files:
    stop_id = stop_file.split('/')[1].split('.')[0]

    pct = round((nr / total) * 100, 4)

    print('%s - %s/%s %s%%' % (stop_file, nr, total, pct))
    html = file_get_contents(stop_file)

    out = get_departures_from_html(html)

    all_departures[stop_id] = out

    if out['headers'] not in all_headers:
        all_header_stops.append(stop_id)
        all_headers.append(out['headers'])

    nr = nr + 1

pprint(dict(zip(all_header_stops, all_headers)))

print('%s %s' % get_nice_bytes(getsizeof(all_departures)))
