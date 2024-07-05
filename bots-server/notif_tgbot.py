import telebot
from telebot import types
import socket
import json
import threading
from datetime import datetime

with open('credentials.TXT', 'r') as file:
    bot_token = file.read().strip()

bot = telebot.TeleBot(bot_token)
commands = bot.get_my_commands()
command_list = "\n".join([f"/{command.command} - {command.description}" for command in commands])

SERVER_HOST = '109.111.157.159'
SERVER_PORT = 8001

client_socket = None
target_users = []
events_list = []
notif_user = {}

data_received = threading.Condition()


def socket_client():
    global target_users
    global client_socket
    global notif_user
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                json_data = data.decode('utf-8')
                data_dict = json.loads(json_data)
                notif_value = json.loads(json_data)

                if isinstance(data_dict, list):

                    headers = ["id", "title", "description", "category_id", "created_at", "event_time"]
                    data_dict.insert(0, headers)
                    data_dict = [dict(zip(headers, values)) for values in data_dict[1:]]

                if isinstance(data_dict, dict):
                    category_id = int(notif_value.get('category_id', 0))
                    if category_id == 1:
                        notif_value['category_id'] = 'Важное'
                    elif category_id == 2:
                        notif_value['category_id'] = 'Мероприятие'
                    elif category_id == 3:
                        notif_value['category_id'] = 'Обучение'

                    notif_user = notif_value
                    send_notif(notif_user)

                target_users = data_dict

            else:
                print("No data received, closing connection")
                break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


def send_notif(notif_user):
    users_id = notif_user.get("users_id")
    desc = notif_user.get("description")
    title = notif_user.get("title")
    event_time = notif_user.get("event_time")

    for user_id in users_id:
        notif_message = (
            f"*{title}* ({event_time.replace('T', ' ')})\n"
            f"{desc}\n"
        )
        bot.send_message(int(user_id[0]), notif_message, parse_mode='Markdown', reply_markup=create_keyboard())


def send_data_to_server(data):
    try:
        if isinstance(data, dict):
            json_data = json.dumps(data, ensure_ascii=False)
            print(f"Sending to server: {json_data}")
            client_socket.sendall(json_data.encode('utf-8'))
        elif isinstance(data, str):
            print(f"Sending string to server: {data}")
            client_socket.sendall(data.encode('utf-8'))
        else:
            print(f"Unsupported data type: {type(data)}")
            return "Unsupported data type"

    except ConnectionRefusedError:
        return "Could not connect to server"
    except TimeoutError:
        return "Connection timed out"


def create_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sub_btn = types.KeyboardButton('Подписаться')
    unsub_btn = types.KeyboardButton('Отписаться')
    help_btn = types.KeyboardButton('Список команд')
    recent_btn = types.KeyboardButton('Последнее событие')
    upcoming_btn = types.KeyboardButton('Предстоящее событие')
    markup.row(sub_btn, unsub_btn)
    markup.row(recent_btn, upcoming_btn)
    markup.row(help_btn)
    return markup


def create_categories():
    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    imp = types.KeyboardButton('Важное')
    event = types.KeyboardButton('Мероприятие')
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


@bot.message_handler(func=lambda message: message.text in ['Важное', 'Мероприятие', 'Обучение'])
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


def wait_for_data(timeout=1):

    with data_received:
        data_received.wait(timeout)
        return len(target_users) > 0


def event_handler(target_users, process):
    relevant_event_details = None
    event_datetime = None
    print(f"target_users in event_handler: {target_users}")

    if process == "recent":
        for item in target_users:
            event_time = item.get("event_time")
            event_datetime = datetime.strptime(event_time, '%Y-%m-%dT%H:%M')

            if event_datetime <= datetime.now():
                if relevant_event_details is None or event_datetime > datetime.strptime(
                        relevant_event_details["event_time"], '%Y-%m-%dT%H:%M'):
                    relevant_event_details = item

    elif process == "upcoming":
        for item in target_users:
            event_time = item.get("event_time")
            event_datetime = datetime.strptime(event_time, '%Y-%m-%dT%H:%M')

            if event_datetime > datetime.now():
                if relevant_event_details is None or event_datetime < datetime.strptime(
                        relevant_event_details["event_time"], '%Y-%m-%dT%H:%M'):
                    relevant_event_details = item

    return relevant_event_details


@bot.message_handler(commands=['recent'])
def recent_handler(message):
    global target_users

    notif = {
        "get": "Дай"
    }

    send_data_to_server(notif)


    if wait_for_data():
        event_details = event_handler(target_users, "recent")
        if event_details:
            response_message = (
                f"Последнее событие:\n"
                f"Заголовок: {event_details['title']}\n"
                f"Описание: {event_details['description']}\n"
                f"Время события: {event_details['event_time'].replace('T', ' ')}"
            )
        else:
            response_message = "Нет событий, произошедших до текущего времени"
    else:
        response_message = "Нет данных о событиях"

    bot.send_message(message.chat.id, response_message, reply_markup=create_keyboard())
    target_users = []


@bot.message_handler(commands=['upcoming'])
def upcoming_events(message):
    global target_users

    notif = {
        "get": "Дай"
    }

    send_data_to_server(notif)


    if wait_for_data():
        event_details = event_handler(target_users, "upcoming")
        if event_details:
            response_message = (
                f"Предстоящее событие:\n"
                f"Заголовок: {event_details['title']}\n"
                f"Описание: {event_details['description']}\n"
                f"Время события: {event_details['event_time'].replace('T', ' ')}"
            )
        else:
            response_message = "Новых событий нет"
    else:
        response_message = "Нет данных о событиях"

    bot.send_message(message.chat.id, response_message, reply_markup=create_keyboard())
    target_users = []


@bot.message_handler(func=lambda message: message.text == 'Последнее событие')
def recent_handler(message):
    global target_users

    notif = {
        "get": "Дай"
    }

    send_data_to_server(notif)


    if wait_for_data():
        event_details = event_handler(target_users, "recent")
        if event_details:
            response_message = (
                f"Последнее событие:\n"
                f"Заголовок: {event_details['title']}\n"
                f"Описание: {event_details['description']}\n"
                f"Время события: {event_details['event_time'].replace('T', ' ')}"
            )
        else:
            response_message = "Нет событий, произошедших до текущего времени"
    else:
        response_message = "Нет данных о событиях"

    bot.send_message(message.chat.id, response_message, reply_markup=create_keyboard())
    target_users = []


@bot.message_handler(func=lambda message: message.text == 'Предстоящее событие')
def upcoming_events(message):
    global target_users

    notif = {
        "get": "Дай"
    }

    send_data_to_server(notif)


    if wait_for_data():
        event_details = event_handler(target_users, "upcoming")
        if event_details:
            response_message = (
                f"Предстоящее событие:\n"
                f"Заголовок: {event_details['title']}\n"
                f"Описание: {event_details['description']}\n"
                f"Время события: {event_details['event_time'].replace('T', ' ')}"
            )
        else:
            response_message = "Новых событий нет"
    else:
        response_message = "Нет данных о событиях"

    bot.send_message(message.chat.id, response_message, reply_markup=create_keyboard())
    target_users = []


@bot.message_handler(func=lambda message: message.text == 'Отписаться')
def unsub(message):
    bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!', reply_markup=create_keyboard())

    person = {
        "user_id": message.chat.id,
        "delete": "Отписка"
    }

    send_data_to_server(person)


@bot.message_handler(
    func=lambda message: message.text in ['Подписаться', 'Список команд'])
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
