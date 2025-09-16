# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 19.12.2021
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


CHANNELS = {
    'm1':'https://www.youtube.com/watch?v=_Z03zwFd8yI',
    'm2':'https://c401-node62-cdn.connectmedia.hu/110102/3cf4e460d05d1cd6e78f1aec0d7ae914/68c8a1fe/index.m3u8',
    'm4magyar':'https://livestreamlinks.net/en/onlinetv/hungary/m4magyar',
    'm5':'https://livestreamlinks.net/en/onlinetv/hungary/m5',
    'rtlklub':'https://livestreamlinks.net/en/onlinetv/hungary/rtlklub',
    'rtlii':'https://livestreamlinks.net/en/onlinetv/hungary/rtlii',
    'tv2':'https://livestreamlinks.net/en/onlinetv/hungary/tv2',
    'super-tv2':'https://livestreamlinks.net/en/onlinetv/hungary/super-tv2',
    'filmplusz':'https://livestreamlinks.net/en/onlinetv/hungary/filmplusz',
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    li = xbmcgui.ListItem(path=CHANNELS[channel]+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)


