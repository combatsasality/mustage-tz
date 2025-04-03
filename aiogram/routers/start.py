from utils import Menu, ServerBroker

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from .callbacks import MenuCallback

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message):
    await ServerBroker().add_user(message.chat.id, message.chat.first_name)

    await message.answer(
        "Привіт! Я бот який допоможе тобі слідкувати за своїми фінансами!\nОберіть пункт меню",
        reply_markup=Menu.get_menu(),
    )


@router.callback_query(MenuCallback.filter(F.action == "back"))
async def back_to_menu(query: CallbackQuery):
    await query.message.answer("Оберіть пункт меню", reply_markup=Menu.get_menu())
