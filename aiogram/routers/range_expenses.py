from datetime import datetime

from utils import Menu, ServerBroker

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from .callbacks import MenuCallback


class ReportForm(StatesGroup):
    from_range = State()
    to_range = State()


router = Router(name="range")


@router.callback_query(MenuCallback.filter(F.action == "report"))
async def report(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.from_range)
    await query.message.answer("Введіть початок періоду в форматі 31.12.2024")


@router.message(ReportForm.from_range)
async def from_range(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
    except Exception:
        await message.answer("Невірно введена дата, формат: день.місяць.рік")
        return
    await state.update_data(from_range=date)
    await state.set_state(ReportForm.to_range)

    await message.answer("Введіть кінець періоду")


@router.message(ReportForm.to_range)
async def to_range(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
    except Exception:
        await message.answer("Невірно введена дата, формат: день.місяць.рік")
        return
    data = await state.get_data()
    if data["from_range"] > date:
        await message.answer("Кінець періоду не може бути менше за початок")
        return
    file = await ServerBroker().generate_report_from_range(
        user_id=message.chat.id, from_range=data["from_range"], to_range=date
    )

    await message.answer_document(BufferedInputFile(file.read(), filename="Звіт.xlsx"))
    await state.clear()
    await message.answer("Оберіть пункт меню", reply_markup=Menu.get_menu())
