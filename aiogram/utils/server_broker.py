from datetime import datetime
from io import BytesIO
from json import dumps
from typing import Union

import aiohttp
from constants import SECRET, SERVER_URL
from openpyxl import Workbook


class ServerBroker:
    def __init__(self):
        self.url = SERVER_URL
        self.headers = {"secret": SECRET, "Content-Type": "application/json"}

    async def _make_request(self, method: str, path: str, data: dict = None) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as ses:
            response = await ses.request(
                method=method, url=f"{self.url}{path}", data=dumps(data)
            )

            response.raise_for_status()

            json = await response.json()

            if "status" in json and not json["status"]:
                raise Exception(json)

            return json

    async def _report(self, data: list[dict], with_id: bool = False) -> BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "Звіт"

        if with_id:
            ws.append(["Назва", "Сума в гривнях", "Сума в долларах", "Дата", "ID"])
            ws.column_dimensions["E"].width = 45
        else:
            ws.append(["Назва", "Сума в гривнях", "Сума в долларах", "Дата"])

        for col in ["A", "B", "C", "D"]:
            ws.column_dimensions[col].width = 20

        for row in data:
            if with_id:
                ws.append(list(row.values()))
            else:
                ws.append(list(row.values())[:-1])

        total_row = len(data) + 2

        ws[f"B{total_row}"] = "=SUM(B2:B{})".format(total_row - 1)
        ws[f"C{total_row}"] = "=SUM(C2:C{})".format(total_row - 1)

        output = BytesIO()

        wb.save(output)
        output.seek(0)

        return output

    async def user_identical(self, user_id: int, name: str) -> bool:
        """
        The method checks the identity of the name in database
        """
        json = await self._make_request("GET", f"/users/{user_id}")

        if json["name"] != name:
            return False

        return True

    async def add_user(self, user_id: int, name: str) -> bool:
        """
        Method add user to backend
        """
        await self._make_request(
            "POST", "/users/add", data={"id": user_id, "name": name}
        )

        return True

    async def add_expenses(
        self, user_id: int, name: str, date: datetime, amount: int
    ) -> str:
        """
        Method of adding expanses to the user
        """
        json = (
            await self._make_request(
                "POST",
                "/expenses/add",
                data={
                    "name": name,
                    "amount_uah": amount,
                    "user_id": user_id,
                    "created_at": date.strftime("%Y-%m-%d"),
                },
            )
        )["message"]
        return f"\nНазва: {json['name']}\nСума в гривнях: {json['amount_uah']}₴\nСума в долларах: {round(json['amount_usd'], 2)}$\nДата: {datetime.strptime(json['created_at'], '%Y-%m-%d').strftime('%d.%m.%Y')}"

    async def generate_report(self, user_id: int) -> BytesIO:
        """
        Method of generate xlsx file
        """
        json = await self._make_request("GET", f"/expenses/{user_id}")

        return await self._report(json, True)

    async def generate_report_from_range(
        self, user_id: int, from_range: datetime, to_range: datetime
    ) -> BytesIO:
        """
        Method of generate xlsx file from range
        """
        json = await self._make_request(
            "GET",
            f"/expenses/{user_id}/{from_range.strftime('%d.%m.%Y')}/{to_range.strftime('%d.%m.%Y')}",
        )

        return await self._report(json)

    async def delete(self, id: str) -> bool:
        """
        Method to delete expenses
        """
        await self._make_request("DELETE", f"/expenses/{id}")

        return True

    async def delete_many(self, ids: list[str]) -> bool:
        """
        Method to delete many expenses
        """
        await self._make_request("DELETE", "/expenses", data=ids)

        return True

    async def has_expenses(self, id: str) -> Union[bool, dict]:
        """
        Method check if id expenses exists
        """
        json = await self._make_request("GET", f"/expenses/get/{id}")

        return json

    async def update_expenses(
        self, id: str, name: str, amount: str
    ) -> Union[bool, dict]:
        """
        Method update expenses
        """
        json = await self._make_request(
            "PATCH", f"/expenses/{id}", data={"name": name, "amount_uah": amount}
        )

        return json
