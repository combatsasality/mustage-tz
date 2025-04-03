from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


class Menu:
    @staticmethod
    def get_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Додати статтю витрат", callback_data="menu:add")
        builder.button(
            text="Отримати звіт витрат за вказаний період", callback_data="menu:report"
        )
        builder.button(text="Видалити статтю у списку витрат", callback_data="menu:del")
        builder.button(
            text="Відредагувати статтю у списку витрат", callback_data="menu:upd"
        )
        builder.adjust(1, repeat=True)
        return builder.as_markup()

    @staticmethod
    def back_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="Повернутись до меню", callback_data="menu:back")

        return builder.as_markup()
