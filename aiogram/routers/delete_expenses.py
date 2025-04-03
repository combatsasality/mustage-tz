from uuid import UUID

from utils import Menu, ServerBroker

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from .callbacks import MenuCallback


class DeleteForm(StatesGroup):
    ids = State()


router = Router(name="menu")


@router.callback_query(MenuCallback.filter(F.action == "del"))
async def delete(query: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteForm.ids)

    file = await ServerBroker().generate_report(query.from_user.id)

    await query.message.answer_document(
        BufferedInputFile(file.read(), filename="Звіт.xlsx")
    )

    await query.message.answer(
        "Введіть ID витрат (також можна видалити декілька, ID треба писати через кому)"
    )


@router.message(DeleteForm.ids)
async def ids(message: Message, state: FSMContext):
    ids = message.text.split(",")

    valid_uuids = []

    for id in ids:
        try:
            UUID(id)
            valid_uuids.append(id.strip())
        except ValueError:
            await message.answer(f"ID: {id} не є вірним форматом")

    if len(valid_uuids) > 1:
        await ServerBroker().delete_many(valid_uuids)
    elif len(valid_uuids) == 1:
        await ServerBroker().delete(valid_uuids[0])

    await state.clear()

    await message.answer("Витрати було успішно видалено", reply_markup=Menu.back_menu())
