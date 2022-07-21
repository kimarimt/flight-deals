from dataclasses import dataclass, field


@dataclass
class FlightData:
    city_from: str
    fly_from: str
    city_to: str
    fly_to: str
    price: int
    leave_date: str
    return_date: str
    stopovers: int = 0
    via_city: str = ''

