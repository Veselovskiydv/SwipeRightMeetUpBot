from time import sleep
import telebot
from telebot import types
from telebot.util import quick_markup

from IOFs import (
    write_interactions,
    read_interactions,
    # write_profiles,
    # read_profiles,
    write_profiles_json,
    read_profiles_json,
)
from over_classes import JSONDataAdapter, Metrics, Profile


class Bot(telebot.TeleBot):
    def __init__(self, token):
        super().__init__(token)
        self.states = {}  # { id->int: state->Any[float, str] }
        self.profiles = JSONDataAdapter.from_json(
            read_profiles_json()
        )  # { id->int: Profile->class }
        self.temp_profiles = {}
        self.interactions = read_interactions()  # { id_from->int: list(id_to->int) }

    def get_stranger(self, id_from):
        interaction = self.interactions.get(id_from, {"like": [], "dislike": []})
        for id_to in self.profiles.keys():
            if (
                id_to != id_from
                and id_to not in interaction["like"]
                and id_to not in interaction["dislike"]
            ):
                return id_to

    @staticmethod
    def main_menu():
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

    def edit_used_markup(self, message, text):
        markup = quick_markup({text: {"callback_data": "used"}})
        self.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=markup,
        )


bot = Bot("7156409593:AAGtiGecftVC_imFf7UtZaCdJyv8VZBtYmg")


@bot.message_handler(commands=["start", "menu"])
def start(message):
    chat_id = message.chat.id
    markup = bot.main_menu()
    bot.states[chat_id] = "main_menu"
    bot.send_message(message.chat.id, "Выберите команду 👇", reply_markup=markup)


@bot.message_handler(content_types=["text", "photo"])
def commands_handler(message):
    chat_id = message.chat.id
    # state = bot.states.get(chat_id, "main_menu")
    state = Metrics(bot.states, chat_id, "main_menu")
    temp_profile = Metrics(bot.temp_profiles, chat_id)

    if state.val == "main_menu":
        if message.text == "Создать профиль":
            state.val = 1.0
        elif message.text == "Посмотреть профиль":
            state.val = 2.0
        elif message.text == "Искать друзей":
            state.val = 3.0

    if int(state.val) == 1:
        temp_profile.val = Profile()
        if state.val == 1.0:
            bot.send_message(message.chat.id, "Укажите свое имя, фамилию")
            state.val = 1.1
        elif state.val == 1.1:
            name, surname = message.text.split()
            # check correct input
            temp_profile.val.name, temp_profile.val.surname = name, surname

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
            state.val = 1.2
        elif state.val == 1.2:
            sex = message.text
            # check correct input
            temp_profile.val.sex = sex
            # remove keyboard(sex)
            rmarkup = types.ReplyKeyboardRemove(selective=True)
            bot.send_message(
                message.chat.id, "Укажите свой возраст", reply_markup=rmarkup
            )
            state.val = 1.3
        elif state.val == 1.3:
            age = message.text
            # check correct input
            temp_profile.val.age = int(age)
            bot.send_message(message.chat.id, "Расскажите о себе")
            state.val = 1.4
        elif state.val == 1.4:
            description = message.text
            # check correct input
            temp_profile.val.desc = description
            bot.send_message(
                message.chat.id, "Загрузите одну фотографию для своего профиля"
            )
            state.val = 1.5
        elif state.val == 1.5:
            photo = message.photo[-1]
            # check correct input
            file_info = bot.get_file(photo.file_id)
            temp_profile.val.photo = file_info.file_id
            # print(file_info)
            downloaded_file = bot.download_file(file_info.file_path)

            markup = bot.main_menu()
            bot.send_message(
                message.chat.id, "Профиль успешно создан! ✅", reply_markup=markup
            )

            bot.send_photo(
                message.chat.id, photo=downloaded_file, caption=temp_profile.val
            )

            # сохроняем профиль в файл
            bot.profiles[chat_id] = temp_profile.val
            write_profiles_json(JSONDataAdapter.to_json(bot.profiles))
            state.val = "main_menu"

    elif int(state.val) == 2:
        if state.val == 2.0:
            temp_profile.val = bot.profiles.get(message.chat.id, None)
            if temp_profile.val is None:
                markup = bot.main_menu()
                bot.send_message(
                    message.chat.id,
                    "Вы ещё не создали свой профиль!",
                    reply_markup=markup,
                )
            else:
                print(message.chat.id, bot.profiles[chat_id].name)  # !!!!!!
                print(bot.profiles.keys())  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                file_info = bot.get_file(temp_profile.val.photo)
                downloaded_file = bot.download_file(file_info.file_path)

                markup = bot.main_menu()
                bot.send_photo(
                    message.chat.id,
                    photo=downloaded_file,
                    caption=temp_profile.val,
                    reply_markup=markup,
                )
            state.val = "main_menu"

    elif int(state.val) == 3:
        if state.val == 3.0:
            id_to = bot.get_stranger(message.chat.id)  # stranger's id
            if id_to:
                stranger = bot.profiles[id_to]

                file_info = bot.get_file(stranger.photo)
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
                    caption=stranger,
                    reply_markup=markup,
                )
            else:
                markup = bot.main_menu()
                bot.send_message(
                    message.chat.id,
                    "Нам некого Вам предложить😢\nПовторите попытку позже!",
                    reply_markup=markup,
                )
                state.val = "main_menu"


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    chat_id = call.message.chat.id
    if call.data != "used":
        reaction, id_to = call.data.split()
        id_to = int(id_to)

        if (
            id_to
            not in bot.interactions[chat_id]["like"]
            + bot.interactions[chat_id]["dislike"]
        ):
            bot.edit_used_markup(call.message, ("👍" if reaction == "like" else "👎"))

            bot.interactions.setdefault(
                call.message.chat.id, {"like": [], "dislike": []}
            )[reaction].append(id_to)

            write_interactions(bot.interactions)

            sleep(2)
            commands_handler(call.message)  # get new stranger
        else:
            # edit_used_markup(
            #     call.message, ("👍" if id_to in interactions[chat_id]["like"] else "👎")
            # )

            bot.delete_message(call.message.chat.id, call.message.id)


bot.polling(non_stop=True)
