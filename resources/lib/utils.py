import HTMLParser
import requests


def unescape(string):
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(string)


def urlencode(string):
    return requests.utils.quote(string.encode("utf8"))
