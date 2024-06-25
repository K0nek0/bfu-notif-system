import telebot

bot = telebot.TeleBot('7275660382:AAGLrZFJDaayCToiDB-4G2r8gwppILpDoao')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Тест!')

bot.polling(none_stop=True)