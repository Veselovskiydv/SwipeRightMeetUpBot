from time import sleep

from IOFs import write_interactions
from main_class import Bot
from over_classes import Metrics


bot = Bot("7156409593:AAGtiGecftVC_imFf7UtZaCdJyv8VZBtYmg")


bot.register_callback_query_handler(bot.check_username, func=lambda call: True)
bot.register_message_handler(bot.check_username, func=lambda msg: True)


@bot.message_handler(commands=["start", "menu"])
def start(message):
    chat_id = message.chat.id
    state = Metrics(bot.states, chat_id, "main_menu")  # state of current user
    bot.MainMenu.choose_command(chat_id, state)


@bot.message_handler(content_types=["text", "photo"])
def commands_handler(message):
    chat_id = message.chat.id
    state = Metrics(bot.states, chat_id, "main_menu")  # state of current user
    temp_profile = Metrics(bot.temp_profiles, chat_id)  # temp profile of current user

    if state.val == "main_menu":
        if message.text == "Создать профиль":
            state.val = 1.0
            markup = bot.CancelMenu.cancel_markup()
            bot.send_message(
                message.chat.id,
                "Для создания профиля заполните все данные 🗒️",
                reply_markup=markup,
            )
        elif message.text == "Посмотреть профиль":
            state.val = 2.0
        elif message.text == "Искать друзей":
            state.val = 3.0

            if bot.check_profile(chat_id):
                markup = bot.CancelMenu.cancel_markup()
                bot.send_message(
                    message.chat.id, "Бот начал поиск друзей...", reply_markup=markup
                )
                sleep(1)
            else:
                markup = bot.MainMenu.main_markup()
                bot.send_message(
                    chat_id, "Вы ещё не создали свой профиль!", reply_markup=markup
                )
                state.val = "main_menu"
                return
        elif message.text == "Удалить аккаунт":
            state.val = 4.0
        else:
            bot.send_message(chat_id, "Нажмите на одну из кнопок главного меню!")
            return

    if int(state.val) == 1:
        bot.MainMenu.create_profile(message, state, temp_profile)

    elif int(state.val) == 2:
        bot.MainMenu.view_profile(chat_id, bot.profiles.get(chat_id, None))
        bot.MainMenu.choose_command(chat_id, state)

    elif int(state.val) == 3:
        bot.MainMenu.find_friends(message, chat_id, state)

    elif int(state.val) == 4:
        bot.MainMenu.remove_account(chat_id, state)

    del state, temp_profile  # clear memory


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    chat_id = call.message.chat.id
    chat_username = call.from_user.username
    if call.data != "used":
        reaction, id_to = call.data.split()
        id_to = int(id_to)

        # if bot.profiles.get(id_to, None) is None:
        username_to = bot.profiles[id_to].username  # write check profile!!!

        if (
            id_to
            not in bot.interactions.get(chat_id, {"like": []})["like"]
            + bot.interactions.get(chat_id, {"dislike": []})["dislike"]
        ):
            if reaction in ("like", "dislike"):

                bot.edit_used_markup(call.message, ("👍" if reaction == "like" else "👎"))

                bot.interactions.setdefault(
                    call.message.chat.id, {"like": [], "dislike": []}
                )[reaction].append(id_to)

                write_interactions(bot.interactions)

                if reaction == "like" and bot.check_matching(chat_id, id_to):
                    message_matching = lambda username: (  # noqa: E731
                        f"Этому пользователю тоже понравился ваш профиль!🎉\n @{username}"
                    )
                    bot.MainMenu.view_profile(chat_id, bot.profiles[id_to])
                    bot.send_message(chat_id, message_matching(username_to), reply_to_message_id=call.message.id+1)
                    bot.send_message(id_to, message_matching(chat_username) + " 👇")
                    bot.MainMenu.view_profile(id_to, bot.profiles[chat_id])

                sleep(2)
                if Metrics(bot.states, chat_id).val is not None:  # if bot wasn't stopped
                    commands_handler(call.message)  # get new stranger

            elif reaction == "give_photos":

                profile_stranger = bot.profiles[id_to]

                if len(profile_stranger.photo) > 1:
                    from telebot.types import InputMediaPhoto

                    medias = [InputMediaPhoto(file_id) for file_id in profile_stranger.photo]
                    bot.send_media_group(
                        chat_id=chat_id, media=medias[1:], protect_content=True
                    )
                else:
                    bot.send_message(
                        chat_id,
                        "Пользователь загрузил только одну фотографию!",
                    )

        else:
            bot.delete_message(chat_id, call.message.id)
            # edit_used_markup(
            #     call.message, ("👍" if id_to in interactions[chat_id]["like"] else "👎")
            # )


bot.polling(non_stop=True)
