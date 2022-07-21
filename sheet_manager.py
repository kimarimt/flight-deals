import requests
import os
from dotenv import load_dotenv

load_dotenv()


class SheetManager:
    headers = {'Authorization': os.getenv('SHEET_HEADER')}
    prices_sheet_url = 'https://api.sheety.co/73f31757b57e0257d2e45dee0591bec5/flightDeals/prices'
    update_row_url = 'https://api.sheety.co/73f31757b57e0257d2e45dee0591bec5/flightDeals/prices/'

    def __init__(self):
        self.data = []
        self.get_data()

        self.codes = [entry['iataCode'] for entry in self.data]
        self.lowest_prices = [entry['lowestPrice'] for entry in self.data]
        self.cities = [entry['city'] for entry in self.data]

    def get_data(self):
        response = requests.get(
            url=self.prices_sheet_url,
            headers=self.headers,
        )
        response.raise_for_status()

        self.data = [entry for entry in response.json()['prices']]

    def update_codes_row(self, codes):
        starting_row = 2

        for code in codes:
            row_url = f'{self.update_row_url}{starting_row}'
            body = {
                'price': {
                    'iataCode': code
                }
            }
            response = requests.put(
                url=row_url,
                headers=self.headers,
                json=body
            )
            response.raise_for_status()

            starting_row += 1
