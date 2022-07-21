import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flight_data import FlightData

load_dotenv()


class FlightManager:
    locations_url = 'https://tequila-api.kiwi.com/locations/query'
    search_url = 'https://tequila-api.kiwi.com/v2/search'
    headers = {'apikey': os.getenv('TEQUILA_APIKEY')}
    date_format = '%d/%m/%Y'

    def __init__(self):
        self.flights = []

    def get_iata_code(self, city):
        params = {
            'term': city,
            'location_types': 'city',
            'limit': 1
        }
        response = requests.get(
            url=self.locations_url,
            params=params,
            headers=self.headers,
        )
        response.raise_for_status()

        return response.json()['locations'][0]['code']

    def search(self, codes):
        for code in codes:
            try:
                search_url = 'https://tequila-api.kiwi.com/v2/search'
                tomorrow = (datetime.today() + timedelta(days=1)) \
                    .strftime(self.date_format)
                six_months = (datetime.today() + timedelta(days=182)) \
                    .strftime(self.date_format)
                params = {
                    'fly_from': 'DTW',
                    'fly_to': code,
                    'date_from': tomorrow,
                    'date_to': six_months,
                    'nights_in_dst_from': 7,
                    'nights_in_dst_to': 28,
                    'flight_type': 'round',
                    'curr': 'USD',
                    'asc': 1,
                    'limit': 1
                }

                response = requests.get(
                    url=search_url,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()['data'][0]
                city_from = data['cityFrom']
                fly_from = data['flyFrom']
                city_to = data['cityTo']
                fly_to = data['flyTo']
                price = int(data['price'])
                route = data['route']
                leave_date = route[0]['local_arrival'].split('T')[0]
                return_date = route[-1]['local_arrival'].split('T')[0]

                flight = FlightData(
                    city_from=city_from,
                    fly_from=fly_from,
                    city_to=city_to,
                    fly_to=fly_to,
                    price=price,
                    leave_date=leave_date,
                    return_date=return_date
                )

                self.flights.append(flight)
            except IndexError:
                self.flights.append({})
