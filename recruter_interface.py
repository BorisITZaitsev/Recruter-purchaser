from telebot import *
from custom_API import *
from datetime import datetime, timedelta


bot = TeleBot("7160462503:AAF2TsIXaehcOi-j_j60p4UN8yZ3_2tv-Vw")
context = ["refuse|", "interview|", "date|", "time|", "cancel|", "accept|"]


# _________________________________________Error_catcher________________________________________________________________


def r_error(message):
    bot.send_message(message.from_user.id, "Произошла ошибка. Возвращаю вас в меню рекрутера.")
    recr_menu(message)


def p_error(message):
    bot.send_message(message.from_user.id, "Произошла ошибка.\n"
                                           "У вас есть возможность пройти процесс регистрации кандидата заново "
                                           "в сообщени с информацией.\n"
                                           "Вашему рекрутеру также был направлен запрос на повторный пересыл "
                                           "информации о кандидате.")
    purch_menu(message)


# _________________________________________There_is_a_purchaser_interface_lower_________________________________________


@bot.callback_query_handler(func=lambda call: call.data == "p_menu")
def purch_menu(message):
    bot.send_message(message.from_user.id, "Уважаемый заказчик, ожидайте, пока вам придёт уведомление о "
                                           "новом кандидате.")


@bot.callback_query_handler(func=lambda call: any(i in call.data for i in context))
def selector(call):
    try:
        if "refuse|" in call.data:
            c_name = call.data.split("|")[-1]
            bot.send_message(call.from_user.id, f"Кандидату - {c_name}, успешно отказано!")
            r_name = read_candidates()[call.from_user.username][c_name]["r"]
            bot.send_message(read_nicknames()[r_name], f"Заказчик "
                                                       f"@{call.from_user.username} отказал кандидату {c_name}",
                             reply_markup=types.ReplyKeyboardRemove())
            del_file(read_candidates()[call.from_user.username][c_name]["f"])
            delete_from_candidates(call.from_user.username, c_name)
        elif "interview|" in call.data:
            markup = types.InlineKeyboardMarkup(row_width=1)
            now = datetime.now()
            c_name = call.data.split("|")[-1]
            for i in range(0, 7):
                date = now + timedelta(days=i)
                date = date.strftime("%d.%m.%Y")
                markup.add(telebot.types.InlineKeyboardButton(text=date, callback_data="date|" + date + "|" + c_name))
            coming_text = "Тогда нам нужно назначить дату собеседования! Выберите из предложенных в списке ниже!"
            bot.send_message(call.from_user.id, text=coming_text.format(call.from_user), reply_markup=markup)
        elif "date|" in call.data:
            data = call.data.split("|")
            date, c_name = data[-2], data[-1]
            markup = types.InlineKeyboardMarkup(row_width=1)
            for i in range(12, 24):
                full_int = "time|" + str(i) + ":00" + ";" + date + "|" + c_name
                markup.add(types.InlineKeyboardButton(text=str(i) + ":00", callback_data=full_int))
            coming_text = "Теперь выберите время из предложенных ниже вариантов."
            bot.send_message(call.from_user.id, text=coming_text.format(call.from_user), reply_markup=markup)
        elif "time|" in call.data:
            data = call.data.split("|")
            time_date, c_name = data[1:]
            time_date = datetime.strptime(time_date, "%H:%M;%d.%m.%Y")
            if time_date <= datetime.now():
                bot.send_message(call.from_user.id, "Вы назначили собеседовние на время, которое уже прошло. "
                                                    "Сейчас я верну вас на этап выбора даты.")
                call.data = "interview|" + c_name
                selector(call)
                return 0
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Да", callback_data="accept|" + data[1] + "|" + data[-1])
            btn2 = types.InlineKeyboardButton(text="Нет", callback_data="cancel|" + data[-1])
            markup.add(btn1, btn2)
            bot.send_message(call.from_user.id, f"Ваш кандидат - {c_name}. Вы уверены, "
                                                f"что хотите назначить собеседование в {time_date}?",
                             reply_markup=markup)
        elif "accept|" in call.data:
            data = call.data.split("|")
            time_date, c_name = data[1:]
            time_date = datetime.strptime(time_date, "%H:%M;%d.%m.%Y")
            time_date0 = time_date - timedelta(hours=1)
            time_date1 = time_date - timedelta(minutes=15)
            cands = read_candidates()
            add_time_date(time_date0.strftime("%H:%M;%d.%m.%Y"), c_name, call.from_user.username)
            add_time_date(time_date1.strftime("%H:%M;%d.%m.%Y"), c_name, call.from_user.username)
            r_name = read_nicknames()[read_candidates()[call.from_user.username][c_name]["r"]]
            bot.send_message(r_name, f"Заказчик {call.from_user.username} одобрил кандидата {c_name}")
            bot.send_message(call.from_user.id, "Собеседование назначено.\n"
                                                "Я напомню вам о нём за 1 час и за 15 минут.\n"
                                                "Ожидайте следующего кандидата.")
            del_file(cands[call.from_user.username][c_name]["f"])
            delete_from_candidates(call.from_user.username, c_name)
        elif "cancel|" in call.data:
            c_name = call.data.split("|")[-1]
            bot.send_message(call.from_user.id, "В таком случае, мы проведём процесс назначения собеседования "
                                                "заново.")
            call.data = "interview|" + c_name
            selector(call)
    except (TypeError, KeyError, ValueError):
        p_error(call)


