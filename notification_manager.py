import requests
import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
from flight_data import FlightData

load_dotenv()


class NotificationManager:
    flight_bot = os.getenv('FLIGHT_NOTIFICATION_BOT')
    chat_id = os.getenv('CHAT_ID')
    flight_email_key = os.getenv('FLIGHT_EMAIL_KEY')
    email_address = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('APP_PASSWORD')

    def send_sms(self, flight: FlightData):
        append_message = ''
        if flight.via_city != '' and flight.stopovers != 0:
            append_message = f'\nFlight has {flight.stopovers} stopover in {flight.via_city}.'

        message = f'''
LOW PRICE ALERT! ONLY ${flight.price} to fly 
from {flight.city_from}-{flight.fly_from} to {flight.city_to}-{flight.fly_to}, 
from {flight.leave_date} to {flight.return_date}
{append_message}
'''

        url = 'https://api.telegram.org/bot' + self.flight_bot + '/sendMessage?chat_id=' \
              + self.chat_id + '&parse_mode=Markdown&text=' + message
        response = requests.get(url)
        response.raise_for_status()

    def email_users(self, flight: FlightData, emails):
        host = 'smtp.mail.yahoo.com'
        context = ssl.create_default_context()

        with smtplib.SMTP(host, port=587) as smtp:
            smtp.starttls(context=context)
            smtp.login(self.email_address, self.password)

            stopover_content = ''

            if flight.via_city != '' and flight.stopovers != 0:
                stopover_content = f'\nFlight has {flight.stopovers} stopover in {flight.via_city}.'

            content = f'''
LOW PRICE ALERT! ONLY ${flight.price} to fly 
from {flight.city_from}-{flight.fly_from} to {flight.city_to}-{flight.fly_to}, 
from {flight.leave_date} to {flight.return_date}
{stopover_content}
'''

            for email in emails:
                msg = EmailMessage()
                msg.set_content(content)
                msg['Subject'] = 'CHEAP FLIGHT ALERT'
                msg['From'] = self.email_address
                msg['To'] = email
                smtp.send_message(msg=msg)
