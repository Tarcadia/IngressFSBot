# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import time
import json

from dataclasses import dataclass, field, asdict


def load(filename):
    with open(filename, "r") as fp:
        return PasscodeData(**json.load(fp))


def dump(filename, data):
    with open(filename, "w") as fp:
        json.dump(asdict(data), fp)



@dataclass
class PasscodeData:
    passcode_url:   str                 = ""
    passcode_patt:  str                 = ""
    user_reports:   dict[str, dict]     = field(default_factory=dict)
    user_trusted:   list                = field(default_factory=list)
    user_info:      dict[str, dict]     = field(default_factory=dict)

    min_correct:    int     = 3
    min_count:      int     = 3
    min_rate:       int     = 0.5


    def set_passcode_url(self, url):
        self.passcode_url = url


    def set_passcode_patt(self, patt):
        self.passcode_patt = patt


    def add_user(self, user):
        uid = str(user["id"])
        self.user_info[uid] = user


    def add_report(self, user, index, name, media):
        uid = str(user["id"])
        if not uid in self.user_reports:
            self.user_reports[uid] = {}
        if not index in self.user_reports[uid]:
            self.user_reports[uid][index] = []
        self.user_reports[uid][index].append({
            "time": time.time(),
            "name": name,
            "media": media
        })


    def add_trusted_user(self, user):
        uid = str(user["id"])
        if uid not in self.user_trusted:
            self.user_trusted.append(uid)


    def get_passcode_url(self):
        return self.passcode_url


    def get_passcode_patt(self):
        return self.passcode_patt


    def get_user_by_username(self, username):
        for uid in self.user_info:
            if self.user_info[uid]["username"] == username:
                return self.user_info[uid]


    def get_user_trusted(self, user):
        uid = str(user["id"])
        return uid in self.user_trusted


    def get_user_trustable(self, user):
        uid = str(user["id"])
        trustable_users = self.get_trustable_users()
        for user in trustable_users:
            if str(user["id"]) == uid:
                return True
        return False


    def get_user_reports(self, user):
        uid = str(user["id"])
        reports = set()
        for index in self.user_reports[uid]:
            entry = (
                index,
                self.user_reports[uid][index][-1]["name"],
                self.user_reports[uid][index][-1]["media"],
            )
            reports.add(entry)
        return sorted(list(reports))


    def get_trusted_users(self):
        return [self.user_info[uid] for uid in set(self.user_trusted)]


    def get_trustable(self):
        trustable_users = []
        users_stat = {}
        trustable_reports = self.get_trustable_reports()
        _trustable_reports = {_index: (_name, _media) for _index, _name, _media in trustable_reports}
        for uid in self.user_reports:
            users_stat[uid] = 0
            for index in self.user_reports[uid]:
                if index in _trustable_reports and _trustable_reports[index][1] == self.user_reports[uid][index][-1]["media"]:
                    users_stat[uid] += 1
            if users_stat[uid] > self.min_correct:
                trustable_users.append(self.user_info[uid])
        return trustable_reports, trustable_users


    def get_trustable_users(self):
        _, trustable_users = self.get_trustable()
        return trustable_users


    def get_trustable_reports(self):
        names = {}
        medias = {}
        indexes = set()
        for uid in self.user_reports:
            for index in self.user_reports[uid]:
                indexes.add(index)
                if not index in names:
                    names[index] = []
                if not index in medias:
                    medias[index] = []
                names[index].append(self.user_reports[uid][index][-1]["name"])
                medias[index].append(self.user_reports[uid][index][-1]["media"])
        trustable_names = {}
        trustable_medias = {}
        trustable_reports = set()
        for index in indexes:
            for name in set(names[index]):
                _count = names[index].count(name)
                if (not index in trustable_names and _count >= self.min_count and _count >= self.min_rate * len(names[index])):
                    trustable_names[index] = name
                elif (index in trustable_names and _count > names[index].count(trustable_names[index])):
                    trustable_names[index] = name
            for media in set(medias[index]):
                _count = medias[index].count(media)
                if (not index in trustable_medias and _count >= self.min_count and _count > self.min_rate * len(medias[index])):
                    trustable_medias[index] = media
                elif (index in trustable_medias and _count > medias[index].count(trustable_medias[index])):
                    trustable_medias[index] = media
            _name = trustable_names[index] if index in trustable_names else ""
            _media = trustable_medias[index] if index in trustable_medias else ""
            if _name or _media:
                _report = (index, _name, _media)
                trustable_reports.add(_report)
        return list(trustable_reports)

