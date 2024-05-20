#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from . import _logging
import logging
logger = logging.getLogger(__package__)

import click

from . import _config
from . import __url__
from . import __version__

from .main_thread import main
from ._config import (
    CONF_TELEGRAM,
    CONF_TELEGRAM_TOKEN,
    CONF_PASSCODE,
    CONF_PASSCODE_ADMIN_UID,
    CONF_LOGGING,
    CONF_LOGGING_VERBOSE_LEVEL,
    CONF_LOGGING_FILE_LEVEL,
    CONF_LOGGING_FILE_PATH,
    CONF_LOGGING_HTTPX_LEVEL,
)


@click.command()
@click.option("--config", "-c",     type=click.Path(exists=True))
@click.option("--token", "-t",      type=click.STRING)
@click.option("--admin", "-a",      type=click.STRING)
@click.option("--logfile",          type=click.Path(dir_okay=False))
@click.option("--verbose", "-v",    type=click.INT, count=True)
def cli(
    config=None,
    token=None,
    admin=None,
    logfile=None,
    verbose=0,
):
    loglevel = _config.getint(CONF_LOGGING, CONF_LOGGING_VERBOSE_LEVEL) - (verbose * 10)
    _logging.setVerboseLevel(loglevel)
    logging.info(f"Running {__package__}...")
    logging.info(f"Version {__version__}.")
    logging.info(f"Check {__url__} for more info.")

    if not config is None:
        _config.read_config(config)
    if not token is None:
        _config.set(CONF_TELEGRAM, CONF_TELEGRAM_TOKEN, token)
    if not admin is None:
        _config.set(CONF_PASSCODE, CONF_PASSCODE_ADMIN_UID, admin)
    if not logfile is None:
        _config.set(CONF_LOGGING, CONF_LOGGING_FILE_PATH, logfile)
    
    loglevel = _config.getint(CONF_LOGGING, CONF_LOGGING_VERBOSE_LEVEL) - (verbose * 10)
    _logging.setVerboseLevel(loglevel)
    if _config.has_option(CONF_LOGGING, CONF_LOGGING_FILE_LEVEL):
        _logging.setFileLevel(_config.get(CONF_LOGGING, CONF_LOGGING_FILE_LEVEL))
    if _config.has_option(CONF_LOGGING, CONF_LOGGING_FILE_PATH):
        _logging.setFileName(_config.get(CONF_LOGGING, CONF_LOGGING_FILE_PATH))
    if _config.has_option(CONF_LOGGING, CONF_LOGGING_HTTPX_LEVEL):
        httpx_log_level=_config.getint(CONF_LOGGING, CONF_LOGGING_HTTPX_LEVEL)
        logging.getLogger("httpx").setLevel(httpx_log_level)
        logging.getLogger("httpcore").setLevel(httpx_log_level)

    main()


if __name__ == "__main__":
    cli()

