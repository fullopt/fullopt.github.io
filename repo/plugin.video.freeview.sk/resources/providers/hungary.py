# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 19.12.2021
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import requests.cookies
import time
import re
import xbmcgui
import xbmcplugin

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


CHANNELS = {
    'm1':'http://play4you.icu/e/1b6d437dbd',
    'm2':'http://play4you.icu/e/1b0d237dbd',
    'm4sport':'http://play4you.icu/e/r3a5t0bf0s',
    'm5':'http://play4you.icu/e/22a640b1de',
    'rtlklub':'http://play4you.icu/e/8bb04c766c',
    'rtlii':'http://play4you.icu/e/k65f4zh4e9',
    'tv2':'http://play4you.icu/e/910c276218',
    'supertv2':'http://play4you.icu/e/d33r4zg5z9',
    'filmplusz':'http://play4you.icu/e/0977afac7c'
}

ORIGIN = 'https://play4you.icu/'
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36', 'Referer': ORIGIN}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO
    
    session = requests.Session()
    headers = {}
    headers.update(HEADERS)
    response = session.get(CHANNELS[channel], headers=headers)
    
    match_load = re.search(r'load\.php\?a=[a-zA-Z0-9]+&b=[a-zA-Z0-9]+&c=', response.text)
    str_load = match_load.group(0)
    
    timestamp = int(time.time())
    response2 = requests.get(f"{ORIGIN}/{str_load}{timestamp}", headers=headers)
    match_playlist = re.search(r'https://[^\s\'"]*playlist\.m3u8[^\s\'"]*', response2.text)
    hls = match_playlist.group(0)
    
    li = xbmcgui.ListItem(path=hls+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)


