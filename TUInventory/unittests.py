import os
import random
import unittest


import classes
import utils


class TestUtils(unittest.TestCase):
    def test_normalize_filename(self):
        self.assertEqual(utils.normalize_filename(
            "123abd.edg/(&(&(%§!14    g\n1gj2141.pdf"), 
            "123abd.edg4___gj2141.pdf")
        
    def test_validate_filename(self):
        self.assertTrue(utils.validate_filename("abc"))
        with open("abc", "w") as f:
            self.assertFalse(utils.validate_filename("abc"))
        os.remove("abc")


class TestTelephoneNumber(unittest.TestCase):
    @classmethod
    def phone_number(cls, string):
        try:
            pn = classes.PhoneNumber(string)
        except Exception as e:
            raise e
        else:
            return str(pn)

    def test_basic_function(self):
        self.assertEqual(self.phone_number("+049 9723 1234-123"), "+049 9723 1234-123")
    
    def test_non_conforming_input(self):
        self.assertEqual(self.phone_number("09723 1234"), "+049 9723 1234")
        self.assertEqual(self.phone_number("09723 1234 56789-10"), "+049 9723 123456789-10")
        self.assertEqual(self.phone_number("09723 1234 56789+10"), "+049 9723 123456789-10")

    def test_text_input(self):
        self.assertEqual(self.phone_number("My telephonenumber is: 09723 1234. Yes."), "+049 9723 1234")
        self.assertEqual(self.phone_number("My number is 0 9723 1234+1 and yours is 09723 1234"), "+049 9723 1234-1")


if __name__ == "__main__":
    try:
        unittest.main()
    except SystemExit:
        pass