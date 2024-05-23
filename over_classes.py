from telebot import types
from telebot.types import InputMediaPhoto
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
    def __init__(self, username, name="", sex=None, age=-1, description="", photo=None):
        self.username = username
        self.name = name
        # self.surname = surname
        self.sex = sex
        self.age = age
        self.desc = description
        self.photo = photo if photo else []

    def __str__(self) -> str:
        short_text = lambda x: x if len(x) < 30 else x[:10] + "..." + x[-10:]
        short_file_id = lambda x: x[:5] + "..." + x[-5:]
        return (
            f"username: {self.username}\n"
            f"Имя: {self.name}\n"
            # f"Фамилия: {self.surname}\n"
            f"пол: {self.sex}\n"
            f"возраст: {self.age}\n"
            f"описание: {short_text(self.desc)}\n"
            f"фото: {"\n".join([short_file_id(file_id) for file_id in self.photo])}\n"
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
    def main_markup():
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            row_width=2,
        )
        btn1 = types.KeyboardButton("Создать профиль")
        btn2 = types.KeyboardButton("Посмотреть профиль")
        btn3 = types.KeyboardButton("Искать друзей")
        btn4 = types.KeyboardButton("Удалить аккаунт")
        markup.add(btn1, btn2, btn3, btn4)
        return markup

    def create_profile(self, message: types.Message, state, temp_profile):
        chat_id = message.chat.id
        cur_username = message.from_user.username
        if message.text == "Выйти":
            self.bot.CancelMenu.cancel(chat_id, state)
            return

        if self.get_tail(state.val) == 0:
            temp_profile.val = Profile(cur_username)
            self.bot.send_message(message.chat.id, "1. Укажите свое имя")
            state.val += 0.1

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
                message.chat.id, "2. Укажите свой пол 👇", reply_markup=markup
            )
            state.val += 0.1

        elif self.get_tail(state.val) == 2:
            sex = message.text
            # check correct input
            temp_profile.val.sex = sex
            # remove keyboard(sex)
            # rmarkup = types.ReplyKeyboardRemove(selective=True)
            markup = self.bot.CancelMenu.cancel_markup()
            self.bot.send_message(
                message.chat.id, "3. Укажите свой возраст", reply_markup=markup
            )
            state.val += 0.1

        elif self.get_tail(state.val) == 3:
            age = message.text
            # check correct input
            try:
                temp_profile.val.age = int(age)
            except ValueError:
                self.bot.send_message(message.chat.id, "Введите корректный возраст!")
            else:
                self.bot.send_message(message.chat.id, "4. Расскажите о себе")
                state.val += 0.1

        elif self.get_tail(state.val) == 4:
            description = message.text
            # check correct input
            temp_profile.val.desc = description
            markup = self.bot.SaveProfileMenu.save_profile_markup()
            self.bot.send_message(
                message.chat.id,
                "5. Загрузите одну или несколько фотографий для вашего профиля",
                reply_markup=markup,
            )
            state.val += 0.1

        elif self.get_tail(state.val) == 5:
            if message.text == "Сохранить профиль":
                if temp_profile.val.photo:
                    self.bot.SaveProfileMenu.save_profile(chat_id, state, temp_profile)
                else:
                    self.bot.send_message(
                        chat_id, "Вы не загрузили ещё ни одной фотографии!"
                    )
                return
            if message.text == "Отмена":
                self.bot.CancelMenu.cancel(chat_id, state)
                return
            try:
                print(f"{message.photo=}" f"{message.media_group_id=}\n\n")
                photo = message.photo[-1]
                # check correct input
                file_info = self.bot.get_file(photo.file_id)
                temp_profile.val.photo.append(file_info.file_id)
            except TypeError:
                self.bot.send_message(
                    message.chat.id,
                    "Ошибка загрузки фотографии! Попробуйте загрузить фотографию ещё раз.",
                )
                # state.val = "main_menu"
                print(temp_profile.val)

            # print(len(temp_profile.val.photo))
            # print(file_info)
            # downloaded_file = self.bot.download_file(file_info.file_path)

    def view_profile(self, chat_id, state, viewing_profile: Profile):
        if self.get_tail(state.val) == 0:
            if viewing_profile is None:
                markup = self.main_markup()
                self.bot.send_message(
                    chat_id,
                    "Вы ещё не создали свой профиль!",
                    reply_markup=markup,
                )
            else:
                print(chat_id, viewing_profile.name)  # !!!!!!!!!!!!!!

                # file_info = self.bot.get_file(temp_profile.val.photo)
                # downloaded_file = self.bot.download_file(file_info.file_path)

                # self.bot.send_photo(
                #     chat_id,
                #     photo=downloaded_file,
                #     caption=temp_profile.val,
                #     reply_markup=markup,
                # )
                medias = [InputMediaPhoto(file_id) for file_id in viewing_profile.photo]
                medias[0].caption = str(viewing_profile)
                self.bot.send_media_group(
                    chat_id=chat_id, media=medias, protect_content=True
                )

                markup = self.main_markup()
                self.bot.send_message(
                    chat_id, "Выберите команду 👇", reply_markup=markup
                )

            state.val = "main_menu"

    def find_friends(self, message, chat_id, state):
        if self.get_tail(state.val) == 0:
            if message.text == "Выйти":
                self.bot.CancelMenu.stop_search(chat_id, state)
                return
            id_to = self.bot.get_stranger(chat_id)  # stranger's id
            if id_to:
                stranger = self.bot.profiles[id_to]

                markup = quick_markup(
                    {
                        "👍": {"callback_data": f"like {id_to}"},
                        "🖼️": {"callback_data": f"give_photos {id_to}"},
                        "👎": {"callback_data": f"dislike {id_to}"},
                    },
                    row_width=3,
                )
                file_info = self.bot.get_file(stranger.photo)
                downloaded_file = self.bot.download_file(file_info.file_path)

                self.bot.send_photo(
                    chat_id,
                    photo=downloaded_file,
                    caption=stranger,
                    reply_markup=markup,
                )

                # self.bot.MainMenu.view_profile(chat_id, state, stranger)
            else:
                markup = self.main_markup()
                self.bot.send_message(
                    chat_id,
                    "Нам некого Вам предложить😢\nПовторите попытку позже!",
                    reply_markup=markup,
                )
                state.val = "main_menu"

    def remove_account(self, chat_id, state):
        from IOFs import write_interactions, write_profiles_json

        self.bot.profiles.pop(chat_id, None)
        write_profiles_json(self.bot.profiles)

        self.bot.interactions.pop(chat_id, None)
        write_interactions(self.bot.interactions)

        markup = self.main_markup()
        self.bot.send_message(
            chat_id, "Данные об аккаунте успешно удалены! ✅", reply_markup=markup
        )
        state.val = "main_menu"


