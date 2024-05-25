# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import configparser
import os

from functools import wraps

from . import __version__


CONFIG_FILE = "./conf.d"

CONF_POOL = "pool"
CONF_POOL_MAX_WORKERS = "max-workers"
CONF_POOL_THREAD_PREFIX = "thread-prefix"

CONF_POOL_MAX_WORKERS_DEFAULT = 32
CONF_POOL_THREAD_PREFIX_DEFAULT = "Worker #"

CONF_TELEGRAM = "telegram"
CONF_TELEGRAM_TOKEN = "token"
CONF_TELEGRAM_URL_BOT = "url-bot"
CONF_TELEGRAM_URL_FILE = "url-file"
CONF_TELEGRAM_USER_AGENT = "user-agent"
CONF_TELEGRAM_TIMEOUT = "timeout"

CONF_TELEGRAM_URL_BOT_DEFAULT = "https://api.telegram.org/bot"
CONF_TELEGRAM_URL_FILE_DEFAULT = "https://api.telegram.org/file/bot"
CONF_TELEGRAM_USER_AGENT_DEFAULT = f"IngressFSBot/{__version__}"

CONF_PASSCODE = "passcode"
CONF_PASSCODE_DATA_FILE = "log-file"
CONF_PASSCODE_ADMIN_UID = "admin-uid"
CONF_PASSCODE_PROTAL_COUNT = "portal-count"
CONF_PASSCODE_SAVE_INTERVAL = "save-interval"
CONF_PASSCODE_BROADCAST_INTERVAL = "broadcast-interval"

CONF_PASSCODE_DATA_FILE_DEFAULT = "passcode_log.json"
CONF_PASSCODE_ADMIN_UID_DEFAULT = ""
CONF_PASSCODE_PROTAL_COUNT_DEFAULT = 11
CONF_PASSCODE_SAVE_INTERVAL_DEFAULT = 10
CONF_PASSCODE_BROADCAST_INTERVAL_DEFAULT = 60

CONF_LOGGING = "logging"
CONF_LOGGING_VERBOSE_LEVEL = "verbose-level"
CONF_LOGGING_FILE_LEVEL = "file-level"
CONF_LOGGING_FILE_PATH = "file-path"
CONF_LOGGING_HTTPX_LEVEL = "httpx-level"

CONF_LOGGING_VERBOSE_LEVEL_DEFAULT = logging.WARNING
CONF_LOGGING_HTTPX_LEVEL_DEFAULT = logging.WARNING

_config = configparser.ConfigParser()
_config.read_dict({
    CONF_POOL: {
        CONF_POOL_MAX_WORKERS: CONF_POOL_MAX_WORKERS_DEFAULT,
        CONF_POOL_THREAD_PREFIX: CONF_POOL_THREAD_PREFIX_DEFAULT,
    },
    CONF_TELEGRAM: {
        CONF_TELEGRAM_URL_BOT: CONF_TELEGRAM_URL_BOT_DEFAULT,
        CONF_TELEGRAM_URL_FILE: CONF_TELEGRAM_URL_FILE_DEFAULT,
        CONF_TELEGRAM_USER_AGENT: CONF_TELEGRAM_USER_AGENT_DEFAULT,
    },
    CONF_PASSCODE: {
        CONF_PASSCODE_DATA_FILE: CONF_PASSCODE_DATA_FILE_DEFAULT,
        CONF_PASSCODE_PROTAL_COUNT: CONF_PASSCODE_PROTAL_COUNT_DEFAULT,
        CONF_PASSCODE_SAVE_INTERVAL: CONF_PASSCODE_SAVE_INTERVAL_DEFAULT,
        CONF_PASSCODE_BROADCAST_INTERVAL: CONF_PASSCODE_BROADCAST_INTERVAL_DEFAULT,
    },
    CONF_LOGGING: {
        CONF_LOGGING_VERBOSE_LEVEL: CONF_LOGGING_VERBOSE_LEVEL_DEFAULT,
        CONF_LOGGING_HTTPX_LEVEL: CONF_LOGGING_HTTPX_LEVEL_DEFAULT,
    },
})


def get_config():
    return _config


@wraps(_config.has_section)
def has_section(*args, **kwargs):
    return _config.has_section(*args, **kwargs)


@wraps(_config.has_option)
def has_option(*args, **kwargs):
    return _config.has_option(*args, **kwargs)


@wraps(_config.set)
def set(*args, **kwargs):
    return _config.set(*args, **kwargs)


@wraps(_config.get)
def get(*args, **kwargs):
    return _config.get(*args, **kwargs)


@wraps(_config.getint)
def getint(*args, **kwargs):
    return _config.getint(*args, **kwargs)


@wraps(_config.getfloat)
def getfloat(*args, **kwargs):
    return _config.getfloat(*args, **kwargs)


@wraps(_config.getboolean)
def getboolean(*args, **kwargs):
    return _config.getboolean(*args, **kwargs)


def read_config(config_file = CONFIG_FILE):
    if os.path.isdir(config_file):
        for _, _, _subfiles in os.walk(config_file):
            _read_files = _config.read(_subfiles)
            for _filename in _read_files:
                logger.info(f"Loading config from {_filename}")
    else:
        _read_files = _config.read(config_file)
        for _filename in _read_files:
            logger.info(f"Loading config from {_filename}")

