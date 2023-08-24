import os
import re
from enum import Enum
from typing import Set, List, Dict, Optional, TextIO

from structures.table_stats import TableStats
from structures.time import Time


class ComputerClubErrorType(Enum):
    YOU_SHALL_NOT_PASS = "YouShallNotPass"
    NOT_OPEN_YET = "NotOpenYet"
    PLACE_IS_BUSY = "PlaceIsBusy"
    CLIENT_UNKNOWN = "ClientUnknown"
    I_CAN_WAIT_NO_LONGER = "ICanWaitNoLonger!"


class ComputerClubSimulator:
    def __init__(self):
        self._reinitialize()

    def simulate(self, input_filename: str):
        self._reinitialize()

        if not os.path.exists(input_filename):
            print("The algorithm file does not exists!")
            return

        with open(input_filename, "r") as input_file:
            self._process_file(input_file)

    @staticmethod
    def _parse_time(time_string: str) -> Optional[Time]:
        if not re.fullmatch("(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]", time_string):
            return None

        hours, minutes = [int(i) for i in time_string.split(":")]
        return Time(hours, minutes)

    @staticmethod
    def _is_client_name_valid(username: str) -> bool:
        return re.fullmatch("[a-z0-9_-]+", username) is not None

    @staticmethod
    def _print_error(error_type: ComputerClubErrorType, time: Time):
        print(f"{time} 13 {str(error_type.value)}")

    @staticmethod
    def _print_client_exit(client_name: str, time: Time):
        print(f"{time} 11 {client_name}")

    @staticmethod
    def _print_client_sit(client_name: str, time: Time, table_number: int):
        print(f"{time} 12 {client_name} {table_number}")

    def _process_file(self, input_file: TextIO):
        processing_line_number = 1
        tables_number_string = input_file.readline().strip()
        if not tables_number_string.isdigit():
            print(processing_line_number)
            return
        self.tables_number = int(tables_number_string)

        processing_line_number += 1
        split_time_strings = input_file.readline().strip().split()
        if len(split_time_strings) != 2:
            print(processing_line_number)
            return
        self.open_time, self.close_time = [self._parse_time(time_string) for time_string in split_time_strings]
        if self.open_time is None or self.close_time is None:
            print(processing_line_number)
            return

        processing_line_number += 1
        hour_cost_string = input_file.readline().strip()
        if not hour_cost_string.isdigit():
            print(processing_line_number)
            return
        self.hour_cost = int(hour_cost_string)

        self._on_day_has_begun()
        for line in input_file.readlines():
            processing_line_number += 1
            line = line.strip()
            if not self._process_line(line):
                print(processing_line_number)
                return
        self._on_day_is_over()

    def _process_line(self, line: str) -> bool:
        print(line)
        event_parts_strings = line.split()
        event_parts_number = len(event_parts_strings)
        if event_parts_number < 3:
            return False

        event_time_string = event_parts_strings[0]
        event_id_string = event_parts_strings[1]
        event_client_name = event_parts_strings[2]

        parsed_time = self._parse_time(event_time_string)
        if parsed_time is None or not event_id_string.isdigit() or not self._is_client_name_valid(event_client_name):
            return False

        event_time = self._parse_time(event_time_string)
        event_id = int(event_id_string)

        if event_parts_number == 3:
            if event_id == 1:
                self._on_client_entered(event_client_name, event_time)
                return True

            if event_id == 3:
                self._on_client_waiting(event_client_name, event_time)
                return True

            if event_id == 4:
                self._on_client_exited(event_client_name, event_time)
                return True

            return False

        if event_parts_number == 4 and event_id == 2:
            table_number_string = event_parts_strings[3]
            if not table_number_string.isdigit():
                return False

            table_number = int(table_number_string)
            self._on_client_sit(event_client_name, event_time, table_number)
            return True
        else:
            return False

    def _on_client_entered(self, client_name: str, time: Time):
        if client_name in self.in_club_clients:
            self._print_error(ComputerClubErrorType.YOU_SHALL_NOT_PASS, time)
        elif not (self.open_time <= time <= self.close_time):
            self._print_error(ComputerClubErrorType.NOT_OPEN_YET, time)
        else:
            self.in_club_clients.add(client_name)

    def _left_client_table(self, client_name: str, time: Time):
        client_table = self.client_to_table_dict.get(client_name, None)
        if client_table is not None:
            self.not_free_tables.remove(client_table)
            self._on_table_is_left(self.tables_stats_dict[client_table], time)

    def _seat_client_from_queue(self, table_number: int, time: Time):
        client_name = self.waiting_clients_queue.pop(0)
        self._on_table_is_sit(table_number, time)
        self.client_to_table_dict[client_name] = table_number
        self._print_client_sit(client_name, time, table_number)

    def _on_client_exited(self, client_name: str, time: Time):
        if client_name not in self.in_club_clients:
            self._print_error(ComputerClubErrorType.CLIENT_UNKNOWN, time)

        exited_client_table_number = self.client_to_table_dict.get(client_name, None)
        if exited_client_table_number is not None:
            self._on_table_is_left(self.tables_stats_dict[exited_client_table_number], time)
            if len(self.waiting_clients_queue) == 0:
                self._left_client_table(client_name, time)
            else:
                self._seat_client_from_queue(exited_client_table_number, time)

            self.client_to_table_dict.pop(client_name)

        self.in_club_clients.remove(client_name)

    def _on_table_is_left(self, table_stats: TableStats, table_left_time: Time):
        if table_stats.is_free:
            return

        current_seat_time = table_left_time - table_stats.last_seat_time
        income_hours_number = current_seat_time.hours
        if current_seat_time.minutes > 0:
            income_hours_number += 1

        table_stats.income += income_hours_number * self.hour_cost
        table_stats.total_seat_time += current_seat_time
        table_stats.is_free = True

    def _on_table_is_sit(self, table_number: int, time: Time, first_time: bool = False):
        if first_time:
            self.tables_stats_dict[table_number] = TableStats(0, Time(), time)
            return

        table_stats = self.tables_stats_dict[table_number]
        table_stats.last_seat_time = time
        table_stats.is_free = False

    def _on_client_sit(self, client_name: str, time: Time, table_number: int):
        if client_name not in self.in_club_clients:
            self._print_error(ComputerClubErrorType.CLIENT_UNKNOWN, time)
            return

        if table_number in self.not_free_tables:
            self._print_error(ComputerClubErrorType.PLACE_IS_BUSY, time)
            return

        self._left_client_table(client_name, time)
        self.client_to_table_dict[client_name] = table_number
        self.not_free_tables.add(table_number)
        self._on_table_is_sit(table_number, time, True)

    def _on_client_waiting(self, client_name: str, time: Time):
        if len(self.not_free_tables) < self.tables_number:
            self._print_error(ComputerClubErrorType.I_CAN_WAIT_NO_LONGER, time)
            return

        if len(self.waiting_clients_queue) >= self.tables_number:
            self._print_client_exit(client_name, time)
            return

        self.waiting_clients_queue.append(client_name)

    def _on_day_has_begun(self):
        print(self.open_time)

    def _print_tables_stats(self):
        for i in range(1, self.tables_number + 1):
            table_stats = self.tables_stats_dict.get(i)
            income = 0
            total_seat_time = Time()
            if table_stats is not None:
                income = table_stats.income
                total_seat_time = table_stats.total_seat_time
            print(f"{i} {income} {total_seat_time}")

    def _on_day_is_over(self):
        sorted_by_name_clients = sorted(list(self.in_club_clients))
        for client_name in sorted_by_name_clients:
            self._print_client_exit(client_name, self.close_time)
        print(self.close_time)

        for table_stats in self.tables_stats_dict.values():
            if not table_stats.is_free:
                self._on_table_is_left(table_stats, self.close_time)
        self._print_tables_stats()

    def _reinitialize(self):
        self.tables_number = 0
        self.open_time = Time()
        self.close_time = Time()
        self.hour_cost = 0

        self.in_club_clients: Set[str] = set()
        self.not_free_tables: Set[int] = set()
        self.waiting_clients_queue: List[str] = []

        self.client_to_table_dict: Dict[str, int] = dict()
        self.tables_stats_dict: Dict[int, TableStats] = dict()
