from dataclasses import dataclass


@dataclass
class FlightData:
    city_from: str
    fly_from: str
    city_to: str
    fly_to: str
    price: int
    leave_date: str
    return_date: str
