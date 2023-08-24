class Time:
    hours: int = 0
    minutes: int = 0

    def __init__(self, hours: int = 0, minutes: int = 0):
        total_minutes = self._get_total_minutes(hours, minutes)
        self.hours = total_minutes // 60
        self.minutes = total_minutes % 60

    @staticmethod
    def _get_total_minutes(hours: int, minutes: int) -> int:
        return hours * 60 + minutes

    def _compare(self, other: "Time") -> int:
        if self._get_total_minutes(self.hours, self.minutes) == other._get_total_minutes(other.hours, other.minutes):
            return 0

        if self._get_total_minutes(self.hours, self.minutes) > other._get_total_minutes(other.hours, other.minutes):
            return 1

        return -1

    def __eq__(self, other: "Time"):
        return self._compare(other) == 0

    def __lt__(self, other: "Time"):
        return self._compare(other) == -1

    def __gt__(self, other: "Time"):
        return self._compare(other) == 1

    def __le__(self, other: "Time"):
        return self._compare(other) <= 0

    def __ge__(self, other: "Time"):
        return self._compare(other) >= 0

    def __add__(self, other: "Time") -> "Time":
        return Time(self.hours + other.hours, self.minutes + other.minutes)

    def __sub__(self, other: "Time"):
        return Time(self.hours - other.hours, self.minutes - other.minutes)

    def __str__(self):
        return f"{self.hours:02d}:{self.minutes:02d}"
