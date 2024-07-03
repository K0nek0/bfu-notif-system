import telebot
from telebot import types
import socket
import json

with open('credentials.TXT', 'r') as file:
    bot_token = file.read().strip()

bot = telebot.TeleBot(bot_token)
commands = bot.get_my_commands()
command_list = "\n".join([f"/{command.command} - {command.description}" for command in commands])

SERVER_HOST = '109.111.157.159'
SERVER_PORT = 8001


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((SERVER_HOST, SERVER_PORT))

# s.sendall(b"Hello, world")
# data = s.recv(1024)


def get_id_with_target_category(json_data, target_category):
    data = json.loads(json_data)

    for item in data:
        if item.get("category") == target_category:
            return item.get("id")
    return None


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


# def send_message(target_category):
#     data = json.loads(json_data)
#     for item in data:
#         if item.get("category") == target_category:
#             user_id = item.get("id")
#             bot.send_message(user_id, "Событие!!", reply_markup=create_keyboard())

# target_category = "Обучение"
# data = json.loads(json_data)
# for item in data:
#     if item.get("category") == target_category:
#         send_message(target_category)

# def send_data_to_server(data):
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#             client_socket.connect((SERVER_HOST, SERVER_PORT))
#             client_socket.sendall(json.dumps(data).encode())
#             response = client_socket.recv(1024)
#             return json.loads(response.decode())
#     except ConnectionRefusedError:
#         return {"status": "error", "message": "Could not connect to server"}
#     except TimeoutError:
#         return {"status": "error", "message": "Connection timed out"}

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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))

        category = message.text
        bot.send_message(message.chat.id, f'Вы успешно подписались на {category}!',
                         reply_markup=create_keyboard())
        person = {
            "user_id": message.chat.id,
            "category": category
        }

        json_data = json.dumps(person, ensure_ascii=False)
        s.sendall(json_data.encode('utf-8'))

        data = s.recv(1024)
        json_data = json.loads(data.decode('utf-8'))
        json_data = json.dumps(json_data, ensure_ascii=False)
        print(json_data)



@bot.message_handler(commands=['unsub'])
def unsubscribe(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())

        person = {
            "user_id": message.chat.id,
            "delete": "Отписка"
        }

        json_data = json.dumps(person, ensure_ascii=False)
        s.sendall(json_data.encode('utf-8'))

        # data = s.recv(1024)
        # print(data.decode('utf-8'))


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


@bot.message_handler(func=lambda message: message.text == 'Отписаться')
def unsub(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())

        person = {
            "user_id": message.chat.id,
            "delete": "Отписка"
        }

        json_data = json.dumps(person, ensure_ascii=False)
        s.sendall(json_data.encode('utf-8'))

        # data = s.recv(1024)
        # print(data.decode('utf-8'))
@bot.message_handler(
    func=lambda message: message.text in ['Подписаться', 'Список команд', 'Последнее событие',
                                          'Предстоящие события'])
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
                     parse_mode='Markdown',
                     reply_markup=create_keyboard())


bot.polling(none_stop=True)
