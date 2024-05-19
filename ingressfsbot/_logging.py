# -*- coding=utf-8 -*-


import logging
import logging.handlers

import os

from functools import wraps


LOG_FILE = "ingressfsbot.log"


_logger = logging.getLogger()
_logger.setLevel(logging.NOTSET)

_hdlr_file = logging.handlers.TimedRotatingFileHandler(LOG_FILE)
_hdlr_file.setFormatter(logging.Formatter(
    fmt="%(asctime)s [%(levelname)s][%(name)s] %(message)s",
    datefmt="%Y-%m-%d-%H:%M:%S",
))
_hdlr_file.setLevel(logging.NOTSET)

_hdlr_stream = logging.StreamHandler()
_hdlr_stream.setFormatter(logging.Formatter(
    fmt="\033[0m%(asctime)s \033[1;34m[%(levelname)s]\033[0;33m[%(name)s]\033[0m >> %(message)s",
    datefmt="%H:%M",
))

_logger.addHandler(_hdlr_file)
_logger.addHandler(_hdlr_stream)


@wraps(_hdlr_stream.setLevel)
def setVerboseLevel(level):
    _hdlr_stream.setLevel(level=level)


@wraps(_hdlr_file.setLevel)
def setFileLevel(level):
    _hdlr_file.setLevel(level=level)


def setFileName(filename):
    _hdlr_file.baseFilename = os.path.abspath(filename)

