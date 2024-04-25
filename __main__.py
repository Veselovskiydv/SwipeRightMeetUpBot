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
    markup = bot.main_menu.main_menu()
    bot.states[chat_id] = "main_menu"
    bot.send_message(message.chat.id, "Выберите команду 👇", reply_markup=markup)


@bot.message_handler(content_types=["text", "photo"])
def commands_handler(message):
    chat_id = message.chat.id
    state = Metrics(bot.states, chat_id, "main_menu")  # state of current user
    temp_profile = Metrics(bot.temp_profiles, chat_id)  # temp profile of current user

    if state.val == "main_menu":
        if message.text == "Создать профиль":
            state.val = 1.0
        elif message.text == "Посмотреть профиль":
            state.val = 2.0
        elif message.text == "Искать друзей":
            state.val = 3.0
        else:
            bot.send_message(chat_id, "Нажмите на одну из кнопок главного меню!")
            return

    if int(state.val) == 1:
        bot.main_menu.create_profile(message, state, temp_profile)

    elif int(state.val) == 2:
        bot.main_menu.view_profile(chat_id, state, temp_profile)

    elif int(state.val) == 3:
        bot.main_menu.find_friends(chat_id, state)

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
            bot.edit_used_markup(call.message, ("👍" if reaction == "like" else "👎"))

            bot.interactions.setdefault(
                call.message.chat.id, {"like": [], "dislike": []}
            )[reaction].append(id_to)

            write_interactions(bot.interactions)

            if reaction == "like" and bot.check_matching(chat_id, id_to):
                message_matching = lambda username: (  # noqa: E731
                    f"Some person has liked you too! 🎉\n @{username}"
                )
                bot.send_message(chat_id, message_matching(username_to))
                bot.send_message(id_to, message_matching(chat_username))

            sleep(3)
            if Metrics(bot.states, chat_id).val is not None:  # if bot was stopped
                commands_handler(call.message)  # get new stranger

        else:
            bot.delete_message(chat_id, call.message.id)
            # edit_used_markup(
            #     call.message, ("👍" if id_to in interactions[chat_id]["like"] else "👎")
            # )


bot.polling(non_stop=True)