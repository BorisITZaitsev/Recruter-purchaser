import os
import json


class Candidate:
    """This class contains the description of a candidate"""
    def __init__(self, name, link, file, interview, recruter):
        self.name = name
        self.link = link
        self.file = file
        self.interview = interview
        self.recruter = recruter

    def get_info(self):
        return {"n": self.name, "l": self.link, "f": self.file, "i": self.interview, "r": self.recruter}


path = os.getcwd().replace('\\', "/")


def nickname_registration(u_nick, u_id, type=0):
    data = read_nicknames()
    if u_nick not in data:
        data[u_nick] = str(u_id)
        write_nicknames(data)
    if type == 0:
        data = read_connections()
        data[u_nick] = [0]
        write_connections(data)


def add_connection(r_nick, p_nick):
    data = read_connections()
    if p_nick not in data[r_nick]:
        data[r_nick][0] += 1
        data[r_nick].append(p_nick)
        write_connections(data)


def change_connection(r_nick, p_nick):
    data = read_connections()
    data[r_nick][0] = data[r_nick].index(p_nick)
    write_connections(data)


def delete_connection(r_nick, p_nick):
    data = read_connections()
    data[r_nick].remove(p_nick)
    data[r_nick][0] -= 1
    write_connections(data)


def create_list(p_nick):
    data = read_candidates()
    if p_nick not in data:
        data[p_nick] = {}
        write_candidates(data)


def add_to_candidates(p_nick, candidate):
    data = read_candidates()
    data[p_nick][candidate["n"]] = candidate
    write_candidates(data)


def delete_from_candidates(p_nick, c_name):
    data = read_candidates()
    del data[p_nick][c_name]
    write_candidates(data)


def add_time_date(time_date, c_nick, p_nick):
    data = read_interviews()
    interview = c_nick + "||||" + p_nick
    if time_date not in data:
        data[time_date] = [interview]
    else:
        data[time_date].append(interview)
    write_interviews(data)


def delete_interview(time_date, interview):
    data = read_interviews()
    if time_date in data:
        data[time_date].remove(interview)
        write_interviews(data)


def delete_time(time_date):
    data = read_interviews()
    if time_date in data and data[time_date] == []:
        del data[time_date]
        write_interviews(data)


# _____________________________________Here_are_the_file-opener-functions_______________________________________________
def read_nicknames():
    with open("nickid.json", "r", encoding="utf-8") as file:
        return json.load(file)


def write_nicknames(data):
    with open("nickid.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def read_connections():
    with open("connections.json", "r", encoding="utf-8") as file:
        return json.load(file)


def write_connections(data):
    with open("connections.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def read_candidates():
    with open("candidates.json", "r", encoding="utf-8") as file:
        return json.load(file)


def write_candidates(data):
    with open("candidates.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def read_interviews():
    with open("interviews.json", "r", encoding="utf-8") as file:
        return json.load(file)


def write_interviews(data):
    with open("interviews.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def del_file(src):
    os.remove(src)
