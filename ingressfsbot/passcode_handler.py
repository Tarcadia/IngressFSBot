# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import shlex
import time

from . import passcode_data
from threading import Lock

from ._config import (
    CONF_PASSCODE_DATA_FILE_DEFAULT,
    CONF_PASSCODE_ADMIN_UID_DEFAULT,
    CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
)


@dataclass
class PasscodeLog:
    image_url: str = ""
    user_reports: dict[str, dict] = field(default_factory=dict)
    user_info: dict[str, dict] = field(default_factory=dict)
    user_trusted: list = field(default_factory=list)

    def get_user_reports(self, uid):
        reports = set()
        for index in self.user_reports[uid]:
            entry = (
                index,
                self.user_reports[uid][index][-1]["name"],
                self.user_reports[uid][index][-1]["media"],
            )
            reports.add(entry)
        return list(reports)

    def get_trustable_reports(self):
        reports = set()
        trusted_reports = set()
        for uid in self.user_reports:
            for index in self.user_reports[uid]:
                entry = (
                    index,
                    self.user_reports[uid][index][-1]["name"],
                    self.user_reports[uid][index][-1]["media"],
                )
                if entry in reports:
                    trusted_reports.add(entry)
                reports.add(entry)
        return list(trusted_reports)
    
    def get_trustable_users(self):
        trusted_users = set()
        trusted_reports = self.get_trustable_reports()
        for uid in self.user_reports:
            user_reports = self.get_user_reports(uid)
            for entry in user_reports:
                if entry in trusted_reports:
                    trusted_users.add(uid)
        return list(trusted_users)


