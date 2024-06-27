import telebot
from telebot import types

with open('credentials.TXT', 'r') as file:
    bot_token = file.read()
bot = telebot.TeleBot(bot_token)
commands = bot.get_my_commands()
command_list = "\n".join([f"/{command.command} - {command.description}" for command in commands])

@bot.message_handler(commands=['start'])
def start(message):

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if last_name == None:
        user_name = first_name
    else:
        user_name = f'{first_name} {last_name}'

    markup = types.ReplyKeyboardMarkup()
    sun_btn = types.KeyboardButton('Подписаться')
    unsub_btn = types.KeyboardButton('Отписаться')
    markup.row(sun_btn, unsub_btn)
    help_btn = types.KeyboardButton('Список команд')
    markup.row(help_btn)
    bot.register_next_step_handler(message, on_click)

    bot.send_message(message.chat.id, f'Привет, {user_name}!\n'
                                      'Для подписки на рассылку воспользуйся командой /sub\n'
                                      'Остальные команды доступны в /help',
                     parse_mode='Markdown', reply_markup=markup)

def on_click(message):
    if message.text == 'Подписаться':
        bot.send_message(message.chat.id, 'Вы успешно подписались на рассылку!')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Отписаться':
        bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!')
        bot.register_next_step_handler(message, on_click)
    elif message.text == 'Список команд':
        bot.send_message(message.chat.id, f'Список команд:\n'
                                          f'{command_list}')
        bot.register_next_step_handler(message, on_click),

@bot.message_handler(commands=['sub'])
def stop(message):
    bot.send_message(message.chat.id, 'Вы успешно подписались на рассылку!')
@bot.message_handler(commands=['unsub'])
def stop(message):
    bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, f'Список команд:\n'
                                      f'{command_list}')

bot.polling(none_stop=True)
