from loader import bot, dp, types, db
from utils.notify_admins import on_startup_notify, admin_notify, admin_cancel
from aiogram import executor
from utils.states import States
from filters import IsAdmin


async def on_startup(dp):
    import filters
    filters.setup(dp)
    await on_startup_notify('Бот запущен...')
    print('Bot start...')


async def check_username(message):
    if message.from_user.username != None:
        return f'@{message.from_user.username}'
    else:
        return f'{message.from_user.first_name}'


async def bars_setting(call):
    bars = db.bars_get()['name']
    card = db.user_get(call.from_user.id)['card']
    for i in range(len(bars)):
        bars[i]['count'] -= card[i]['count']
    db.bars_set(bars)


@dp.message_handler(commands=['start', 'menu'], state=None)
async def start(message):
    if message.chat.type == 'private':
        if not bool(db.user_get(message.from_user.id)):
            db.user_add(message)
    if len(db.user_get(message.from_user.id)['card']) == 0:
        await States.start.set()
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            f'🛍️ Заказать', callback_data=f'Start')
        markup.add(btn1)
        await bot.send_message(
            message.chat.id, '👋 Привет, тут можно заказать <b>Elf Bar</b>💨\n\n'+'🥇 У нас лучшие цены и проверенные поставщики.\nЧтобы заказать выбери соответствующую кнопку.\n'+'😎 По городу Васильков можем доставить прям под дверь.', reply_markup=markup)
    else:
        cards = db.user_get(message.from_user.id)['card']
        text = ''
        for card in cards:
            if card['count'] != 0:
                text += f'✅ {card["name"]} - {card["count"]} шт.\n'
        await message.answer(f'🛍️ У тебя уже есть корзина с эльфбарами:\n{text}')


