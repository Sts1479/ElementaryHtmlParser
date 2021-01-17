# -*- coding: utf-8 -*-

import requests

from html.parser import HTMLParser

from .config import ALLOWED_TAGS, TAG_BEGIN_SYMBOLS, TAG_END_SYMBOLS, POSTFIX_ATTR
from .urlutils import write_to_file, prepare_html

class ElementaryHTMLParser(HTMLParser):
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.current_tag = None
        self.print_postfix = None
        self.current_text = ''
        self.write_to_file = write_to_file(self.url)

    
    def try_get_page_content(self):
        try:
            r = requests.get(self.url)
        except Exception:
            print('No response from server!')
            return -1
        return prepare_html(r.text)

    def handle_starttag(self, tag, attrs):
        if tag in ALLOWED_TAGS:
            self.current_text += TAG_BEGIN_SYMBOLS.get(tag, '')
            self.current_tag = tag
        else:
            if self.current_tag:
                self.current_text += TAG_BEGIN_SYMBOLS.get(tag, '')
                if tag in POSTFIX_ATTR:
                    attr = POSTFIX_ATTR[tag]
                    attrs = dict(attrs)
                    if attr in attrs:
                        self.print_postfix = attrs[attr]

    def parse(self):
        prepare_html = self.try_get_page_content()
        if prepare_html != -1:
            super().feed(prepare_html)
        else: 
           print('Content not received')
           self.write_to_file.send('No content or invalid url')

    def handle_endtag(self, tag):
        if tag in ALLOWED_TAGS:
            self.current_tag = None
            self.current_text += TAG_END_SYMBOLS.get(tag, '')
            self.write_to_file.send(self.current_text)
            self.current_text = ''
        else:
            self.current_text += TAG_END_SYMBOLS.get(tag, '')

    def handle_data(self, data):
        if self.current_tag:
            self.current_text += data
            if self.print_postfix:
                self.current_text += ' [' + self.print_postfix + ']'
                self.print_postfix = None

    def close(self):
        self.write_to_file.close()
        super().close()

