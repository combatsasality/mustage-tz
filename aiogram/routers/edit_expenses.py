from uuid import UUID

from utils import Menu, ServerBroker

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from .callbacks import MenuCallback


class ChangeForm(StatesGroup):
    id = State()
    name = State()
    amount = State()


router = Router(name="menu")


@router.callback_query(MenuCallback.filter(F.action == "upd"))
async def delete(query: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeForm.id)

    file = await ServerBroker().generate_report(query.from_user.id)

    await query.message.answer_document(
        BufferedInputFile(file.read(), filename="Звіт.xlsx")
    )

    await query.message.answer("Введіть ID витрати")


@router.message(ChangeForm.id)
async def ids(message: Message, state: FSMContext):
    try:
        UUID(message.text)
    except ValueError:
        await message.answer(f"ID: {message.text} не є вірним форматом")

    response = await ServerBroker().has_expenses(message.text)

    if not response:
        await message.answer("Такої витрати не існує")
        return

    await message.answer(
        f"\nНазва: {response['name']}\nСума в гривнях: {response['amount_uah']}₴\nСума в долларах: {round(response['amount_usd'], 2)}$\nДата: {response['created_at']}"
    )

    await state.set_state(ChangeForm.name)
    await state.update_data(id=message.text)

    await message.answer("Введіть нову назву витрати")


@router.message(ChangeForm.name)
async def name(message: Message, state: FSMContext):
    await state.set_state(ChangeForm.amount)
    await state.update_data(name=message.text)

    await message.answer("Введіть нову сумму витрати")


@router.message(ChangeForm.amount)
async def amount(message: Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer("Сума має бути числом")
        return

    data = await state.get_data()
    response = (
        await ServerBroker().update_expenses(data["id"], data["name"], message.text)
    )["message"]

    await message.answer(
        f"\nНазва: {response['name']}\nСума в гривнях: {response['amount_uah']}₴\nСума в долларах: {round(response['amount_usd'], 2)}$\nДата: {response['created_at']}",
        reply_markup=Menu.back_menu(),
    )
