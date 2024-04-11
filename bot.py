import json
from time import sleep
import telebot
from telebot import types
from telebot.util import quick_markup
import dill as pickle

bot = telebot.TeleBot("7156409593:AAGtiGecftVC_imFf7UtZaCdJyv8VZBtYmg")

state = 0.0


class User:
    def __init__(self, name="", surname="", sex=None, age=-1, description="", photo=""):
        self.name = name
        self.surname = surname
        self.sex = sex
        self.age = age
        self.desc = description
        self.photo = photo

    def __str__(self) -> str:
        return (
            f"Имя: {self.name}\n"
            f"Фамилия: {self.surname}\n"
            f"пол: {self.sex}\n"
            f"возраст: {self.age}\n"
            f"описание: {self.desc if len(self.desc)<30 else self.desc[:10]+'...'+self.desc[-10:]}\n"
            f"фото: {self.photo[:10]+'...'+self.photo[-10:]}\n"
        )


def write_profiles(profiles):
    with open("profiles.pickle", "wb") as f:
        return pickle.dump(profiles, f)


def read_profiles():
    with open("profiles.pickle", "rb") as f:
        try:
            return pickle.load(f)
        except EOFError:
            write_profiles({})
            return {}


def write_interactions(interactions):
    with open("interactions.json", "w", encoding="utf-8") as f:
        return json.dump(interactions, f, indent=4)


def read_interactions():
    with open("interactions.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            data_copy = {}
            for key, val in data.items():
                data_copy[int(key)] = val
            return data_copy
        except EOFError:
            write_interactions({})
            return {}


def get_stranger(id_from):
    global user, profiles, interactions
    for id_to in profiles.keys():
        if (
            id_to != id_from
            and id_to
            not in interactions.get(id_from, {"like": [], "dislike": []})["like"]
            and id_to
            not in interactions.get(id_from, {"like": [], "dislike": []})["dislike"]
        ):
            return id_to


def main_menu(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        row_width=2,
    )
    btn1 = types.KeyboardButton("Создать профиль")
    btn2 = types.KeyboardButton("Посмотреть профиль")
    btn3 = types.KeyboardButton("Искать друзей")
    markup.add(btn1, btn2, btn3)
    return markup


@bot.message_handler(commands=["start", "menu"])
def start(message):
    global state
    markup = main_menu(message)
    state = "main_menu"
    bot.send_message(message.chat.id, "Выберите команду 👇", reply_markup=markup)


profiles = read_profiles()  # { id->int: User->class }
user = User()
interactions = read_interactions()  # { id_from->int: list(id_to->int) }


@bot.message_handler(content_types=["text", "photo"])
def commands_handler(message):
    global state, user, profiles
    if state == "main_menu":
        if message.text == "Создать профиль":
            state = 1.0
        elif message.text == "Посмотреть профиль":
            state = 2.0
        elif message.text == "Искать друзей":
            state = 3.0

    if int(state) == 1:
        if state == 1.0:
            bot.send_message(message.chat.id, "Укажите свое имя, фамилию")
            state = 1.1
        elif state == 1.1:
            name, surname = message.text.split()
            # check correct input
            user.name, user.surname = name, surname

            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
                row_width=2,
                selective=True,
            )
            male = types.KeyboardButton("М")
            female = types.KeyboardButton("Ж")
            markup.add(male, female)

            bot.send_message(
                message.chat.id, "Укажите свой пол 👇", reply_markup=markup
            )
            state = 1.2
        elif state == 1.2:
            sex = message.text
            # check correct input
            user.sex = sex
            # remove keyboard(sex)
            rmarkup = types.ReplyKeyboardRemove(selective=True)
            bot.send_message(
                message.chat.id, "Укажите свой возраст", reply_markup=rmarkup
            )
            state = 1.3
        elif state == 1.3:
            age = message.text
            # check correct input
            user.age = int(age)
            bot.send_message(message.chat.id, "Расскажите о себе")
            state = 1.4
        elif state == 1.4:
            description = message.text
            # check correct input
            user.desc = description
            bot.send_message(
                message.chat.id, "Загрузите одну фотографию для своего профиля"
            )
            state = 1.5
        elif state == 1.5:
            photo = message.photo[-1]
            # check correct input
            file_info = bot.get_file(photo.file_id)
            user.photo = file_info.file_id
            # print(file_info)
            downloaded_file = bot.download_file(file_info.file_path)
            # with open(photo.file_id+".jpg", 'wb') as new_file:
            #     new_file.write(downloaded_file)
            # bot.reply_to(message, "Фото успешно сохранено! 🖼️")

            markup = main_menu(message)
            bot.send_message(
                message.chat.id, "Профиль успешно создан! ✅", reply_markup=markup
            )

            bot.send_photo(message.chat.id, photo=downloaded_file, caption=user)

            # сохроняем профиль в файл
            profiles[message.chat.id] = user
            write_profiles(profiles)
            state = "main_menu"

    elif int(state) == 2:
        if state == 2.0:
            user = profiles.get(message.chat.id, None)
            if user is None:
                markup = main_menu(message)
                bot.send_message(
                    message.chat.id,
                    "Вы ещё не создали свой профиль!",
                    reply_markup=markup,
                )
            else:
                print(message.chat.id, profiles[message.chat.id].name)  # !!!!!!
                print(profiles.keys())  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                file_info = bot.get_file(user.photo)
                downloaded_file = bot.download_file(file_info.file_path)

                markup = main_menu(message)
                bot.send_photo(
                    message.chat.id,
                    photo=downloaded_file,
                    caption=user,
                    reply_markup=markup,
                )
            state = "main_menu"

    elif int(state) == 3:
        if state == 3.0:
            id_to = get_stranger(message.chat.id)
            if id_to:
                user = profiles[id_to]

                file_info = bot.get_file(user.photo)
                downloaded_file = bot.download_file(file_info.file_path)

                markup = quick_markup(
                    {
                        "👍": {"callback_data": f"like {id_to}"},
                        "👎": {"callback_data": f"dislike {id_to}"},
                    }
                )
                bot.send_photo(
                    message.chat.id,
                    photo=downloaded_file,
                    caption=user,
                    reply_markup=markup,
                )
                state = 3.1  # waiting press on button
            else:
                markup = main_menu(message)
                bot.send_message(
                    message.chat.id,
                    "Нам некого Вам предложить😢\nПовторите попытку позже!",
                    reply_markup=markup,
                )
                state = "main_menu"


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global state, user, profiles, interactions
    if state == 3.1 and call.data != "used":
        reaction, id_to = call.data.split()
        id_to = int(id_to)

        edit_used_markup(call.message, ("👍" if reaction == "like" else "👎"))

        interactions.setdefault(call.message.chat.id, {"like": [], "dislike": []})[
            reaction
        ].append(id_to)

        write_interactions(interactions)

        state = 3.0  # for get new stranger

        sleep(2)
        commands_handler(call.message)  # get new stranger


def edit_used_markup(message, text):
    markup = quick_markup({text: {"callback_data": "used"}})
    bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=message.id,
        reply_markup=markup,
    )


bot.polling(non_stop=True)
