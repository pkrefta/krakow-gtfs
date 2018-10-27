from datetime import datetime

today = datetime.now().strftime('%Y%m%d')

AGENCIES = [
    {
        'agency_name': 'MPK S.A. w Krakowie',
        'agency_url': 'http://rozklady.mpk.krakow.pl/',
        'agency_timezone': 'Europe/Warsaw',
    },
]


CALENDARS = [
    {
        'service_id': '1',
        'monday': 1,
        'tuesday': 1,
        'wednesday': 1,
        'thursday': 1,
        'friday': 1,
        'saturday': 1,
        'sunday': 1,
        'start_date': today,
        'end_date': today,
    },
]