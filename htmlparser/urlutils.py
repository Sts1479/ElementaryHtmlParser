# -*- coding: utf-8 -*-

import functools
import os
import textwrap
import uuid
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .config import MAX_LINE_LENGTH, IGNORE_ATTRS, IGNORE_TAGS



def coroutine(g):
    @functools.wraps(g)
    def inner(*args, **kwargs):
        gen = g(*args, **kwargs)
        next(gen)
        return gen
    return inner


"""
    URL может заканчиваться на слэш, а может заканчиваться на: .html, .php и т.д.,
    а может ни на то, ни на то.
    Если не можем дать название из урла, то даем просто какое-то уникальное и кладем в дирректорию
    с названием сайта.
 """

def url_to_filepath(url):
    now = datetime.now()
    dt_string = now.strftime('%Y%m%d%H%M%S')
    f = urlparse(url)
    file_path = '%s.txt' % uuid.uuid4()
    f_path = f.path.strip('/')
    if f_path:
        split_url_path = f_path.split('/')
        if split_url_path[-1].find('.') != -1:
            url_chank = split_url_path[-1].split('.')
            url_chank[-1] = 'txt'
            split_url_path[-1] = '_' + dt_string +'.'.join(url_chank)
        else:
            split_url_path[-1] += '_' + dt_string  + '.txt'
        file_path = '/'.join(split_url_path)
    return os.path.join(os.getcwd(), f.netloc, file_path)


@coroutine
def write_to_file(url):
    filename = url_to_filepath(url)
    print(filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        while True:
            text = yield
            f.write(textwrap.fill(text, width=MAX_LINE_LENGTH))
            f.write('\n\n')


def prepare_html(html):
    """
    "Готовит" html к последующему парсингу, вырезая ненужные тэги и тэги с ненужными атрибутами.

    """
    soup = BeautifulSoup(html, "html.parser")
    if IGNORE_TAGS:
        tags = soup.findAll(IGNORE_TAGS)
        [tag.extract() for tag in tags]
    for tag_attr_name, tag_attr_value in IGNORE_ATTRS:
        tags = soup.findAll(attrs={tag_attr_name: tag_attr_value})
        [tag.extract() for tag in tags]
    return str(soup)
