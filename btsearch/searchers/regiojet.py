import time
import unicodedata

import requests
from bs4 import BeautifulSoup

from ..exceptions import DestinationNotFoundException
from ..utils import slugify


class RegioJetSearcher:
    DESTINATION_URL = 'https://www.studentagency.cz/data/wc/ybus-form/destinations-en.json'
    HOMEPAGE_URL = 'https://www.regiojet.com/en'
    SEARCH_URL = 'https://bustickets.regiojet.com/Booking/from/{from_}/to/{to}/tarif/REGULAR/departure/{date_from}/retdep/{date_to}/return/false?0'
    HACK_QUERY = '-1.IBehaviorListener.0-mainPanel-routesPanel&_={timestamp}'

    def __init__(self):
        self.destinations = requests.get(self.DESTINATION_URL).json()['destinations']

    def get_destination_id(self, destination_name):
        destination_name = slugify(destination_name)
        for country in self.destinations:
            for city in country['cities']:
                for station in city['stations']:
                    if slugify(station['fullname']) == destination_name or slugify(station['name']) == destination_name:
                        return station['id'], station['fullname']
                    for alias in station['aliases']:
                        if slugify(alias) == destination_name:
                            return station['id'], station['fullname']

        raise DestinationNotFoundException()

    def get_route(self, from_, to, date, passengers=1):
        s = requests.session()

        s.get(self.DESTINATION_URL)
        from_id, from_name = self.get_destination_id(from_)
        to_id, to_name = self.get_destination_id(to)

        search_url = self.SEARCH_URL.format(from_=from_id, to=to_id, date_from=date.strftime('%Y%m%d'),
                                            date_to=date.strftime('%Y%m%d'))
        s.get(search_url)
        search_url += self.HACK_QUERY.format(timestamp=int(time.time()))
        html_response = s.get(search_url).content

        soup = BeautifulSoup(html_response, 'html.parser')
        results = []

        routes_root = soup.select('div#ticket_lists div div div.left_column div div')[0]
        correct_day = False
        for element in routes_root.children:
            if isinstance(element, str):
                continue

            if element.name == 'h2':
                d = date.strftime('%d/%m/%y')
                if element.text.find(d) != -1:
                    correct_day = True
                else:
                    correct_day = False
            elif element.name == 'div' and all(x in element.attrs['class'] for x in ['routeSummary', 'free'])\
                    and correct_day:
                d = {'departure': element.select('div.col_depart')[0].text,
                     'arrival': element.select('div.col_arival')[0].text,
                     'from': from_name,
                     'to': to_name,
                     'from_id': from_id,
                     'to_id': to_id,
                     'type': 'TODO',
                     'free_seats': element.select('div.col_space')[0].get_text().strip(),
                     'price': unicodedata.normalize('NFKD', element.select('div.col_price')[0].find_all('span')[
                         0].get_text().strip()),
                     }
                results.append(d)

        return results
