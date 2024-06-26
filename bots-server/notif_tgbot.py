import telebot

with open('credentials.TXT', 'r') as file:
    bot_token = file.read()
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Тест!')

bot.polling(none_stop=True)