class PasscodeHandler:

    def __init__(
        self,
        data_file = CONF_PASSCODE_DATA_FILE_DEFAULT,
        admin_uid = CONF_PASSCODE_ADMIN_UID_DEFAULT,
        portal_count = CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
    ) -> None:

        self.passcode_data = passcode_data.PasscodeData()
        self.data_file = data_file
        self.admin_uid = admin_uid
        self.portal_count = portal_count
        self.lock = Lock()

        if not os.path.exists(data_file):
            passcode_data.dump(data_file, self.passcode_data)
        
        self.passcode_data = passcode_data.load(data_file)


    def help(self, tg, message, chat, user, command):
        help_text = """
/passcode help
/passcode report <index> <name> <media>
/passcode unknown
/passcode known
"""
        tg.sendMessage({
            "chat_id": chat["id"],
            "text": help_text,
            "reply_parameters": {"message_id": message["message_id"]}
        })
        return True


    def report(self, tg, message, chat, user, command):
        uid = str(user["id"])
        portal_index = command[2]
        portal_name = command[3]
        portal_media = command[4]
        report_trusted = False
        user_trusted = False
        with self.lock:
            self.passcode_data.user_info[uid] = user
            if not uid in self.passcode_data.user_reports:
                self.passcode_data.user_reports[uid] = {}
            if not portal_index in self.passcode_data.user_reports[uid]:
                self.passcode_data.user_reports[uid][portal_index] = []
            self.passcode_data.user_reports[uid][portal_index].append({
                "time": time.time(),
                "name": portal_name,
                "media": portal_media
            })
            trusted_reports = self.passcode_data.get_trustable_reports()
            trusted_users = self.passcode_data.get_trustable_users()
            for trusted_uid in trusted_users:
                if not trusted_uid in self.passcode_data.user_trusted:
                    self.passcode_data.user_trusted.append(trusted_uid)
            if (portal_index, portal_name, portal_media) in trusted_reports:
                report_trusted = True
            if uid in trusted_users:
                user_trusted = True
        text = """
Report recieved.
User /passcode known to view reports.
"""
        text += """
Your report is trusted.
""" if report_trusted else ""
        text += """
You are trusted.
""" if user_trusted else ""
        tg.sendMessage({
            "chat_id": chat["id"],
            "text": text,
            "reply_parameters": {"message_id": message["message_id"]}
        })
        with self.lock:
            passcode_data.dump(self.data_file, self.passcode_data)
        return True


    def unknown(self, tg, message, chat, user, command):
        return
    

    def known(self, tg, message, chat, user, command):
        uid = str(user["id"])
        user_reports = []
        trusted_reports = []
        trusted = False
        with self.lock:
            self.passcode_data.user_info[uid] = user
            if not uid in self.passcode_data.user_reports:
                self.passcode_data.user_reports[uid] = {}
            trusted = uid in self.passcode_data.user_trusted
            user_reports = self.passcode_data.get_user_reports(uid)
            if trusted:
                trusted_reports = self.passcode_data.get_trustable_reports()
        
        user_reports.sort()
        trusted_reports.sort()

        user_reports_text = "\n".join(
            f"{_index}\t{_name}\t{_media}"
            for _index, _name, _media in user_reports
        ) if user_reports else "No reports found."
        trusted_reports_text = "\n".join(
            f"{_index}\t{_name}\t{_media}"
            for _index, _name, _media in trusted_reports
        ) if trusted_reports else "No reports found."

        text = f"""
Your reports:
{user_reports_text}
"""
        text += f"""
======== TRUSTED ONLY ========
You are now trusted so providing joined trusted reports:
{trusted_reports_text}
""" if trusted else ""

        tg.sendMessage({
            "chat_id": chat["id"],
            "text": text,
            "reply_parameters": {"message_id": message["message_id"]}
        })
        
        return True
    

    def trust(self, tg, message, chat, user, command):
        uid = str(user["id"])
        if uid != self.admin_uid:
            tg.sendMessage({
                "chat_id": chat["id"],
                "text": "You are not authorized to do so.",
                "reply_parameters": {"message_id": message["message_id"]}
            })
            return
        
        uid_to_trust = command[2]
        user_to_trust = {}
        with self.lock:
            self.passcode_data.user_info[uid] = user
            if not uid in self.passcode_data.user_reports:
                self.passcode_data.user_reports[uid] = {}
            if not uid_to_trust in self.passcode_data.user_trusted:
                self.passcode_data.user_trusted.append(uid_to_trust)
            if uid_to_trust in self.passcode_data.user_info:
                user_to_trust = self.passcode_data.user_info[uid_to_trust]
        
        text = f"""
Added user {uid_to_trust} to the trusted.
"""
        text += f"""
Recognized user info:
{user_to_trust}
""" if user_to_trust else ""
        text += f"""
Currently trusted users:
{"\n".join(self.passcode_log.user_trusted)}
"""

        tg.sendMessage({
            "chat_id": chat["id"],
            "text": text,
            "reply_parameters": {"message_id": message["message_id"]}
        })
        with self.lock:
            passcode_data.dump(self.data_file, self.passcode_data)
        return True


    def failed_command(self, tg, message, chat, user, command):
        help_text = """
Unrecognized command, check for the following commands:
/passcode help
/passcode report <index> <name> <media>
/passcode unknown
/passcode known
"""
        tg.sendMessage({
            "chat_id": chat["id"],
            "text": help_text,
            "reply_parameters": {"message_id": message["message_id"]}
        })
        return True
    

    def handle(self, tg, update):
        if not "message" in update or not update["message"]:
            return
        if not "chat" in update["message"] or not update["message"]["chat"]:
            return
        if not "from" in update["message"] or not update["message"]["from"]:
            return
        if not "text" in update["message"] or not update["message"]["text"]:
            return
        
        message = update["message"]
        chat = update["message"]["chat"]
        user = update["message"]["from"]
        text = update["message"]["text"]
        command = shlex.split(text)

        if len(command) < 1:
            return
        
        if not command[0] == "/passcode":
            return
        
        if len(command) < 2:
            return self.failed_command(tg, message, chat, user, command)
        elif command[1] == "help":
            return self.help(tg, message, chat, user, command)
        elif command[1] == "report" and len(command) == 5:
            return self.report(tg, message, chat, user, command)
        elif command[1] == "unknown" and len(command) == 2:
            return self.unknown(tg, message, chat, user, command)
        elif command[1] == "known" and len(command) == 2:
            return self.known(tg, message, chat, user, command)
        elif command[1] == "trust" and len(command) == 3:
            return self.trust(tg, message, chat, user, command)
        else:
            return self.failed_command(tg, message, chat, user, command)

