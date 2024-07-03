import telebot
from telebot import types
import socket
import json
import threading

with open('credentials.TXT', 'r') as file:
    bot_token = file.read().strip()

bot = telebot.TeleBot(bot_token)
commands = bot.get_my_commands()
command_list = "\n".join([f"/{command.command} - {command.description}" for command in commands])

SERVER_HOST = '109.111.157.159'
SERVER_PORT = 8001

client_socket = None

def socket_client():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")



def send_data_to_server(data):
    try:
        if isinstance(data, dict):
            json_data = json.dumps(data, ensure_ascii=False)
            print(f"Sending to server: {json_data}")
            client_socket.sendall(json_data.encode('utf-8'))
        elif isinstance(data, str):  # Пример отправки строки
            print(f"Sending string to server: {data}")
            client_socket.sendall(data.encode('utf-8'))
        else:
            print(f"Unsupported data type: {type(data)}")
            return "Unsupported data type"

        response = client_socket.recv(1024)
        if not response:
            return "No response from server"
        response_data = response.decode('utf-8')
        print(f"Received from server: {response_data}")
        return response_data
    except ConnectionRefusedError:
        return "Could not connect to server"
    except TimeoutError:
        return "Connection timed out"
    # except json.JSONDecodeError:
    #     return {"status": "error", "message": "Invalid response from server"}

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
    back = types.KeyboardButton('Назад')
    markup2.row(imp, study)
    markup2.row(event)
    markup2.row(back)
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
    bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=create_categories())

@bot.message_handler(func=lambda message: message.text == 'Назад')
def back(message):
    bot.send_message(message.chat.id, 'Вы в главном меню!', reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text in ['Важное', 'Развлекательное', 'Обучение'])
def category_sub(message):
    category = message.text
    bot.send_message(message.chat.id, f'Вы успешно подписались на {category}!',
                     reply_markup=create_keyboard())
    person = {
        "user_id": message.chat.id,
        "category": category
    }
    send_data_to_server(person)

@bot.message_handler(commands=['unsub'])
def unsubscribe(message):
    bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())

    person = {
        "user_id": message.chat.id,
        "delete": "Отписка"
    }

    send_data_to_server(person)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, f'Список команд:\n{command_list}', reply_markup=create_keyboard())

@bot.message_handler(commands=['recent'])
def recent_event(message):
    bot.send_message(message.chat.id, 'recent_event', reply_markup=create_keyboard())

@bot.message_handler(commands=['upcoming'])
def upcoming_events(message):
    bot.send_message(message.chat.id, 'upcoming_events', reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Отписаться')
def unsub(message):
    bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())

    person = {
        "user_id": message.chat.id,
        "delete": "Отписка"
    }

    response = send_data_to_server(person)
    # print(f"Response from server: {response}")

@bot.message_handler(
    func=lambda message: message.text in ['Подписаться', 'Список команд', 'Последнее событие', 'Предстоящие события'])
def on_click(message):
    msgTextDict = {
        'Подписаться': {
            'text': "Выберите категорию:",
            'markup': create_categories
        },
        'Список команд': {
            'text': f'Список команд:\n{command_list}',
            'markup': create_keyboard
        },
        'Последнее событие': {
            'text': "recent_event",
            'markup': create_keyboard
        },
        'Предстоящие события': {
            'text': "upcoming_events",
            'markup': create_keyboard
        }
    }
    replyDict = msgTextDict[message.text]
    bot.send_message(message.chat.id, replyDict['text'], reply_markup=replyDict['markup']())

@bot.message_handler()
def error(message):
    bot.send_message(message.chat.id, 'Неизвестная команда, используйте /help, чтобы вывести список команд',
                     parse_mode='Markdown', reply_markup=create_keyboard())

if __name__ == '__main__':
    socket_thread = threading.Thread(target=socket_client, daemon=True)
    socket_thread.start()
    bot.polling(none_stop=True)
