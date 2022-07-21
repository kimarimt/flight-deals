import requests
import os
from dotenv import load_dotenv

load_dotenv()


class SheetManager:
    headers = {'Authorization': os.getenv('SHEET_HEADER')}
    user_sheet_url = 'https://api.sheety.co/73f31757b57e0257d2e45dee0591bec5/flightDeals/users'
    prices_sheet_url = 'https://api.sheety.co/73f31757b57e0257d2e45dee0591bec5/flightDeals/prices'

    def __init__(self):
        self.prices_data = []
        self.emails = []
        self.get_data()

        self.codes = [entry['iataCode'] for entry in self.prices_data]
        self.lowest_prices = [entry['lowestPrice'] for entry in self.prices_data]
        self.cities = [entry['city'] for entry in self.prices_data]

    def get_data(self):
        response = requests.get(
            url=self.prices_sheet_url,
            headers=self.headers,
        )
        response.raise_for_status()

        self.prices_data = [entry for entry in response.json()['prices']]

        response = requests.get(
            url=self.user_sheet_url,
            headers=self.headers
        )
        response.raise_for_status()

        self.emails = [entry['email'] for entry in response.json()['users']]

    def update_codes_row(self, codes):
        starting_row = 2

        for code in codes:
            row_url = f'{self.prices_sheet_url}{starting_row}'
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

    def add_user(self):
        print('Welcome to the Python Flight Club')
        print('We email you the cheapest round trip flights')
        first_name = input('Enter your first name: ')
        last_name = input('Enter your last name: ')
        email = input('Enter your email: ')
        verify_email = input('Reenter email to verify: ')

        if first_name == '' or last_name == '' or email == '' or verify_email == '':
            print('please fill out all required fields')
            self.add_user()

        if email != verify_email:
            print('email fields must match')
            self.add_user()

        body = {
            'user': {
                'firstName': first_name,
                'lastName': last_name,
                'email': email
            }
        }
        response = requests.post(
            url=self.user_sheet_url,
            headers=self.headers,
            json=body
        )
        response.raise_for_status()

        print('Success! You are subscribed to the Flight Club')

