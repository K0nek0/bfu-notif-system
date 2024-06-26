import telebot

with open('credentials.TXT', 'r') as file:
    bot_token = file.read()
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start(message):

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if last_name == None:
        user_name = first_name
    else:
        user_name = f'{first_name} {last_name}'

    bot.send_message(message.chat.id, f'Привет, {user_name}!\n'
                                      'Для подписки на рассылку воспользуйся командой /sub\n'
                                      'Остальные команды доступны в /help',
                     parse_mode='Markdown')


# @bot.message_handler(commands=['stop'])
# def stop(message):
#     bot.send_message(message.chat.id, 'Вы отписались от уведомлений!')
#
# @bot.message_handler(commands=['help'])
# def help(message):
#     bot.send_message(message.chat.id, '<b>Доступные команды</b>:', parse_mode='html')

bot.polling(none_stop=True)