# _____________________________________There_is_a_purchaser_interface_higher____________________________________________
@bot.message_handler(commands=["start"])
def rec_or_purch(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Рекрутер", callback_data="Рекрутер")
    btn2 = types.InlineKeyboardButton(text="Заказчик", callback_data="Заказчик")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Приветсвую вас. Вы рекрутер или заказчик?\n"
                                      "Выберите ответ на клавиатуре!",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["Рекрутер", "Заказчик"])
def defenition(call):
    markup = types.InlineKeyboardMarkup()
    if call.data == "Рекрутер":
        markup.add(types.InlineKeyboardButton("В меню!", callback_data="r_menu"))
        nickname_registration(call.from_user.username, call.from_user.id, type=0)
        bot.send_message(call.from_user.id, "Приветсвую тебя, рекрутер!\nГотов приступить к работе?",
                         reply_markup=markup)
    elif call.data == "Заказчик":
        create_list(call.from_user.username)
        markup.add(types.InlineKeyboardButton("В меню!", callback_data="p_menu"))
        nickname_registration(call.from_user.username, call.from_user.id, type=1)
        bot.send_message(call.from_user.id, "Приветсвую тебя, заказчик!\nГотов приступить к работе?",
                         reply_markup=markup)
# _____________________________________There_is_a_recruiter_interface_lower______________________________________________


@bot.callback_query_handler(func=lambda call: call.data == "r_menu")
def recr_menu(call):
    try:
        if read_connections()[call.from_user.username][0] == 0:
            msg = bot.send_message(call.from_user.id, "У тебя нет подключений к заказчикам.\n"
                                                      "Введите никнейм кого-нибудь из них без символа '@',\n"
                                                      "чтобы приступить к работе.",
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, connect_to1)
        else:
            connections = read_connections()[call.from_user.username]
            coming_text = (f"Текущий заказчик - @{connections[connections[0]]}.\n"
                           f"Доступны следующие варианты действий:")
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton(text="Добавить заказчика", callback_data="connection")
            btn2 = types.InlineKeyboardButton(text="Сменить заказчика", callback_data="change")
            btn3 = types.InlineKeyboardButton(text="Отключиться от...", callback_data="delete")
            btn4 = types.InlineKeyboardButton(text="Добавить кандидата", callback_data="candidate_reg")
            markup.add(btn1, btn2, btn3, btn4)
            bot.send_message(call.from_user.id, text=coming_text.format(call.from_user), reply_markup=markup)
    except (TypeError, KeyError, ValueError):
        r_error(call)
# _____________________________________Adding_a_new_connection__________________________________________________________


@bot.callback_query_handler(func=lambda call: call.data == "connection")
def connect_to0(call):
    msg = bot.send_message(call.from_user.id, "Введите никнейм нового заказчика без символа '@'.")
    bot.register_next_step_handler(msg, connect_to1)


def connect_to1(message):
    purchaser = message.text
    r_n = read_nicknames()
    if purchaser in r_n:
        add_connection(message.chat.username, purchaser)
        bot.send_message(r_n[purchaser], f"К Вам подключён рекрутер с нимком: @{message.chat.username}!")
        bot.send_message(message.chat.id, f"@{purchaser} подключён успешно. Возвращаю вас в меню.")
        recr_menu(message)
    elif purchaser not in r_n:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("В меню", callback_data="r_menu")
        btn2 = types.InlineKeyboardButton("Ввод повторно", callback_data="connection")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, f"Заказчик '@{purchaser}' не подключён,"
                                          f"так как не числится в базе.\n"
                                          f"Вы можете подождать, "
                                          f"пока он зарегистрируется, или попробовать изменить\n"
                                          f"введённый ранее никнейм.",
                                          reply_markup=markup)
# _____________________________________Changing_actual_connection_______________________________________________________


@bot.callback_query_handler(func=lambda call: call.data == "change")
def change0(call):
    try:
        markup = types.ReplyKeyboardMarkup()
        connections = read_connections()[call.from_user.username][1:]
        for i in connections:
            markup.add(types.KeyboardButton(text="@" + i))
        msg = bot.send_message(call.from_user.id, text="Выберите заказчика из этого списка:".format(call.from_user),
                               reply_markup=markup)
        bot.register_next_step_handler(msg, change1)
    except (TypeError, KeyError, ValueError):
        r_error(call)


def change1(message):
    try:
        change_connection(message.from_user.username, message.text[1:])
        bot.send_message(message.from_user.id, "Успешно!", reply_markup=types.ReplyKeyboardRemove())
        recr_menu(message)
    except (TypeError, KeyError, ValueError):
        r_error(message)
