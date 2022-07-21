from flight_manager import FlightManager
from notification_manager import NotificationManager
from sheet_manager import SheetManager


def main():
    sheet_manager = SheetManager()
    flight_manager = FlightManager()
    notification_manager = NotificationManager()

    if sheet_manager.codes[0] != 'PAR':
        iata_codes = [flight_manager.get_iata_code(city) for city in sheet_manager.cities]
        sheet_manager.update_codes_row(iata_codes)

    flight_manager.search(sheet_manager.codes)

    for i, flight in enumerate(flight_manager.flights):
        if flight == {}:
            continue

        lowest_price = sheet_manager.lowest_prices[i]

        if flight.price < lowest_price:
            notification_manager.send_message(flight)


if __name__ == '__main__':
    main()