@dp.message_handler(commands='cancel', state=States.complite)
async def cancel(message):
    if message.chat.type == 'private':
        state = dp.current_state(
            chat=message.chat.id, user=message.from_user.id)
        bars = db.bars_get()['name']
        card = db.user_get(message.from_user.id)['card']
        for i in range(len(bars)):
            bars[i]['count'] += card[i]['count']
        db.card_edit(message.from_user.id, [])
        db.bars_set(bars)
        await on_startup_notify(f'{await check_username(message)} очистил корзину!')
        await bot.send_message(message.chat.id, '🗑️ Корзина очищена.', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()


@dp.message_handler(commands='cancel', state=None)
async def clear(message):
    db.card_edit(message.from_user.id, [])
    await bot.send_message(message.chat.id, '🗑️ Корзина очищена.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(IsAdmin(), commands='setbars', state='*')
async def setbars(message):
    await States.setbars.set()
    await bot.send_message(message.chat.id, '📋 Введи список эльфбарова в формате:\n<i>Название бара - [кол-во];</i>', reply_markup=types.ForceReply())


@dp.message_handler(IsAdmin(), commands='list', state='*')
async def list_bars(message):
    text = ''
    bars = db.bars_get()['name']
    for bar in bars:
        text += f'✅ {bar["name"]} - {bar["count"]} шт.\n'
    await message.answer(f'📋 <b>Каталог эльфбаров:</b>\n\n{text}')


@dp.message_handler(IsAdmin(), state=States.setbars)
async def get_bars(message):
    state = dp.current_state(
        chat=message.chat.id, user=message.from_user.id)
    await state.finish()
    data = message.text.split(';')
    bars = []
    for item in data:
        if item != '':
            elem = item.split('-')
            bars.append({'name': elem[0], 'count': int(elem[1])})
    db.bars_set(bars)
    await message.answer('✅ Список эльфбаров успешно обновлен.')


@dp.callback_query_handler(lambda callback_query: True, state=States.start)
async def bars_buttons(call):
    if call.data == 'Start':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    bars = db.bars_get()['name']
    if call.data == 'Order':
        await States.getting.set()
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(
            '🧭 Самовывоз', callback_data='Pickup')
        btn2 = types.InlineKeyboardButton('📦 Курьер', callback_data='Courier')
        markup.add(btn1, btn2)
        await bot.send_message(call.message.chat.id, '🤔 Выберите способ доставки:', reply_markup=markup)
        return
    cards = db.user_get(call.from_user.id)['card']
    markup = types.InlineKeyboardMarkup()
    edit = 0
    text = ''
    if call.data.isnumeric():
        cards[int(call.data)]['count'] += 1
        db.card_edit(call.from_user.id, cards)
    if len(cards) == 0:
        for bar in bars:
            cards.append({'name': bar['name'], 'count': 0})
            db.card_edit(call.from_user.id, cards)
    else:
        edit += 1
    for i in range(len(bars)):
        if bars[i]['count'] - cards[i]["count"] > 0:
            markup.add(types.InlineKeyboardButton(
                f'{bars[i]["name"]} - {bars[i]["count"] - cards[i]["count"]} шт.', callback_data=i))
        if cards[i]['count'] > 0:
            text += f'{cards[i]["name"]} - {cards[i]["count"]} шт.\n'
    if edit == 0:
        await bot.send_message(call.message.chat.id,
                               '😋 Выберите интересующий вкус:', reply_markup=markup)
    else:
        markup.add(types.InlineKeyboardButton(
            '🛍️ Заказать', callback_data='Order'))
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'😋 Выберите интересующий вкус:\nКорзина:\n{text}', reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: True, state=States.getting)
async def getting(call):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'Courier':
        await States.phone.set()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(
            '📱 Номер телефона', request_contact=True)
        markup.add(btn1)
        await bot.send_message(call.message.chat.id, '📱 Нажмите на кнопку внизу, чтобы отправить нам свой номер телефона, для того чтобы связаться с вами.', reply_markup=markup)
    elif call.data == 'Pickup':
        await States.complite.set()
        card = db.user_get(call.from_user.id)['card']
        summ = 0
        text = ''
        for i in range(len(card)):
            if card[i]['count'] != 0:
                summ += card[i]['count']
                text += f'{card[i]["name"]} - {card[i]["count"]} шт.\n'
        await call.message.answer('✅ Ваша заявка была принята.\nЗабрать свой заказ можно по адресу: остановка Военный городок №11. Перед прибытием по адресу свяжитесь с менеджерами: @eva_elfbar или @TTaRaDoKc.\n'+f'⌚ Время работы: c 10:00 до 19:00.\nСумма заказа: {summ * 300} грн.\nКорзина:\n{text}')
        await bars_setting(call)
        await admin_notify(f'Заявка на самовывоз от {await check_username(call)}.\nСумма: {summ*300}\nКорзина:\n{text}\nID::{call.from_user.id}')


@dp.message_handler(content_types=types.message.ContentType.CONTACT, state=States.phone)
async def phone(message):
    await States.complite.set()
    card = db.user_get(message.from_user.id)['card']
    summ = 0
    text = ''
    for i in range(len(card)):
        summ += card[i]['count']
        if card[i]['count'] != 0:
            text += f'{card[i]["name"]} - {card[i]["count"]} шт.\n'
    phone = message.contact.phone_number
    await bot.send_message(
        message.chat.id, f'✅ Ваш заказ принят и передан в обработку, ожидайте звонка менеджера.\n'+f'⌚ Рабочее время: 10:00 до 19:00.\nДоставка стоит 20 гривен.\nСумма: {summ*300+20} грн.\nКорзина:\n{text}', reply_markup=types.ReplyKeyboardRemove())
    await bars_setting(message)
    await admin_notify(f'Заявка на доставку от {await check_username(message)}.\nНомер телефона: +{phone}\nСумма: {summ*300+20}\nКорзина:\n{text}\nID::{message.from_user.id}')


@dp.callback_query_handler(lambda callback_query: True, state=States.admin)
async def admin_card(call):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    data = call.data.split()
    if len(db.user_get(int(data[1]))['card']) != 0:
        if data[0] == 'Confirm':
            db.card_edit(int(data[1]), [])
        elif data[0] == 'Cancel':
            bars = db.bars_get()['name']
            card = db.user_get(int(data[1]))['card']
            for i in range(len(bars)):
                bars[i]['count'] += card[i]['count']
            db.card_edit(int(data[1]), [])
            db.bars_set(bars)
        state = dp.current_state(
            chat=int(data[1]), user=int(data[1]))
        await state.finish()
    else:
        await call.message.answer(
            'У этого пользователя уже пустая корзина, значит его уже принял другой админ.')

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
