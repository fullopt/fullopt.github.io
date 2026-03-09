# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests
import datetime

from dateutil.parser import parse
from dateutil.tz import tzutc, tzlocal

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from utils import setup_adaptive

CHANNELS = {
    'jednotka':1,
    'dvojka':2,
    '24':3,
    'online':4,
    'nrsr':5,
    'rtvs':6,
    'sport':15
}

API_INIT = "https://www.rtvs.sk/televizia/tv"
API = "https://www.rtvs.sk/json/live5f.json"
PARAMS = {'ad':1,'b':'chrome','p':'win','v':'77','f':0,'d':1}
CHANNEL_PARAM = 'c'
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO
    
    prefer_mpd = xbmcplugin.getSetting(_handle, 'rtvsmpd') == 'true'
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(API_INIT)
    params = {CHANNEL_PARAM:CHANNELS[channel]}
    params.update(PARAMS)
    response = session.get(API, params=params)
    data = response.json()
    clip = data['clip']
    sources = clip['sources']
    hls = None
    mpd = None
    for src in sources:
        if src['type'] == "application/dash+xml":
            mpd = src['src'].replace('\n','')
        elif src['type'] == "application/x-mpegurl":
            hls = src['src'].replace('\n','')
    
    uheaders = urlencode(HEADERS)

    if (prefer_mpd or hls is None) and mpd is not None:
        li = xbmcgui.ListItem(path=mpd)
        setup_adaptive(li, uheaders, 'mpd')
        xbmcplugin.setResolvedUrl(_handle, True, li)
    elif hls is not None:
        li = xbmcgui.ListItem(path=hls)
        setup_adaptive(li, uheaders, 'hls')
        xbmcplugin.setResolvedUrl(_handle, True, li)
    else:
        raise #TODO
            