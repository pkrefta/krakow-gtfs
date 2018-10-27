import requests
import os

from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint

from utils import file_put_contents


now = datetime.now()
today = now.strftime('%Y%m%d')

COOKIES = {
    'ROZKLADY_AB': '0',
    'ROZKLADY_JEZYK': 'PL',
    'ROZKLADY_WIDTH': '2000',
    'ROZKLADY_OSTATNIA': str(int(now.timestamp())),
    'ROZKLADY_WIZYTA': '1'
}


# with open('cache/linie.html') as f:
#     soup = BeautifulSoup(f.read(), 'html.parser')
#
#     lines = soup.select('a[class^="linia"]')
#
#     url_tpl = 'http://rozklady.mpk.krakow.pl/?lang=PL&rozklad=%s&linia=%s'
#
#     for line in lines:
#         nr = line.string.strip()
#
#         for route in [nr + '__1', nr + '__2']:
#             file = 'cache/%s.html' % route
#             url = url_tpl % (today, route)
#
#             if os.path.exists(file):
#                 print('ALREADY CACHED -> ' + url)
#             else:
#                 r = requests.get(url, cookies=COOKIES)
#
#                 if r.status_code == 200:
#                     file_put_contents(file, r.text)
#                     print('CACHED -> ' + url)
#                 else:
#                     print('ERROR at ' + url)
#                     exit()
#
#                 sleep(1)
#
#     print('Lines info cached')

with open('cache/linie.html') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

    lines = soup.select('a[class^="linia"]')

    for line in lines:
        nr = line.string.strip()

        for route in [nr + '__1', nr + '__2']:
            fx = 'cache/%s.html' % route
            with open(fx) as f2:
                soup2 = BeautifulSoup(f2.read(), 'html.parser')

                stops_hrefs = []

                time_table = soup2.select('table[style=" width: 700px; "]')

                has_timetable = len(time_table) > 0

                if has_timetable:
                    stops_table = soup2.select('table[style=" "]')[0]

                    for row in stops_table.select('tr'):
                        cells = row.select('td')

                        if len(cells) == 1 and cells[0].contents[2].strip() == 'GRANICA TARYF':
                            continue

                        name_cell = cells[0]

                        name_spans = name_cell.select('span')

                        if len(name_spans) > 0:
                            line_stop_href = name_cell.select('a')[0].get('href')

                            stops_hrefs.append(line_stop_href)

                if len(stops_hrefs) > 0:
                    print('scanned %s.html - has timetable -> %s' % (route, 'yes' if has_timetable else 'no'))

                    total = len(stops_hrefs)
                    nr  = 1

                    for href in stops_hrefs:
                        tmp = href.split('=')
                        stop_id = tmp[-1]

                        file_name = 'cache/%s.html' % stop_id

                        if not os.path.exists(file_name):
                            r = requests.get(href, cookies=COOKIES)

                            if r.status_code == 200:
                                file_put_contents(file_name, r.text)
                                print('CACHED %s/%s  %s -> %s' % (nr, total, href, file_name))

                                nr = nr + 1

                                sleep(1)
                            else:
                                print('ERROR at ' + url)
                                exit()
                        else:
                            print('istnieje %s' % file_name)

print('Finished')
