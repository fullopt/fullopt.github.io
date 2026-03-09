# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
import re

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from utils import setup_adaptive

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def brexit(_addon, _handle, word):
    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30105) + word)
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
    return False

def play(_handle, _addon, params):

    session = requests.Session()
    session.verify = False
    headers = {}
    headers.update(HEADERS)
    response = session.get("https://retromusic.cz/", headers=headers)
    content = response.text

    matches = re.search('file: "(.+)",', content)
    if bool(matches):
        playlist = matches.group(1)
    else:
        return brexit(_addon, _handle, 'do')

    li = xbmcgui.ListItem(path=playlist)
    setup_adaptive(li, None, 'hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
