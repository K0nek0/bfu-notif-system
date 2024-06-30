import telebot
from telebot import types

with open('credentials.TXT', 'r') as file:
    bot_token = file.read().strip()

bot = telebot.TeleBot(bot_token)
commands = bot.get_my_commands()
command_list = "\n".join([f"/{command.command} - {command.description}" for command in commands])
def create_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sub_btn = types.KeyboardButton('Подписаться')
    unsub_btn = types.KeyboardButton('Отписаться')
    help_btn = types.KeyboardButton('Список команд')
    recent_btn = types.KeyboardButton('Последнее событие')
    upcoming_btn = types.KeyboardButton('Предстоящие события')
    markup.row(sub_btn, unsub_btn)
    markup.row(recent_btn, upcoming_btn)
    markup.row(help_btn)
    return markup

def create_categories():
    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    imp = types.KeyboardButton('Важное')
    event = types.KeyboardButton('Развлекательное')
    study = types.KeyboardButton('Обучение')
    markup2.row(imp, event, study)
    return markup2
@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if last_name is None:
        user_name = first_name
    else:
        user_name = f'{first_name} {last_name}'

    markup = create_keyboard()
    bot.send_message(message.chat.id, f'Привет, {user_name}!\n'
                                      'Для подписки на рассылку воспользуйся командой /sub\n'
                                      'Остальные команды доступны в /help',
                     parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['sub'])
def subscribe(message):
    bot.send_message(message.chat.id, 'Выберете категорию:', reply_markup=create_categories())

@bot.message_handler(func=lambda message: message.text in ['Важное', 'Мероприятие', 'Обучение'])
def category(message):
    if message.text == 'Важное':
        bot.send_message(message.chat.id, 'Вы успешно подписались на Важное!', reply_markup=create_keyboard())
    elif message.text == 'Развлекательное':
        bot.send_message(message.chat.id, 'Вы успешно подписались на Развлекательное!', reply_markup=create_keyboard())
    elif message.text == 'Обучение':
        bot.send_message(message.chat.id, 'Вы успешно подписались на Обучение!', reply_markup=create_keyboard())
@bot.message_handler(commands=['unsub'])
def unsubscribe(message):
    bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, f'Список команд:\n{command_list}', reply_markup=create_keyboard())

@bot.message_handler(commands=['recent'])
def recent_event(message):
    # Вывод последнего события
    bot.send_message(message.chat.id, 'recent_event', reply_markup=create_keyboard())
@bot.message_handler(commands=['upcoming'])
def upcoming_events(message):
    # Вывод 3-5 следующх событий
    bot.send_message(message.chat.id, 'upcoming_events', reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text in ['Подписаться', 'Отписаться', 'Список команд'])
def on_click(message):
    if message.text == 'Подписаться':
        bot.send_message(message.chat.id, 'Выберете категорию:', reply_markup=create_categories())
    elif message.text == 'Отписаться':
        bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())
    elif message.text == 'Список команд':
        bot.send_message(message.chat.id, f'Список команд:\n{command_list}', reply_markup=create_keyboard())
@bot.message_handler()
def error(message):
    bot.send_message(message.chat.id, 'Неизвестная команда, используйте /help, чтобы вывести список команд',
                     parse_mode='Markdown',
                     reply_markup=create_keyboard())
    
bot.polling(none_stop=True)
