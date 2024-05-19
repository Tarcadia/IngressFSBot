# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import shlex
import json

from dataclasses import dataclass, field, asdict
from ._config import (
    CONF_PASSCODE_LOG_FILE_DEFAULT,
    CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
)


@dataclass
class PasscodeLog:
    image_url: str = ""
    user_reports: dict[str, list] = field(default_factory=dict)
    user_info: dict[str, dict] = field(default_factory=dict)
    user_trusted: list = field(default_factory=list)


class PasscodeHandler:

    def __init__(
        self,
        log_file = CONF_PASSCODE_LOG_FILE_DEFAULT,
        portal_count = CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
    ) -> None:

        self.passcode_log = PasscodeLog()
        self.log_file = log_file
        self.portal_count = portal_count

        if not os.path.exists(log_file):
            with open(log_file, "w") as fp:
                json.dump(asdict(self.passcode_log), fp)
        
        with open(log_file, "r") as fp:
            self.passcode_log = PasscodeLog(**json.load(fp))

    def help(self, tg, message, chat, user, command):
        tg.sendMessage({
            "chat_id": chat["id"],
            "text": "???",
            "reply_parameters": {"message_id": message["message_id"]}
        })

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

        if not command[0] == "/passcode":
            return
        
        if command[1] == "help":
            self.help(tg, message, chat, user, command)


