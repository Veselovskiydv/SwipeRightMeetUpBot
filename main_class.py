import telebot
from telebot.handler_backends import ContinueHandling
from telebot.util import quick_markup

from IOFs import read_interactions, read_profiles_json, write_profiles_json
from over_classes import CancelMenu, MainMenu, SaveProfileMenu


class Bot(telebot.TeleBot):
    def __init__(self, token):
        super().__init__(token, threaded=False)
        self.states = {}  # { id->int: state->Any[float, str] }
        self.profiles = read_profiles_json()  # { id->int: Profile->class }
        self.temp_profiles = {}  # { id->int: Profile->class } for creating profiles
        self.interactions = read_interactions()  # { id_from->int: list(id_to->int) }
        self.MainMenu = MainMenu(self)  # for functions of main menu
        self.CancelMenu = CancelMenu(self)  # for functions of cancel menu
        self.SaveProfileMenu = SaveProfileMenu(self) # for functions of save profile menu

    def get_stranger(self, id_from):
        interaction = self.interactions.get(id_from, {"like": [], "dislike": []})
        for id_to in self.profiles.keys():
            if (
                id_to != id_from
                and id_to not in interaction["like"]
                and id_to not in interaction["dislike"]
            ):
                return id_to

    def edit_used_markup(self, message, text):
        markup = quick_markup({text: {"callback_data": "used"}})
        self.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=markup,
        )

    def check_matching(self, id_from, id_to):
        if id_from in self.interactions.get(id_to, {"like": []})["like"]:
            return True
        return False

    def check_username(self, message):
        print("Checking username...", end=" ")
        try:
            chat_id = message.chat.id
            cur_username = message.from_user.username
        except AttributeError:
            call = message
            chat_id = call.message.chat.id
            cur_username = call.from_user.username

        if cur_username is None:
            self.send_message(chat_id, "Пожалуйста, заполните ваше имя пользователя!")
        else:
            if self.profiles.get(chat_id, None):
                if cur_username != self.profiles[chat_id].username:
                    print("\nUpdating username...", end=" ")
                    self.profiles[chat_id].username = cur_username
                    write_profiles_json(self.profiles)
                print("Correct!")
        return ContinueHandling()

    def check_profile(self, chat_id):
        return self.profiles.get(chat_id, None) is not None
