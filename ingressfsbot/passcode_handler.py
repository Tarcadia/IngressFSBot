# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import shlex
import time

from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from threading import Lock

from . import passcode_data

from ._config import (
    CONF_PASSCODE_DATA_FILE_DEFAULT,
    CONF_PASSCODE_ADMIN_UID_DEFAULT,
    CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
    CONF_PASSCODE_SAVE_INTERVAL_DEFAULT,
    CONF_PASSCODE_BROADCAST_INTERVAL_DEFAULT,
)


MESSAGE_CMD_FAILED = """
Unrecognized command.
Use "/passcode help" for help.
"""

MESSAGE_HELP = """
/passcode help
/passcode report <index> <name> <media>
/passcode unknown
/passcode status
"""

MESSAGE_REPORT_RECIEVED = """
Report recieved.
Use "/passcode status" to view reports.
"""

MESSAGE_IMAGE_PATT_RECIEVED = """
Updated:
passcode image: {}
passcode patt: {}
"""

MESSAGE_TRUST_USER = """
Added a trusted user:
{}
Use "/passcode trusted" to view trusted users.
"""

MESSAGE_LIST_USER_REPORTS = """
Your reports:
====================
{}
========EOLS========
"""

MESSAGE_LIST_TRUSTED_REPORTS = """
All trusted reports:
====================
{}
========EOLS========
"""

MESSAGE_LIST_TRUSTED_USER = """
List trusted users:
====================
{}
========EOLS========
"""



def _echo_message(tg, message, text):
    tg.sendMessage({
        "chat_id": message["chat"]["id"],
        "reply_parameters": {"message_id": message["message_id"]},
        "text": text,
    })


def _with_data_access(method):
    @wraps(method)
    def wrapper(self, tg, message, *args, **kwargs):
        _ret = False
        with self.lock:
            _ret = method(self, tg, message, *args, **kwargs)
        return _ret
    return wrapper


def _with_data_update(method):
    @wraps(method)
    def wrapper(self, tg, message, *args, **kwargs):
        _ret = False
        with self.lock:
            _ret = method(self, tg, message, *args, **kwargs)
            now = time.time()
            if now > self.last_save_submit + self.save_interval:
                self.last_save_submit = now
                self.pool.submit(self.save)
            if now > self.last_broadcast_submit + self.broadcast_interval:
                self.last_broadcast_submit = now
                self.pool.submit(self.broadcast)
        return _ret
    return wrapper


def _with_admin(method):
    @wraps(method)
    def wrapper(self, tg, message, *args, **kwargs):
        uid = message["from"]["id"]
        if str(uid) != self.admin_uid:
            return self.command_failed(tg, message)
        return method(self, tg, message, *args, **kwargs)
    return wrapper


