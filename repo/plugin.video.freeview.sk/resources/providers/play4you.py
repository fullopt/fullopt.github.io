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


BASE_URL = 'https://play4you.icu'
CHANNELS = {
    'm1':'1b6d437dbd',
    'm2':'1b0d237dbd',
    'dunaworld':'r3a5t0bf0s',
    'm5':'22a640b1de',
    'rtlklub':'8bb04c766c',
    'rtlii':'k65f4zh4e9',
    'tv2':'910c276218',
    'supertv2':'d33r4zg5z9',
    'filmplusz':'0977afac7c',
    
    'bbcnews':'rtz9vnsx8k',
    
    # 'foxnews':'8egpa53inu',
    # 'tvscomedy':'f4j7cvhulz',
    # 'tvsfamily':'k1830tnprs',
    # 'tvsmusic':'amnf5x08vy',
    'wildearth':'9ylw7deu0k',
    'babysharktv':'zbutpgh520'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36', 'Referer': BASE_URL}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO
    
    session = requests.Session()
    response = session.get(f"{BASE_URL}/e/{CHANNELS[channel]}", headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Krok 1: Nepodarilo sa získat stream: http={response.status_code}")
    
    match= re.search(r'load\.php\?a=[a-zA-Z0-9]+&b=[a-zA-Z0-9]+&c=', response.text)
    if not match:
        raise Exception("Krok 2: Nepodarilo sa získat stream")
    str_load = match.group(0)
    
    timestamp = int(time.time())
    response = requests.get(f"{BASE_URL}/{str_load}{timestamp}", headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Krok 3: Nepodarilo sa získat stream: http={response.status_code}")
    
    match = re.search(r'https?://[^\s\'"]*\.m3u8[^\s\'"]*', response.text)
    if not match:
        raise Exception("Krok 4: Nepodarilo sa získat stream")
    hls = match.group(0)
    
    li = xbmcgui.ListItem(path=hls+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)


