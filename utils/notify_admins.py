import logging
from loader import dp, db, types
from utils.states import States


async def on_startup_notify(text):
    admins_id = db.admins_get()
    for admin in admins_id:
        try:
            state = dp.current_state(
                chat=admin, user=admin)
            await state.set_state(States.admin)
            await dp.bot.send_message(admin, text)
        except Exception as error:
            logging.exception(error)


async def admin_notify(text):
    admins_id = db.admins_get()
    user_id = int(text.split('::')[1])
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        '✅ Подтвердить', callback_data=f'Confirm {user_id}')
    btn2 = types.InlineKeyboardButton(
        '❌ Отменить', callback_data=f'Cancel {user_id}')
    markup.add(btn1, btn2)
    for admin in admins_id:
        try:
            await dp.bot.send_message(admin, text, reply_markup=markup)
        except Exception as error:
            logging.exception(error)


async def admin_cancel():
    admins_id = db.admins_get()
    for admin in admins_id:
        state = dp.current_state(chat=admin, user=admin)
        await state.finish()
