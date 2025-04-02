from datetime import datetime, timedelta

import redis

from .currency_api import CurrencyApi


class RedisBroker:
    def __init__(self):
        self.client = redis.Redis(host="redis", port=6379, decode_responses=True)

    def set_rate(self) -> None:
        self.client.set(
            "rate",
            CurrencyApi().convert_currency("uah", "usd")["rates"]["USD"]["rate"],
        )
        self.client.set("last_update", datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))

    def get_rate(self) -> int:
        rate = self.client.get("rate")
        last_update = self.client.get("last_update")

        if rate is None:
            self.set_rate()

        if last_update is None and datetime.strptime(
            last_update, "%d/%m/%Y, %H:%M:%S"
        ) > datetime.now() + timedelta(minutes=5):
            self.set_rate()

        return float(self.client.get("rate"))
