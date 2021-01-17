# -*- coding: utf-8 -*-

import argparse

from .content_parser import ElementaryHTMLParser


parser = argparse.ArgumentParser()
parser.add_argument('url')
url = parser.parse_args().url
html_parser = ElementaryHTMLParser(url)
html_parser.parse()
html_parser.close()
