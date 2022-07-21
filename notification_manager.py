import requests
import os
from dotenv import load_dotenv
from flight_data import FlightData

load_dotenv()


class NotificationManager:
    flight_bot = os.getenv('FLIGHT_NOTIFICATION_BOT')
    chat_id = os.getenv('CHAT_ID')

    def send_message(self, flight: FlightData):
        message = f'''
    LOW PRICE ALERT! ONLY ${flight.price} to fly 
    from {flight.city_from}-{flight.fly_from} to {flight.city_to}-{flight.fly_to}, 
    from {flight.leave_date} to {flight.return_date}
    '''
        url = 'https://api.telegram.org/bot' + self.flight_bot + '/sendMessage?chat_id=' \
              + self.chat_id + '&parse_mode=Markdown&text=' + message
        response = requests.get(url)
        response.raise_for_status()
