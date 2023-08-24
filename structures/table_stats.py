from dataclasses import dataclass
from structures.time import Time


@dataclass
class TableStats:
    income: int = 0
    total_seat_time: Time = Time()
    last_seat_time: Time = Time()
    is_free: bool = False
