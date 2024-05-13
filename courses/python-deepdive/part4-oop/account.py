"""
Class to represent bank accounts.

Project 1 from Python3 Deep Dive Part 4.
Implemented using floating point arithmetic instead of fixed-point arithmetic.

Project specification at https://github.com/fbaptiste/python-deepdive
"""


from datetime import datetime, timezone, timedelta
from collections import namedtuple


AccountTransaction = namedtuple(
    "AccountTransaction",
    "account_number,transaction_code,"
    "transaction_id,timestamp_loc,timestamp_utc")


def custom_timezone(
        offset_hours=0,
        offset_minutes=0,
        offset_seconds=0):
    offset = timedelta(
        hours=offset_hours, minutes=offset_minutes, seconds=offset_seconds)
    return timezone(offset=offset)


class Account:
    _interest = 0.0
    _next_transaction_id = 0
    _compact_datetime_fmt = "%Y%m%d%H%M%S%f"
    _readable_datetime_fmt = "%Y-%m-%d T%H:%M:%S.%f %Z"

    def __init__(
            self,
            account_number,
            first_name,
            last_name,
            balance=0.0,
            tz=None):
        self._number = account_number
        self._first_name = self._check_name(first_name)
        self._last_name = self._check_name(last_name)
        self._balance = balance if balance >= 0.0 else 0.0
        self._timezone = timezone.utc if tz is None else tz
    
    @staticmethod
    def _check_name(name):
        name = ' '.join(name.split())
        if not name:
            raise ValueError("Cannot be an empty string")
        return name

    @classmethod
    def _get_transaction_id(cls):
        tid = cls._next_transaction_id
        cls._next_transaction_id += 1
        return tid

    @classmethod
    def get_interest(cls):
        return cls._interest

    @classmethod
    def set_interest(cls, interest):
        # No range of values specified by business logic
        # Accepts any value that can be converted to a float
        try:
            cls._interest = float(interest)
            return True
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def _string_from_datetime(cls, x, /):
        return x.strftime(cls._compact_datetime_fmt)
    
    @classmethod
    def _datetime_from_string(cls, x, /):
        naive_dt = datetime.strptime(x, cls._compact_datetime_fmt)
        return naive_dt.replace(tzinfo=timezone.utc)
    
    @classmethod
    def _readable_string_from_datetime(cls, x, /):
        return x.strftime(cls._readable_datetime_fmt)

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, fname):
        self._first_name = self._check_name(fname)

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, lname):
        self._last_name = self._check_name(lname)

    @property
    def full_name(self):
        return "%s %s" %(self.first_name, self.last_name)

    @property
    def balance(self):
        return self._balance
    
    def _set_balance(self, value):
        value = float(value)
        if value >= 0.0:  # Negative balance not allowed
            self._balance = value
        else:
            raise ValueError("value must be >= 0.0")

    def _generate_transaction_string(self, transaction_code):
        dt = datetime.now(timezone.utc)
        return "%s-%d-%s-%d" %(transaction_code,
                               self._number,
                               self._string_from_datetime(dt),
                               self._get_transaction_id())

    def process_monthly_interest(self):
        new_balance = round(self.balance * (1 + self.get_interest()), 2)
        try:
            self._set_balance(new_balance)
        except (ValueError, TypeError):
            return self._generate_transaction_string('X')
        return self._generate_transaction_string('I')
    
    def withdraw(self, value):
        try:
            self._set_balance(self.balance - round(value, 2))
        except (ValueError, TypeError):
            return self._generate_transaction_string('X')
        return self._generate_transaction_string('W')

    def deposit(self, value):
        try:
            self._set_balance(self.balance + round(value, 2))
        except (ValueError, TypeError):
            return self._generate_transaction_string('X')
        return self._generate_transaction_string('D')
    
    def parse_transaction_string(self, transaction_string):
        portions = transaction_string.split('-')
        datetime_utc = self._datetime_from_string(portions[2])
        datetime_loc = datetime_utc.astimezone(self._timezone)
        return AccountTransaction(
            account_number=int(portions[1]),
            transaction_code=portions[0],
            transaction_id=int(portions[3]),
            timestamp_loc=self._readable_string_from_datetime(datetime_loc),
            timestamp_utc=self._readable_string_from_datetime(datetime_utc))
