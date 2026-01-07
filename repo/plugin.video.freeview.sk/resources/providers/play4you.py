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


BASE_URL = 'https://play4you.livestreamlinks.net'
CHANNELS = {
    'm1':'a21b6d437dbd',
    'm2':'u71b0d237dbd',
    'dunaworld':'f2r3a5t0bf0s',
    'm5':'h722a640b1de',
    'rtlklub':'x38bb04c766c',
    'rtlii':'k1k65f4zh4e9',
    'tv2':'g5910c276218',
    'supertv2':'0dd33r4zg5z9',
    'filmplusz':'r40977afac7c',
    
    'bbcnews':'fkz3jbmhs7qr',
    
    'comedycentral':'fgro15rvvyjz',
    'comedytv':'7q1iy472cgbe',
    'natgeo':'96xr2tdn2pcs',
    'natgeowild':'6upbqu3pnoes',
    'babysharktv':'zjfc0unr8dki'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36', 'Referer': BASE_URL}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO
    
    session = requests.Session()
    response = session.get(f"{BASE_URL}/e/{CHANNELS[channel]}", headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"{_addon.getLocalizedString(30400)} (1): http={response.status_code}")
    
    match= re.search(r'load\.php\?a=[a-zA-Z0-9]+&b=[a-zA-Z0-9]+&c=', response.text)
    if not match:
        raise Exception(f"{_addon.getLocalizedString(30400)} (2):\nMissing LOAD")
    str_load = match.group(0)
    
    timestamp = int(time.time())
    response = requests.get(f"{BASE_URL}/{str_load}{timestamp}", headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"{_addon.getLocalizedString(30400)} (3): http={response.status_code}")
    
    match = re.search(r'https?://[^\s\'"]*\.m3u8[^\s\'"]*', response.text)
    if not match:
        match = re.search(r'<div\s+class="info".*?>.*?<p>(.*?)</p>.*?</div>', response.text, re.S)
        if not match:
            raise Exception(f"{_addon.getLocalizedString(30400)} (4):\nNo info")
        else:
            raise Exception(f"{_addon.getLocalizedString(30400)} (4):\n{match.group(1).strip()}")
    hls = match.group(0)
    
    li = xbmcgui.ListItem(path=hls+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)


