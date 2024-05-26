# -*- coding=utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import io
import string
import time
import json

import httpx

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def generate_passcode_string(patt, reports):
    patt_letters = []
    patt_numbers = []
    patt_keywords = []
    for _index, _name, _media in reports:
        if _media in string.ascii_letters:
            patt_letters.append(_media)
        elif _media in string.digits:
            patt_numbers.append(_media)
        else:
            patt_keywords.append(_media)
    patt_list = list(patt)
    for _media in patt_letters:
        if "@" in patt_list:
            patt_list[patt_list.index("@")] = _media
    for _media in patt_numbers:
        if "#" in patt_list:
            patt_list[patt_list.index("#")] = _media
    for _media in patt_keywords:
        if "$" in patt_list:
            patt_list[patt_list.index("$")] = _media
    return "".join(patt_list)


def generate_passcode_image(url, reports, file_image_dump, file_image_dump_format, x_offset=640, y_offset=145, y_height=300):
    with Image.open(io.BytesIO(httpx.get(url).content)) as im:
        font = ImageFont.truetype("simhei", size=y_height * 0.6)
        draw = ImageDraw.Draw(im)
        im_io = io.BytesIO()
        for _index, _name, _media in reports:
            if len(_name) > 10:
                _name = _name[:8] + "..."
            text = f"{_name} : {_media}"
            x = x_offset
            y = y_offset + y_height * (_index - 1 + 0.2)
            draw.text((x, y), text=text, fill=(255, 0, 0), font=font)
            im.save(im_io, format=file_image_dump_format)
            im.save(file_image_dump)
        return im_io.read()

