import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dataclasses import dataclass

load_dotenv()

# CONSTANTS
FLIGHT_BOT = os.getenv('FLIGHT_NOTIFICATION_BOT')
CHAT_ID = os.getenv('CHAT_ID')
SHEET_HEADERS = {'Authorization': os.getenv('SHEET_HEADER')}
TEQUILA_HEADERS = {'apikey': os.getenv('TEQUILA_APIKEY')}
DATE_FORMAT = '%d/%m/%Y'


# SHEET MANAGER
def get_sheet_data():
    prices_sheet_url = 'https://api.sheety.co/73f31757b57e0257d2e45dee0591bec5/flightDeals/prices'
    response = requests.get(
        url=prices_sheet_url,
        headers=SHEET_HEADERS,
    )
    response.raise_for_status()

    return [entry for entry in response.json()['prices']]


def update_IATA_codes_row(codes):
    update_row_url = 'https://api.sheety.co/73f31757b57e0257d2e45dee0591bec5/flightDeals/prices/'
    starting_row = 2

    for code in codes:
        row_url = f'{update_row_url}{starting_row}'
        body = {
            'price': {
                'iataCode': code
            }
        }
        response = requests.put(
            url=row_url,
            headers=SHEET_HEADERS,
            json=body
        )
        response.raise_for_status()

        starting_row += 1


# TEQUILA MANAGER
@dataclass
class FlightResult:
    city_from: str
    fly_from: str
    city_to: str
    fly_to: str
    price: int
    leave_date: str
    return_date: str


def get_iata_code(city):
    locations_url = 'https://tequila-api.kiwi.com/locations/query'
    params = {
        'term': city,
        'location_types': 'city',
        'limit': 1
    }
    response = requests.get(
        url=locations_url,
        params=params,
        headers=TEQUILA_HEADERS,
    )
    response.raise_for_status()

    return response.json()['locations'][0]['code']


def flight_search(city_code):
    try:
        search_url = 'https://tequila-api.kiwi.com/v2/search'
        tomorrow = (datetime.today() + timedelta(days=1)) \
            .strftime(DATE_FORMAT)
        six_months = (datetime.today() + timedelta(days=182)) \
            .strftime(DATE_FORMAT)
        params = {
            'fly_from': 'DTW',
            'fly_to': city_code,
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
            headers=TEQUILA_HEADERS,
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

        return FlightResult(
            city_from=city_from,
            fly_from=fly_from,
            city_to=city_to,
            fly_to=fly_to,
            price=price,
            leave_date=leave_date,
            return_date=return_date
        )
    except IndexError:
        return {}


# NOTIFICATION MANAGER
def send_message(flight: FlightResult):
    message = f'''
LOW PRICE ALERT! ONLY ${flight.price} to fly 
from {flight.city_from}-{flight.fly_from} to {flight.city_to}-{flight.fly_to}, 
from {flight.leave_date} to {flight.return_date}
'''
    url = 'https://api.telegram.org/bot' + FLIGHT_BOT + '/sendMessage?chat_id=' \
          + CHAT_ID + '&parse_mode=Markdown&text=' + message
    response = requests.get(url)
    response.raise_for_status()


def main():
    prices = get_sheet_data()
    codes = [price['iataCode'] for price in prices]
    lowest_prices = [int(price['lowestPrice']) for price in prices]

    if codes[0] != 'PAR':
        cities = [price['city'] for price in prices]
        iata_codes = [get_iata_code(city) for city in cities]
        update_IATA_codes_row(iata_codes)

    flights = [flight_search(code) for code in codes]

    for i, flight in enumerate(flights):
        if flight == {}:
            continue

        lowest_price = lowest_prices[i]

        if flight.price < lowest_price:
            send_message(flight)


if __name__ == '__main__':
    main()
