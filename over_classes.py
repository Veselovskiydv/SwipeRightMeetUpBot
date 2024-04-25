from telebot import types
from telebot.util import quick_markup


class JSONDataAdapter:  # work only with profiles
    @staticmethod
    def to_json(obj: dict) -> dict:
        dict_for_json = {}
        try:
            for key, value in obj.items():
                dict_for_json[key] = value.__dict__
        except AttributeError:
            print("Incorrect structure!")
        else:
            return dict_for_json

    @staticmethod
    def from_json(obj: dict) -> dict:
        dict_normalized = {}
        try:
            for key, value in obj.items():
                username = value["username"]
                name = value["name"]
                # surname = value["surname"]
                sex = value["sex"]
                age = value["age"]
                desc = value["desc"]
                photo = value["photo"]
                dict_normalized[int(key)] = Profile(
                    username, name, sex, age, desc, photo
                )
        except AttributeError:
            print("Incorrect structure!")
        else:
            return dict_normalized


class Metrics:
    def __init__(self, dictionary, key, default=None):
        self.dict = dictionary
        self.key = key
        self.default = default

    @property
    def val(self):
        return self.dict.get(self.key, self.default)

    @val.setter
    def val(self, value):
        self.dict[self.key] = value


class Profile:
    def __init__(self, username, name="", sex=None, age=-1, description="", photo=""):
        self.username = username
        self.name = name
        # self.surname = surname
        self.sex = sex
        self.age = age
        self.desc = description
        self.photo = photo

    def __str__(self) -> str:
        short_text = lambda x: x if len(x) < 30 else x[:10] + "..." + x[-10:]
        return (
            f"username: {self.username}\n"
            f"Имя: {self.name}\n"
            # f"Фамилия: {self.surname}\n"
            f"пол: {self.sex}\n"
            f"возраст: {self.age}\n"
            f"описание: {short_text(self.desc)}\n"
            f"фото: {self.photo[:10]+'...'+self.photo[-10:]}\n"
        )


class MainMenu:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_tail(number: float) -> float:
        """get one digit after a floating point

        Args:
            number (float): state of the user

        Returns:
            int: one digit after a floating point
        """
        return int(number * 10 % 10)

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

    def create_profile(self, message, state, temp_profile):
        chat_id = message.chat.id
        cur_username = message.from_user.username

        if self.get_tail(state.val) == 0:
            temp_profile.val = Profile(cur_username)
            self.bot.send_message(message.chat.id, "Укажите свое имя")
            state.val += 0.1
            print(temp_profile.val)
        elif self.get_tail(state.val) == 1:
            name = message.text
            # check correct input
            temp_profile.val.name = name

            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
                row_width=2,
                selective=True,
            )
            male = types.KeyboardButton("М")
            female = types.KeyboardButton("Ж")
            markup.add(male, female)

            self.bot.send_message(
                message.chat.id, "Укажите свой пол 👇", reply_markup=markup
            )
            state.val += 0.1
            print(temp_profile.val)
        elif self.get_tail(state.val) == 2:
            sex = message.text
            # check correct input
            temp_profile.val.sex = sex
            # remove keyboard(sex)
            rmarkup = types.ReplyKeyboardRemove(selective=True)
            self.bot.send_message(
                message.chat.id, "Укажите свой возраст", reply_markup=rmarkup
            )
            state.val += 0.1
            print(temp_profile.val)
        elif self.get_tail(state.val) == 3:
            age = message.text
            # check correct input
            temp_profile.val.age = int(age)
            self.bot.send_message(message.chat.id, "Расскажите о себе")
            state.val += 0.1
            print(temp_profile.val)
        elif self.get_tail(state.val) == 4:
            description = message.text
            # check correct input
            temp_profile.val.desc = description
            self.bot.send_message(
                message.chat.id, "Загрузите одну фотографию для своего профиля"
            )
            state.val += 0.1
            print(temp_profile.val)
        elif self.get_tail(state.val) == 5:
            try:
                photo = message.photo[-1]
            except TypeError:
                self.bot.send_message(
                    message.chat.id,
                    "Ошибка загрузки фотографии. Попробуйте создать профиль еще раз!",
                )
                state.val = "main_menu"
                print(temp_profile.val)
                return
            # check correct input
            file_info = self.bot.get_file(photo.file_id)
            temp_profile.val.photo = file_info.file_id
            # print(file_info)
            downloaded_file = self.bot.download_file(file_info.file_path)

            markup = self.main_menu()
            self.bot.send_message(
                message.chat.id, "Профиль успешно создан! ✅", reply_markup=markup
            )

            self.bot.send_photo(
                message.chat.id, photo=downloaded_file, caption=temp_profile.val
            )

            # сохроняем профиль в файл
            self.bot.profiles[chat_id] = temp_profile.val
            from IOFs import write_profiles_json
            write_profiles_json(self.bot.profiles)
            state.val = "main_menu"

    def view_profile(self, chat_id, state, temp_profile):
        if self.get_tail(state.val) == 0:
            temp_profile.val = self.bot.profiles.get(chat_id, None)
            if temp_profile.val is None:
                markup = self.main_menu()
                self.bot.send_message(
                    chat_id,
                    "Вы ещё не создали свой профиль!",
                    reply_markup=markup,
                )
            else:
                print(chat_id, self.bot.profiles[chat_id].name)  # !!!!!!!!!!!!!!

                file_info = self.bot.get_file(temp_profile.val.photo)
                downloaded_file = self.bot.download_file(file_info.file_path)

                markup = self.main_menu()
                self.bot.send_photo(
                    chat_id,
                    photo=downloaded_file,
                    caption=temp_profile.val,
                    reply_markup=markup,
                )
            state.val = "main_menu"

    def find_friends(self, chat_id, state):
        if self.get_tail(state.val) == 0:
            id_to = self.bot.get_stranger(chat_id)  # stranger's id
            if id_to:
                stranger = self.bot.profiles[id_to]

                file_info = self.bot.get_file(stranger.photo)
                downloaded_file = self.bot.download_file(file_info.file_path)

                markup = quick_markup(
                    {
                        "👍": {"callback_data": f"like {id_to}"},
                        "👎": {"callback_data": f"dislike {id_to}"},
                    }
                )
                self.bot.send_photo(
                    chat_id,
                    photo=downloaded_file,
                    caption=stranger,
                    reply_markup=markup,
                )
            else:
                markup = self.main_menu()
                self.bot.send_message(
                    chat_id,
                    "Нам некого Вам предложить😢\nПовторите попытку позже!",
                    reply_markup=markup,
                )
                state.val = "main_menu"
