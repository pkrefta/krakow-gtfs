import csv

from bs4 import BeautifulSoup

from datetime import datetime
from pprint import pprint

from utils import str_2_b64, write_output_csv
from base_data import AGENCIES, CALENDARS


today = datetime.now().strftime('%Y%m%d')


def stop_code(stop_name):
    out = str_2_b64(stop_name)

    while out[-1] == '=':
        out = out[0:-1]

    return out


def build_stops():
    out = {}
    out_for_csv = []
    stop_id = 1

    with open('data/przystanki.csv') as stopscsv:
        reader = csv.reader(stopscsv)

        for row in reader:
            out[row[0]] = {
                'lat': float(row[1]),
                'lng': float(row[2]),
                'code': stop_code(row[0]),
            }

            out_for_csv.append({
                'stop_id': stop_id,
                'stop_name': row[0],
                'stop_lat': float(row[1]),
                'stop_lng': float(row[2]),
            })

            stop_id = stop_id + 1

        return out, out_for_csv


def build_routes():
    with open('cache/linie.html') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

        lines = soup.select('a[class^="linia"]')

        out = {}
        out_for_csv = []
        route_id = 1

        for line in lines:
            cls = line.get('class')[0].strip()

            # print(line.get('style').strip())

            code = '' if len(cls) == 5 else cls[-1]
            nr = line.string.strip()
            href = line.get('href')
            vehicle_type = 0 if len(nr) == 2 else 3
            wheelchair_accessible = line.get('style').strip() == 'border: 3px solid deepskyblue;'
            route_desc = ''

            normal = build_trip_details(nr, '1')
            ret = build_trip_details(nr, '2')

            normal_stops = ' - '.join(map(lambda x: x['name'], normal['stops'])) if normal else None
            ret_stops = ' - '.join(map(lambda x: x['name'], ret['stops'])) if ret else None

            if normal and ret:
                long_name = '%s - %s|%s - %s' % (normal['from'], normal['to'], ret['from'], ret['to'])
                route_desc = '%s|%s' % (normal_stops, ret_stops)
            elif normal:
                long_name = '%s - %s' % (normal['from'], normal['to'])
                route_desc = normal_stops
            elif ret:
                long_name = '%s - %s' % (ret['from'], ret['to'])
                route_desc = ret_stops

            out[nr] = {
                'id': route_id,
                'nr': nr,
                'href': href,
                'code': code,
                'vehicle_type': vehicle_type,
                'wheelchair_accessible': wheelchair_accessible,
                'route_long_name': long_name,
                'route_desc': route_desc,
                'trips': {
                    'normal': normal,
                    'return': ret,
                }
            }

            out_for_csv.append({
                'route_id': route_id,
                'route_short_name': nr,
                'route_long_name': long_name,
                'route_desc': route_desc,
                'route_type': vehicle_type,
            })

            route_id = route_id + 1

        return out, out_for_csv


def build_trip_details(route_nr, direction):
    fts = '  text-align: left; white-space: nowrap; border-left: solid black; border-radius: 20px; padding: 10px; '
    file_name = 'cache/%s__%s.html' % (route_nr, direction)

    print('reading - ' + file_name)

    with open(file_name) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

        time_table = soup.select('table[style=" width: 700px; "]')

        has_timetable = len(time_table) > 0

        if has_timetable:
            from_to = soup.select('div[style="' + fts + '"]')[0]

            from_txt = from_to.contents[0].strip().replace('Od: ', '')
            to_txt = from_to.contents[2].strip().replace('Do: ', '')

            out = {
                'from': from_txt,
                'to': to_txt,
                'has_tariff_border': False,
            }

            stops_table = soup.select('table[style=" "]')[0]

            short_description = soup.select('div.borderTB')[0].contents[2].strip()

            stops = []
            line_sequence = 0

            for row in stops_table.select('tr'):
                cells = row.select('td')

                # Wiersz z granica taryf
                if len(cells) == 1 and cells[0].contents[2].strip() == 'GRANICA TARYF':
                    out['has_tariff_border'] = True
                    continue

                name_cell = cells[0]
                link_cell = cells[1]
                stop_details_href = None
                line_stop_href = None
                nz_cell = None

                if len(cells) == 3:
                    nz_cell = cells[2]

                name_spans = name_cell.select('span')

                if len(name_spans) > 0:
                    line_stop_href = name_cell.select('a')[0].get('href')
                    stop_name = name_spans[0].contents[0].strip()
                else:
                    stop_name = name_cell.contents[0].strip()

                stop_details_href = link_cell.select('a')[0].get('href')

                if nz_cell:
                    on_request = nz_cell.contents[0].strip() == 'NZ'
                else:
                    on_request = False

                line_sequence = line_sequence + 1

                stops.append({
                    'name': stop_name,
                    'line_stop_href': line_stop_href,
                    'stop_details_href': stop_details_href,
                    'on_request': on_request,
                    'line_sequence': line_sequence,
                })

            out['short_description'] = short_description

            out['stops'] = stops

            return out
        else:
            return None


stops, stops_for_csv = build_stops()

routes_data, routes_for_csv = build_routes()

# pprint(routes_data['6'])

# Tu trzeba zrobic wyciaganie szczegolow route'a

write_output_csv('agency.txt', AGENCIES)
write_output_csv('calendar.txt', CALENDARS)
write_output_csv('stops.txt', stops_for_csv)
write_output_csv('routes.txt', routes_for_csv)
