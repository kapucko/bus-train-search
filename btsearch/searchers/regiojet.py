import time
from datetime import timedelta
import unicodedata
import json

import requests
from bs4 import BeautifulSoup
from redis import StrictRedis

from ..exceptions import DestinationNotFoundException
from ..utils import slugify, time_helper

REDIS_CONF = {
    'host': '37.139.6.125',
    'password': 'wuaei44INlFurP2qMlng89HmH38',
    'port': 6379
}


class RegioJetSearcher:
    DESTINATION_URL = 'https://www.studentagency.cz/data/wc/ybus-form/destinations-en.json'
    HOMEPAGE_URL = 'https://www.regiojet.com/en'
    SEARCH_URL = 'https://bustickets.regiojet.com/Booking/from/{from_}/to/{to}/tarif/REGULAR/departure/{date_from}/retdep/{date_to}/return/false?0'
    HACK_QUERY = '-1.IBehaviorListener.0-mainPanel-routesPanel&_={timestamp}'

    def __init__(self):
        self.cache = StrictRedis(**REDIS_CONF)

    def get_destination_id(self, destination_name):
        destination_name_slug = slugify(destination_name)

        # at first, try cache store
        cache_city_key = 'city_id_{city_slug}'.format(city_slug=destination_name_slug)
        city_id = self.cache.get(cache_city_key)
        if city_id:
            return city_id.decode(), destination_name

        destinations = requests.get(self.DESTINATION_URL).json()['destinations']
        for country in destinations:
            for city in country['cities']:
                for station in city['stations']:
                    if slugify(station['fullname']) == destination_name_slug or slugify(
                            station['name']) == destination_name_slug:
                        self.cache.set(cache_city_key, station['id'], 3600)
                        return station['id'], station['fullname']
                    for alias in station['aliases']:
                        if slugify(alias) == destination_name_slug:
                            self.cache.set(cache_city_key, station['id'], 3600)
                            return station['id'], station['fullname']

        raise DestinationNotFoundException()

    def get_route(self, from_, to, date, passengers=1):
        s = requests.session()
        s.get(self.DESTINATION_URL)
        from_id, from_name = self.get_destination_id(from_)
        to_id, to_name = self.get_destination_id(to)


        connection_key_template = 'connection_{from_id}_{to_id}_{date}'
        connection_key = connection_key_template.format(from_id=from_id, to_id=to_id, date=date.strftime('%Y-%m-%d'))
        cached_result = self.cache.get(connection_key)
        if cached_result:
            result = json.loads(cached_result)
            return result

        search_url = self.SEARCH_URL.format(from_=from_id, to=to_id, date_from=date.strftime('%Y%m%d'),
                                            date_to=date.strftime('%Y%m%d'))
        s.cookies.set('currency', 'CZK')
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
            elif element.name == 'div' and all(x in element.attrs['class'] for x in ['routeSummary', 'free']) \
                    and correct_day:

                price = element.select('div.col_price')
                if not price:
                    price = element.select('div.col_price_no_basket_image')

                time_format = '%Y-%m-%d %H:%M:%S'
                departure = time_helper(date, element.select('div.col_depart')[0].text)
                arrival = time_helper(date, element.select('div.col_arival')[0].text)
                if arrival < departure:
                    # arrival is after midnight, so plus one day...
                    arrival = arrival + timedelta(days=1)

                d = {'departure': departure.strftime(time_format),
                     'arrival': arrival.strftime(time_format),
                     'from': from_name,
                     'to': to_name,
                     'from_id': from_id,
                     'to_id': to_id,
                     # 'type': 'TODO',
                     'free_seats': element.select('div.col_space')[0].get_text().strip(),
                     'price': unicodedata.normalize('NFKD', price[0].find_all('span')[
                         0].get_text().strip()),
                     }
                results.append(d)
        if results:
            self.cache.setex(connection_key, 3600, json.dumps(results))
            print(connection_key)
        return results
