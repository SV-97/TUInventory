import re
strings = ["+049 9729 1422-23", 
    "12345", 
    "09123 161234", 
    "1612+1", 
    "+049", 
    "0", 
    "",
    "256g1"]
print("""
    
    """)
class PhoneNumber():
    def __init__(self, raw_string):
        """Get a Phone Number from raw input string
        Args:
            raw_string (str): String that holds the number
        To do:
            config to set locale (subscriber number prefix and country code)
        """
        pattern = r"(((\+\d{1,3})|(0)) ?([1-9]+) )?(\d+ ?)+(-\d+)?"
        self.match = re.match(pattern, raw_string)
        self.country_code = self._extract_country_code()
        self.area_code = self._extract_area_code()
        self.subscriber_number = self._extract_subscriber_number()
        self.extension = self._extract_extension()
    @staticmethod
    def _whitespacekiller(string):
        return re.sub(r"\D", "", string)
    def _extract_country_code(self):
        country_code = self.match.group(2)
        if "+" in country_code:
            return self._whitespacekiller(country_code)
        else:
            return "049"
    def _extract_area_code(self):
        area_code = self.match.group(5) if self.match.group(5) else "9321"
        return self._whitespacekiller(area_code)
    def _extract_subscriber_number(self):
        subscriber_number = self.match.group(6)
        return self._whitespacekiller(subscriber_number)
    def _extract_extension(self):
        extension = self.match.group(7)
        return self._whitespacekiller(extension)
    def __str__(self):
        extension = f"-{self.extension}" if self.extension else ""
        return "f+{self.country_code} {self.area_code} {self.subscriber_number}{extension}"

for string in strings:
    print(PhoneNumber(string))