class CancelMenu:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def cancel_markup():
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            row_width=2,
        )
        btn1 = types.KeyboardButton("Выйти")
        markup.add(btn1)
        return markup

    def cancel(self, chat_id, state):
        markup = self.bot.MainMenu.main_markup()
        self.bot.send_message(chat_id, "Выход в главное меню...", reply_markup=markup)
        state.val = "main_menu"

    def stop_search(self, chat_id, state):
        state.val = "main_menu"
        markup = self.bot.MainMenu.main_markup()
        self.bot.send_message(chat_id, "Поиск остановлен", reply_markup=markup)


class SaveProfileMenu:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def save_profile_markup():
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            row_width=2,
        )
        btn1 = types.KeyboardButton("Сохранить профиль")
        btn2 = types.KeyboardButton("Отмена")
        markup.add(btn1, btn2)
        return markup

    def save_profile(self, chat_id, state, temp_profile):
        markup = self.bot.MainMenu.main_markup()
        self.bot.send_message(
            chat_id, "Профиль успешно создан! ✅", reply_markup=markup
        )
        # отправляем профиль пользователю
        self.bot.MainMenu.view_profile(chat_id, state, temp_profile.val)
        # сохроняем профиль в файл
        self.bot.profiles[chat_id] = temp_profile.val
        from IOFs import write_profiles_json

        write_profiles_json(self.bot.profiles)
        state.val = "main_menu"
