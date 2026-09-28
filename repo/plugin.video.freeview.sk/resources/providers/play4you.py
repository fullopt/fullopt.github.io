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
    
from utils import setup_adaptive

# CHARCK THIS: https://livestreamlinks.net/onlinetv
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

    'babysharktv':'zjfc0unr8dki'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36', 'Referer': BASE_URL}

def play(_handle, _addon, params):
    channel = params.get('channel')
    if not channel or channel not in CHANNELS:
        raise #TODO
    
    session = requests.Session()
    
    # First request: Embed page
    response = session.get(f"{BASE_URL}/e/{CHANNELS[channel]}", headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"{_addon.getLocalizedString(30400)} (1): http={response.status_code}")
    
    # Extract data-load-url attribute
    match = re.search(r'data-load-url=["\']([^"\']+)["\']', response.text)
    if not match:
        raise Exception("Missing data-load-url attribute")
    str_load = match.group(1).replace('&amp;', '&').lstrip('/')
    
    sep = '&' if '?' in str_load else '?'
    timestamp = int(time.time() * 1000)
    
    # Second request: Fetch stream payload (using session)
    payload_url = f"{BASE_URL}/{str_load}{sep}c={timestamp}"
    response = session.get(payload_url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"{_addon.getLocalizedString(30400)} (3): http={response.status_code}")
    
    # Parse stream JSON
    data = response.json()
    if data.get("ok") is True:
        hls = data.get("config", {}).get("churl")
        if not hls:
            raise Exception(f"{_addon.getLocalizedString(30400)} (4):\nNo HLS")
    else:
        raise Exception(f"{_addon.getLocalizedString(30400)} (4):\nAPI response is FALSE")
    
    # Pass stream URL with headers to Kodi
    li = xbmcgui.ListItem(path=hls + '|' + urlencode(HEADERS))
    setup_adaptive(li, None, 'hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
