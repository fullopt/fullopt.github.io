# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 16.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from utils import setup_adaptive

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
CHANNELS = {
    'prima':{'id':'id-p111013'},
    'love':{'id':'id-p111016'},
    'krimi':{'id':'id-p432829'},
    'max':{'id':'id-p111017'},
    'cool':{'id':'id-p111014'},
    'zoom':{'id':'id-p111015'},
    'star':{'id':'id-p846043'},
    'show':{'id':'id-p899572'},
    'cnn':{'id':'id-p650443'}
}

def play(_handle, _addon, params):
    channel = params['channel']
    
    # Check if the channel key exists in our CHANNELS dictionary
    if channel in CHANNELS:
        # Retrieve the specific ID for this channel
        channel_id = CHANNELS[channel]['id']
        
        session = requests.Session()
        headers = {}
        headers.update(HEADERS)
        
        # Inject the channel_id into the API endpoint
        url = f'https://api.play-backend.iprima.cz/api/v1/products/{channel_id}/play'
        
        response = session.get(url, headers=headers)
        data = response.json()
        if 'streamInfos' in data and data['streamInfos']:
            stream = data['streamInfos'][0]['url']
            stream = stream.replace("_lq", "") #remove lq profile
            li = xbmcgui.ListItem(path=stream)
            setup_adaptive(li, None, 'hls')
            xbmcplugin.setResolvedUrl(_handle, True, li)
    else:
        raise #TODO