class PasscodeHandler:

    def __init__(
        self,
        pool: ThreadPoolExecutor,
        data_file = CONF_PASSCODE_DATA_FILE_DEFAULT,
        admin_uid = CONF_PASSCODE_ADMIN_UID_DEFAULT,
        portal_count = CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
        save_interval = CONF_PASSCODE_SAVE_INTERVAL_DEFAULT,
        broadcast_interval = CONF_PASSCODE_BROADCAST_INTERVAL_DEFAULT,
    ) -> None:

        self.lock = Lock()
        self.pool = pool
        self.passcode_data = passcode_data.PasscodeData()
        self.data_file = data_file
        self.admin_uid = admin_uid
        self.portal_count = portal_count

        if not os.path.exists(data_file):
            passcode_data.dump(data_file, self.passcode_data)
        
        self.passcode_data = passcode_data.load(data_file)

        self.save_interval = save_interval
        self.broadcast_interval = broadcast_interval
        self.last_save_submit = time.time()
        self.last_broadcast_submit = time.time()


    def save(self):
        time.sleep(self.save_interval)
        with self.lock:
            passcode_data.dump(self.data_file, self.passcode_data)


    def broadcast(self):
        time.sleep(self.broadcast_interval)
        with self.lock:
            pass


    def command_failed(self, tg, message, text = ""):
        self.pool.submit(_echo_message, tg, message, MESSAGE_CMD_FAILED + text)
        return True


    def _cmd_help(self, tg, message):
        self.pool.submit(_echo_message, tg, message, MESSAGE_HELP)
        return True


    @_with_data_update
    def _cmd_report(self, tg, message, index, name, media):
        user = message["from"]
        self.passcode_data.add_report(user, index, name, media)
        for user in self.passcode_data.get_trustable_users():
            self.passcode_data.add_trusted_user(user)
        self.pool.submit(_echo_message, tg, message, MESSAGE_REPORT_RECIEVED)
        return True


    # @_with_data_access
    # def _cmd_unknown(self, tg, message, chat, user, command):
    #     return
    

    @_with_data_access
    def _cmd_status(self, tg, message):
        user = message["from"]
        user_trusted = False
        user_reports = []
        trustable_reports = []
        trustable_users = []
        user_trusted = self.passcode_data.get_user_trusted(user)
        user_reports = self.passcode_data.get_user_reports(user)
        trustable_reports, trustable_users = self.passcode_data.get_trustable()
        for user in trustable_users:
            self.passcode_data.add_trusted_user(user)
        
        text_list_user_reports = "\n".join(
            f"{_index}\t{_name}\t{_media}"
            for _index, _name, _media in user_reports
        )
        
        text_list_trustable_reports = "\n".join(
            f"{_index}\t{_name}\t{_media}"
            for _index, _name, _media in trustable_reports
        )

        self.pool.submit(_echo_message, tg, message, MESSAGE_LIST_USER_REPORTS.format(text_list_user_reports))
        if user_trusted:
            self.pool.submit(_echo_message, tg, message, MESSAGE_LIST_TRUSTED_REPORTS.format(text_list_trustable_reports))
        
        return True


    @_with_admin
    @_with_data_update
    def _cmd_image(self, tg, message, url):
        self.passcode_data.set_passcode_url(url)
        self.pool.submit(_echo_message, tg, message, MESSAGE_IMAGE_PATT_RECIEVED.format(
            self.passcode_data.get_passcode_url(),
            self.passcode_data.get_passcode_patt(),
        ))
        return True


    @_with_admin
    @_with_data_update
    def _cmd_patt(self, tg, message, patt):
        self.passcode_data.set_passcode_patt(patt)
        self.pool.submit(_echo_message, tg, message, MESSAGE_IMAGE_PATT_RECIEVED.format(
            self.passcode_data.get_passcode_url(),
            self.passcode_data.get_passcode_patt(),
        ))
        return True


    @_with_admin
    @_with_data_update
    def _cmd_trust(self, tg, message, username):
        user = self.passcode_data.get_user_by_username(username)
        self.passcode_data.add_trusted_user(user)
        self.pool.submit(_echo_message, tg, message, MESSAGE_TRUST_USER.format(f"{user['id']} : @{user['username']}"))
        return True


    @_with_admin
    @_with_data_access
    def _cmd_trusted(self, tg, message):
        text_list_users = "\n".join(
            f"{user['id']} : @{user['username']}"
            for user in self.passcode_data.get_trusted_users()
        )
        self.pool.submit(_echo_message, tg, message, MESSAGE_LIST_TRUSTED_USER.format(text_list_users))
        return True


    def handle(self, tg, update):
        assert "message" in update and update["message"]
        assert "chat" in update["message"] and update["message"]["chat"]
        assert "from" in update["message"] and update["message"]["from"]
        assert "text" in update["message"] and update["message"]["text"]
        self.passcode_data.add_user(update["message"]["from"])
        command = shlex.split(update["message"]["text"])

        if len(command) < 1 or command[0] != "/passcode":
            return False

        if len(command) < 2:
            return self.command_failed(tg, update["message"])
        else:
            try:
                cmd_method = "_cmd_" + command[1]
                return getattr(self, cmd_method)(tg, update["message"], *command[2:])
            except Exception as e:
                return self.command_failed(tg, update["message"], text = str(e))

