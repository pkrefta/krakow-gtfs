import re
from bs4 import BeautifulSoup

HOUR_LABEL_CELL_RE = re.compile('  Godzina   ')

# Sundays w tutejszej nomenkulutrze oznacza swieta

HEADERS_STANDARD = 'standard'
HEADERS_WITHOUT_SUNDAY = 'without-sunday'
HEADERS_SATURDAY_SUNDAY = 'saturday-sunday'
HEADERS_WORKDAYS = 'workdays'
HEADERS_SUNDAYS = 'sundays'
HEADERS_WORKDAYS_SUNDAYS = 'workdays-sundays'
HEADERS_ALL_DAYS = 'all-days'
HEADERS_NIGHT_1 = '5/6-6/7__1/2-4/5__7/1'
HEADERS_NIGHT_2 = '5/6-6/7'
HEADERS_NIGHT_3 = '4/5__5/6-6/7__7/1'
HEADERS_NIGHT_4 = '1/2-4/5__5/6-6/7__7/1'
HEADERS_NIGHT_5 = '1/2-2/3-3/4'

# Po tym co znajduje sie komorkach wyciagamy w ktore dni jezdzi ktory crap

RECOGNIZED_HEADERS = {
    HEADERS_STANDARD: ['Godzina', 'Dzień powszedni', 'Soboty', 'Święta', ''],
    HEADERS_WITHOUT_SUNDAY: ['Godzina', 'Dzień powszedni', 'Soboty', ''],
    HEADERS_SATURDAY_SUNDAY: ['Godzina',  'Soboty', 'Święta', ''],
    HEADERS_WORKDAYS: ['Godzina',  'Dzień powszedni', ''],
    HEADERS_SUNDAYS: ['Godzina', 'Święta', ''],
    HEADERS_WORKDAYS_SUNDAYS: ['Godzina', 'Dzień powszedni', 'Święta', ''],
    HEADERS_ALL_DAYS: ['Godzina', 'Wszystkie dni tygodnia', ''],
    HEADERS_NIGHT_1: ['Godzina', 'Pt/Sob-Sob/Nd', 'Pon/Wt - Czw/Pt', 'Nd/Pon', ''],
    HEADERS_NIGHT_2: ['Godzina', 'Pt/Sob-Sob/Nd', ''],
    HEADERS_NIGHT_3: ['Godzina', 'Czw/Pt', 'Pt/Sob-Sob/Nd', 'Nd/Pon', ''],
    HEADERS_NIGHT_4: ['Godzina', 'Pon/Wt - Czw/Pt', 'Pt/Sob-Sob/Nd', 'Nd/Pon', ''],
    HEADERS_NIGHT_5: ['Godzina', 'Pon/Wt, Wt/Śr, Śr/Czw', ''],
}

# {'100__1__1': ['Godzina', 'Dzień powszedni', 'Soboty', 'Święta', ''],
#  '132__1__1': ['Godzina', 'Dzień powszedni', 'Soboty', ''],
#  '142__1__1': ['Godzina', 'Soboty', 'Święta', ''],
#  '149__1__1': ['Godzina', 'Dzień powszedni', ''],
#  '212__1__24': ['Godzina', 'Dzień powszedni', 'Święta', ''],
#  '601__1__1': ['Godzina', 'Wszystkie dni tygodnia', ''],
#  '605__1__1': ['Godzina', 'Pt/Sob-Sob/Nd', 'Pon/Wt - Czw/Pt', 'Nd/Pon', ''],
#  '605__1__15': ['Godzina', 'Pt/Sob-Sob/Nd', ''],
#  '62__1__1': ['Godzina', 'Czw/Pt', 'Pt/Sob-Sob/Nd', 'Nd/Pon', ''],
#  '637__1__1': ['Godzina', 'Pon/Wt - Czw/Pt', 'Pt/Sob-Sob/Nd', 'Nd/Pon', ''],
#  '662__1__1': ['Godzina', 'Pon/Wt, Wt/Śr, Śr/Czw', ''],
#  '754__1__22': ['Godzina', 'Święta', '']}


def generate_days_data_from_headers():
    pass


# trzeba dodac obsluge tresci w komorkach naglowkowych
def get_departures_from_html(file_content):
    soup = BeautifulSoup(file_content, 'html.parser')

    godzina_cell = soup.find_all(text=HOUR_LABEL_CELL_RE)[0]

    deps_table_rows = godzina_cell.parent.parent.parent.select('tr')

    workdays = {}
    saturdays = {}
    holidays = {}

    def get_cell_content(cell):
        return cell.contents[0].strip()

    def get_cell_minutes(cell_content):
        if len(cell_content) > 0:
            items = cell_content.split(' ')

            if len(items) > 0:
                out = []
                for item in items:
                    if item.isdigit():
                        out.append(int(item))
                    else:
                        minute = int(item[0:2])
                        letter = item[2]
                        out.append((minute, letter))

                return out

        return []

    headers = list(map(lambda x: x.contents[0].strip(), deps_table_rows[0].select('td')))

    # print(list(headers))

    # get rows with hours and skip header & bottom shit
    for row in deps_table_rows[1:-2]:
        cells = row.select('td')

        hour_cell_content = get_cell_content(cells[0])

        if hour_cell_content.isdigit():
            hour = int(hour_cell_content)

            if headers == NORMAL_HEADERS:
                workdays_cell_content = get_cell_content(cells[1])
                saturday_cell_content = get_cell_content(cells[2])
                holiday_cell_content = get_cell_content(cells[3])

                workdays[hour] = get_cell_minutes(workdays_cell_content)
                saturdays[hour] = get_cell_minutes(saturday_cell_content)
                holidays[hour] = get_cell_minutes(holiday_cell_content)

            if headers == WITHOUT_HOLIDAYS_HEADERS:
                workdays_cell_content = get_cell_content(cells[1])
                saturday_cell_content = get_cell_content(cells[2])

                workdays[hour] = get_cell_minutes(workdays_cell_content)
                saturdays[hour] = get_cell_minutes(saturday_cell_content)

    if headers == WITHOUT_HOLIDAYS_HEADERS:
        holidays = None

    return {
        'workdays': workdays,
        'saturdays': saturdays,
        'holidays': holidays,
        'headers': headers,
    }

