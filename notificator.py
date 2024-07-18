from telebot import *
import time
from datetime import datetime, timedelta
from custom_API import read_interviews, delete_interview, read_nicknames, delete_time


bot = TeleBot("7160462503:AAF2TsIXaehcOi-j_j60p4UN8yZ3_2tv-Vw")
BOT_URL = "https://t.me/Recruter_help_bot"


while True:
    time.sleep(1)
    sh = read_interviews()
    now = datetime.now()
    current_time = now.strftime("%H:%M;%d.%m.%Y")
    ch1 = now + timedelta(minutes=45)
    if current_time in sh:
        for i in sh[current_time]:
            i2 = i.split("||||")
            candidate, pid = i2[0], read_nicknames()[i2[1]]
            if ch1.strftime("%H:%M;%d.%m.%Y") in sh:
                bot.send_message(pid, "Вам назначено собеседование с кандидатом - "
                                      f"{candidate} через 1 час.")
            else:
                bot.send_message(pid, "Вам назначено собеседование с кандидатом - "
                                      f"{candidate} через 15 минут.")
            delete_interview(current_time, i)
        delete_time(current_time)
