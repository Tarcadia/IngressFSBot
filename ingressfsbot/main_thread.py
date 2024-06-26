# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import time

from concurrent.futures import ThreadPoolExecutor
from httpx._config import Timeout

from . import _config
from .telegram import Telegram
from .passcode_handler import PasscodeHandler
from ._config import (
    CONF_POOL,
    CONF_POOL_MAX_WORKERS,
    CONF_POOL_THREAD_PREFIX,
    CONF_TELEGRAM,
    CONF_TELEGRAM_TOKEN,
    CONF_TELEGRAM_URL_BOT,
    CONF_TELEGRAM_URL_FILE,
    CONF_TELEGRAM_USER_AGENT,
    CONF_TELEGRAM_TIMEOUT,
    CONF_PASSCODE,
    CONF_PASSCODE_DATA_FILE,
    CONF_PASSCODE_IMAGE_FILE,
    CONF_PASSCODE_IMAGE_FORMAT,
    CONF_PASSCODE_ADMIN_UID,
    CONF_PASSCODE_PROTAL_COUNT,
    CONF_PASSCODE_DUMP_INTERVAL,
    CONF_PASSCODE_BROADCAST_INTERVAL,
)


POLL_INTERVAL = 5


def main():

    pool_args = {}
    if _config.has_option(CONF_POOL, CONF_POOL_MAX_WORKERS):
        pool_args["max_workers"] = _config.getint(CONF_POOL, CONF_POOL_MAX_WORKERS)
    if _config.has_option(CONF_POOL, CONF_POOL_THREAD_PREFIX):
        pool_args["thread_name_prefix"] = _config.get(CONF_POOL, CONF_POOL_THREAD_PREFIX)
    pool = ThreadPoolExecutor(**pool_args)


    telegram_args = {}
    if _config.has_option(CONF_TELEGRAM, CONF_TELEGRAM_TOKEN):
        telegram_args["token"] = _config.get(CONF_TELEGRAM, CONF_TELEGRAM_TOKEN)
    if _config.has_option(CONF_TELEGRAM, CONF_TELEGRAM_URL_BOT):
        telegram_args["url_bot"] = _config.get(CONF_TELEGRAM, CONF_TELEGRAM_URL_BOT)
    if _config.has_option(CONF_TELEGRAM, CONF_TELEGRAM_URL_FILE):
        telegram_args["url_file"] = _config.get(CONF_TELEGRAM, CONF_TELEGRAM_URL_FILE)
    if _config.has_option(CONF_TELEGRAM, CONF_TELEGRAM_USER_AGENT):
        telegram_args["user_agent"] = _config.get(CONF_TELEGRAM, CONF_TELEGRAM_USER_AGENT)
    if _config.has_option(CONF_TELEGRAM, CONF_TELEGRAM_TIMEOUT):
        telegram_args["timeout"] = Timeout(timeout = _config.getfloat(CONF_TELEGRAM, CONF_TELEGRAM_TIMEOUT))
    tg = Telegram(**telegram_args)


    passcode_args = {
        "pool": pool,
        "broadcaster": tg,
    }
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_DATA_FILE):
        passcode_args["data_file"] = _config.get(CONF_PASSCODE, CONF_PASSCODE_DATA_FILE)
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_IMAGE_FILE):
        passcode_args["image_file"] = _config.get(CONF_PASSCODE, CONF_PASSCODE_IMAGE_FILE)
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_IMAGE_FORMAT):
        passcode_args["image_formate"] = _config.get(CONF_PASSCODE, CONF_PASSCODE_IMAGE_FORMAT)
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_ADMIN_UID):
        passcode_args["admin_uid"] = _config.get(CONF_PASSCODE, CONF_PASSCODE_ADMIN_UID)
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_PROTAL_COUNT):
        passcode_args["portal_count"] = _config.getint(CONF_PASSCODE, CONF_PASSCODE_PROTAL_COUNT)
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_DUMP_INTERVAL):
        passcode_args["dump_interval"] = _config.getint(CONF_PASSCODE, CONF_PASSCODE_DUMP_INTERVAL)
    if _config.has_option(CONF_PASSCODE, CONF_PASSCODE_BROADCAST_INTERVAL):
        passcode_args["broadcast_interval"] = _config.getint(CONF_PASSCODE, CONF_PASSCODE_BROADCAST_INTERVAL)
    passcode_handler = PasscodeHandler(**passcode_args)


    # handle_list = []
    # handle_list.append(passcode_handler.handle)


    me = tg.getMe()
    logger.info(f"Bot id={me['id']}")
    logger.info(f"Bot username={me['username']}")
    logger.info(f"Bot first_name={me['first_name']}")
    logger.debug(me)


    offset = 0
    loop_t0 = time.time()
    loop_acc_count = 0
    loop_con_count = 0
    while True:
        loop_acc_count += 1
        try:
            updates = tg.getUpdates({"offset": offset, "allowed_updates": ["message"]})
        except Exception as e:
            logger.error("Failed updating.")
            logger.debug(e, stack_info=True)
            continue
        try:
            logger.debug(updates)
            if updates:
                for update in updates:
                    offset = max(offset, update["update_id"] + 1)
                    pool.submit(passcode_handler.handle, tg, update)
        except Exception as e:
            logger.error("Failed processing update.")
            logger.debug(e, stack_info=True)
        
        loop_tx = loop_t0 + loop_con_count * POLL_INTERVAL
        logger.debug(f"Task Count: {pool._work_queue.qsize()}.")
        logger.debug(f"Loop Count: {loop_acc_count}.")
        logger.debug(f"Loop Cost: {time.time() - loop_tx}s.")
        logger.debug(f"Runing smoothly for {loop_con_count} loops.")
        if (t := loop_tx + POLL_INTERVAL - time.time()) > 0:
            loop_con_count += 1
            time.sleep(t)
        else:
            loop_con_count = 0
            loop_t0 = time.time()

