# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import httpx

from functools import wraps
from typing import Any

from httpx._config import DEFAULT_TIMEOUT_CONFIG

from ._config import (
    CONF_TELEGRAM_URL_BOT_DEFAULT,
    CONF_TELEGRAM_URL_FILE_DEFAULT,
    CONF_TELEGRAM_USER_AGENT_DEFAULT,
)


class Telegram:

    def __init__(
        self,
        token,
        url_bot = CONF_TELEGRAM_URL_BOT_DEFAULT,
        url_file = CONF_TELEGRAM_URL_FILE_DEFAULT,
        user_agent = CONF_TELEGRAM_USER_AGENT_DEFAULT,
        timeout = DEFAULT_TIMEOUT_CONFIG,
    ) -> None:
        self.token = token
        self.url_bot = url_bot
        self.url_file = url_file
        self.user_agent = user_agent
        self.timeout = timeout


    def __getattr__(self, __name: str) -> Any:
        @wraps(self.querymethod)
        def wrapper(obj: dict | None = None):
            return self.query(__name, obj=obj)
        return wrapper


    def querymethod(self, obj: dict | None = None):
        pass


    def query(self, method, obj=None):
        url = self.url_bot + self.token + f"/{method}"
        headers = {"user-agent": self.user_agent}
        resp = httpx.post(url=url, headers=headers, json=obj, timeout=self.timeout)
        obj = resp.json()
        if not obj or not "ok" in obj or not obj["ok"]:
            return
        if not "result" in obj or not obj["result"]:
            return
        return obj["result"]