# _____________________________________Deleting_a_connection____________________________________________________________


@bot.callback_query_handler(func=lambda call: call.data == "delete")
def delete0(call):
    try:
        markup = types.ReplyKeyboardMarkup()
        connections = read_connections()[call.from_user.username][1:]
        for i in connections:
            markup.add(types.KeyboardButton(text="@" + i))
        msg = bot.send_message(call.from_user.id, text="Выберите заказчика для отключения "
                                                       "из этого списка:".format(call.from_user),
                               reply_markup=markup)
        bot.register_next_step_handler(msg, delete1)
    except (TypeError, KeyError, ValueError):
        r_error(call)


def delete1(message):
    try:
        purchaser = message.text[1:]
        connections = read_connections()[message.chat.username]
        if len(connections) == 2:
            bot.send_message(message.chat.id, "Нельзя отключаться от последнего заказчика. Открываю меню.")
            recr_menu(message)
        elif purchaser not in connections:
            bot.send_message(message.chat.id, "Неверный никнейм заказчика. Возвращаю Вас в меню.")
            recr_menu(message)
        else:
            delete_connection(message.chat.username, purchaser)
            bot.send_message(message.chat.id, "Успешно. Окрываю меню, где Вы увидите текущего заказчика.")
            recr_menu(message)
    except (TypeError, KeyError, ValueError):
        r_error(message)
# _____________________________________Adding_a_candidate_______________________________________________________________


@bot.callback_query_handler(func=lambda call: call.data == "candidate_reg")
def candidate_regisrtation(call):
    bot.send_message(call.from_user.id, "Сначала пришлите PDF-файл с резюме кандидата.",
                     reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=["document"])
def set_file(message_doc):
    file_info = bot.get_file(message_doc.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    msg = bot.send_message(message_doc.chat.id, "Теперь напишите ФИО кандидата через пробел.")
    bot.register_next_step_handler(msg, set_name, downloaded_file)


def set_name(message, file):
    msg = bot.send_message(message.from_user.id, "Имя получено. Теперь мне нужна ссылка на его резюме.")
    bot.register_next_step_handler(msg, set_link_and_final_registration, message.text, file)


def set_link_and_final_registration(message, name, summary):
    try:
        src = f"{path}/{name}.pdf"
        with open(src, "wb") as file:
            file.write(summary)
        candidate = Candidate(name, message.text, src, None, message.from_user.username)
        coming_text = "Вот как будет выглядеть описание кандидата у заказчика:"
        bot.send_message(message.chat.id, coming_text)
        info = candidate.get_info()
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Ссылка", url=info["l"]))
        bot.send_message(message.chat.id, f"Кандидат: {info["n"]}", reply_markup=markup)
        file = open(info["f"], "rb")
        bot.send_document(message.chat.id, file)
        coming_text = "Готовы ли Вы отправить этого кандидата заказчику?"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text="Да")
        btn2 = types.KeyboardButton(text="Нет")
        markup.add(btn1, btn2)
        msg = bot.send_message(message.chat.id, text=coming_text.format(message.from_user), reply_markup=markup)
        bot.register_next_step_handler(msg, send_candidate, candidate)
    except (TypeError, KeyError, ValueError, telebot.apihelper.ApiTelegramException, FileNotFoundError):
        r_error(message)


def send_candidate(message, candidate):
    try:
        if message.text == "Да":
            connections = read_connections()[message.from_user.username]
            p_nick = connections[connections[0]]
            info = candidate.get_info()
            p_id = read_nicknames()[p_nick]
            add_to_candidates(p_nick, info)
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Ссылка "
                                                                                      "на резюме.", url=info["l"]))
            bot.send_message(p_id, f"Вам прислан новый кандидат: {info["n"]}.", reply_markup=markup)
            file = open(info["f"], "rb")
            bot.send_document(p_id, file)
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Отказать", callback_data="refuse|"+info["n"])
            btn2 = types.InlineKeyboardButton(text="Собеседовать", callback_data="interview|"+info["n"])
            markup.add(btn1, btn2)
            bot.send_message(p_id, "Отказать ему, или назначить собеседовние?",
                             reply_markup=markup)
            bot.send_message(message.chat.id, "Кандидат успешно отправлен заказчику! Открываю меню.",
                             reply_markup=types.ReplyKeyboardRemove())
            recr_menu(message)
        else:
            bot.send_message(message.chat.id, "В таком случае, повторим всю операцию заново.",
                             reply_markup=types.ReplyKeyboardRemove())
            del_file(candidate.get_info()["f"])
            candidate_regisrtation(message)
    except (TypeError, KeyError, ValueError, telebot.apihelper.ApiTelegramException, FileNotFoundError):
        r_error(message)


@bot.message_handler(content_types=["text"])
def call_menu(message):
    if message.text.lower() == "В меню рекрутера":
        recr_menu(message)
    if message.text.lower() == "В меню заказчика":
        purch_menu(message)


bot.polling(none_stop=True)
