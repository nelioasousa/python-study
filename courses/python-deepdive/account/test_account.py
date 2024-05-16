"""Unit tests for account.py module."""


import unittest
from datetime import timezone
from account import build_timezone, Account
from random import random


class AccountTest(unittest.TestCase):
    def test_empty_names(self):
        for i, name in enumerate(("", " ", "\n", "\n ", "\t", " \t")):
            with self.subTest(i=i, which="first_name"):
                self.assertRaises(ValueError, Account, 1000.0, name, "Sousa")
            with self.subTest(i=i, which="last_name"):
                self.assertRaises(ValueError, Account, 1000.0, "Nelio", name)
    
    def test_timezone_default_init(self):
        account = Account(9999, "Nelio", "Sousa")
        self.assertEqual(account.timezone, timezone.utc)
    
    def test_timezone_proper_init(self):
        initial_timezone = build_timezone(offset_hours=2, offset_minutes=30)
        account = Account(9999, "Nelio", "Sousa", tz=initial_timezone)
        self.assertEqual(account.timezone, initial_timezone)
    
    def test_timezone_setting(self):
        tz = build_timezone(offset_hours=9, offset_minutes=45)
        account = Account(4545, "John", "Doe", tz=tz)
        with self.subTest(test="none-setting"):
            account.timezone = None
            self.assertEqual(account.timezone, timezone.utc)
        with self.subTest(test="valid-setting"):
            tz = build_timezone(offset_hours=-12)
            account.timezone = tz
            self.assertEqual(account.timezone, tz)
        with (self.subTest(test="invalid-setting"), 
              self.assertRaises(TypeError)):
            account.timezone = "Not a timezone"
    
    def test_timezone_deletion(self):
        account = Account(
            7878, "John", "Doe", tz=build_timezone(offset_minutes=120))
        del account.timezone
        self.assertEqual(account.timezone, timezone.utc)
    
    def test_set_interest(self):
        interest = random()
        Account.set_interest(interest)
        self.assertEqual(Account.get_interest(), interest)
    
    def test_account_number(self):
        number = 5555
        account = Account(number, "Nelio", "Sousa")
        self.assertEqual(account.number, number)
    
    def test_monthly_interest(self):
        account = Account(4120, "Just", "Ken", 1000.0)
        Account.set_interest(0.5)
        transaction = account.process_monthly_interest()
        transaction = account.parse_transaction_string(transaction)
        self.assertEqual(transaction.transaction_code, "I")
        self.assertAlmostEqual(account.balance, 1500.0)
    
    def test_valid_withdrawal(self):
        value = round(2000.0 * random(), 2)
        account = Account(6698, "Another", "Person", 2000.0)
        transaction = account.withdraw(value)
        transaction = account.parse_transaction_string(transaction)
        self.assertEqual(transaction.transaction_code, "W")
        self.assertAlmostEqual(account.balance, 2000.0 - value)
    
    def test_invalid_withdrawal(self):
        account = Account(7845, "Again", "Just Ken", 1500.0)
        with self.subTest(test="not-enouth-fund"):
            transaction = account.withdraw(2000.0)
            transaction = account.parse_transaction_string(transaction)
            self.assertEqual(transaction.transaction_code, "X")
            self.assertAlmostEqual(account.balance, 1500.0)
        with (self.subTest(test="negative-value"),
              self.assertRaises(ValueError)):
            account.withdraw(-1.0)
        with (self.subTest(test="not-a-number"), self.assertRaises(TypeError)):
            account.withdraw("I'm not a number nor convertible to one")
    
    def test_valid_deposit(self):
        account = Account(745421, "Another", "Ken")
        value = round(10000.0 * (0.1 + random()), 2)
        transaction = account.deposit(value)
        transaction = account.parse_transaction_string(transaction)
        self.assertEqual(transaction.transaction_code, "D")
        self.assertAlmostEqual(account.balance, value)
    
    def test_invalid_deposit(self):
        account = Account(794613, "Me", "Again")
        with (self.subTest(test="negative-value"),
              self.assertRaises(ValueError)):
            account.deposit(-1.0)
        with (self.subTest(test="not-a-number"), self.assertRaises(TypeError)):
            account.deposit("I'm not a number nor convertible to one")


if __name__ == "__main__":
    unittest.main()
