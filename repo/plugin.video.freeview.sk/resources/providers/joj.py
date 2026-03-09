# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies

try:
    from urllib import urlencode, quote
except ImportError:
    from urllib.parse import urlencode, quote

from utils import setup_adaptive
    
CHANNELS = {
    'joj':{'id':'LYyAwEjjqmj8kMY23Lqw', 'hls':'joj.m3u8'},
    'plus':{'id':'60K9GwR6CLApIHVyNYOj', 'hls':'plus.m3u8'},
    'wau':{'id':'0D9v2CuujVAlLJJTyLWd', 'hls':'wau.m3u8'},
    'family':{'hls':'family.m3u8'},
    'joj24':{'id':'7tl6We5FhLyCfZcmSG6F', 'hls':'joj_news.m3u8'},
    'jojko':{'hls':'jojko.m3u8'},
    'jojcinema':{'hls':'cinema.m3u8'},
    'csfilm':{'hls':'cs_film.m3u8'},
    'cshistory':{'hls':'cs_history.m3u8'},
    'csmystery':{'hls':'cs_mystery.m3u8'},
    'jojsport':{'hls':'joj_sport.m3u8'},
    'jojsport2':{'hls':'joj_sport2.m3u8'}
}

PAYLOAD = {
    "data": {
        "id":"",
        "documentType":"tvChannel",
        "sourceHistory":[],
        "capabilities":[
            {"codec":"h264","protocol":"dash","encryption":"none"},
            {"codec":"h264","protocol":"hls","encryption":"none"}
        ]
    }
}

SOURCE = "https://europe-west3-tivio-production.cloudfunctions.net/getSourceUrl"
FALLBACK = "https://live.cdn.joj.sk/live/"

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', 'Referer': 'https://www.joj.sk/'}

def brexit(_addon, _handle, word):
    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30105) + word)
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
    return False
    
def getSource(channel):
    if 'id' in channel:
        try: 
            session = requests.Session()
            headers = {"Content-Type": "application/json"}
            headers.update(HEADERS)
            PAYLOAD['data']['id'] = channel['id']
            response = session.post(SOURCE, json=PAYLOAD, headers=headers)
            response.raise_for_status()
            data = response.json()
            url = data['result']['url']
            manifest = 'mpd' if url.endswith('.mpd') else 'hls'
            return {'url': url, 'manifest': manifest, 'headers': HEADERS, 'adaptive': True}
        except Exception as e:
            #TODO log?
            pass
    # fallback
    return {'url': FALLBACK + channel['hls'], 'manifest':'hls', 'headers': HEADERS, 'adaptive': False}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    data = getSource(CHANNELS[channel])
    
    uheaders = urlencode(data['headers'])
    
    if data['adaptive']:
        li = xbmcgui.ListItem(path=data['url'])
        setup_adaptive(li, uheaders, data['manifest'])
    else:
        li = xbmcgui.ListItem(path=data['url']+'|'+uheaders)

    xbmcplugin.setResolvedUrl(_handle, True, li)
