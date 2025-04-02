import requests
from constants import GEO_API_KEY


class CurrencyApi:
    def __init__(self):
        self.api_key = GEO_API_KEY
        self.base_url = "https://api.getgeoapi.com/v2/currency"

    def convert_currency(self, from_curr: str, to_curr: str, amount: int = 1) -> dict:
        params = {
            "api_key": self.api_key,
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "format": "json",
        }

        response = requests.get(f"{self.base_url}/convert", params=params)

        return response.json()
