from datetime import datetime

from utils import Menu, ServerBroker

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .callbacks import MenuCallback


class AddForm(StatesGroup):
    name = State()
    date = State()
    amount = State()


router = Router(name="add")


@router.callback_query(MenuCallback.filter(F.action == "add"))
async def add_expenses(query: CallbackQuery, state: FSMContext):
    await state.set_state(AddForm.name)
    await query.message.answer("Введіть назву статті витрат")


@router.message(AddForm.name)
async def set_name(message: Message, state: FSMContext):
    await state.set_state(AddForm.date)
    await state.update_data(name=message.text)
    await message.answer("Чудово, теперь введіть дату в форматі 31.12.2024")


@router.message(AddForm.date)
async def set_date(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
    except Exception:
        await message.answer("Невірно введена дата, формат: день.місяць.рік")
        return
    await state.set_state(AddForm.amount)
    await state.update_data(date=date)
    await message.answer("Теперь потрібно ввести сумму витрати в гривнях")


@router.message(AddForm.amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Потрібно ввести сумму цифрами")
    data = await state.get_data()
    response = await ServerBroker().add_expenses(
        user_id=message.chat.id, name=data["name"], date=data["date"], amount=amount
    )
    await state.clear()
    await message.answer(response, reply_markup=Menu.back_menu())
