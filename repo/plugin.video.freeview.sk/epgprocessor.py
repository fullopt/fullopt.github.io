# -*- coding: utf-8 -*-
# Module: epgprocessor
# Author: cache-sk
# Modified by: cratos38
# License: MIT https://opensource.org/licenses/MIT

import os
import gzip
import xml.etree.ElementTree as ET
from datetime import datetime
import xbmc
import xbmcaddon
import xbmcvfs
import traceback
import requests.cookies

try:
    from xbmc import translatePath
except ImportError:
    from xbmcvfs import translatePath
    
EPG_URLS = [
    'https://iptv-epg.org/files/epg-cz.xml.gz',
    'https://iptv-epg.org/files/epg-hu.xml.gz'
]
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'}

_addon = xbmcaddon.Addon()
_addon_path = translatePath(_addon.getAddonInfo('profile'))

try:
    unicode  # Python 2
    PY2 = True
except NameError:
    PY2 = False

def log(msg):
    """Log messages to Kodi log"""
    if PY2:
        try:
            msg = msg.encode('utf-8')
        except:
            pass
    xbmc.log('[FREEVIEW EPG] %s' % msg, xbmc.LOGINFO)

def download_epg(url):
    """
    Download EPG data from iptv-epg.org
    Returns: Path to downloaded file or None if failed
    """

    log(u'Downloading EPG from: %s' % url)
    
    epg_file = os.path.join(_addon_path, 'epg-cz.xml.gz')

    

    try:
        session = requests.Session()
        r = session.get(url, headers=HEADERS, stream=True, allow_redirects=True)
        r.raise_for_status()

        with open(epg_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    
        log(u'EPG downloaded successfully: %s' % epg_file)
        return epg_file
    except Exception as e:
        log(u'ERROR downloading EPG: %s' % str(e))
        return None

def extract_epg(gz_file):
    """
    Extract gzipped EPG file
    Returns: Path to extracted XML or None if failed
    """
    try:
        xml_file = gz_file.replace('.gz', '')
        
        log(u'Extracting EPG: %s -> %s' % (gz_file, xml_file))
        
        with gzip.open(gz_file, 'rb') as f_in:
            with open(xml_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        log(u'EPG extracted successfully')
        return xml_file
        
    except Exception as e:
        log(u'ERROR extracting EPG: %s' % str(e))
        return None

def parse_epg(channel_ids, xml_file):
    """
    Parse EPG XML and return programme data
    Returns: Dictionary of {channel_id: [programmes]}
    """
    try:
        log(u'Parsing EPG XML: %s' % xml_file)
        
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        epg_data = {i: [] for i in channel_ids}
        
        # Parse programmes
        for programme in root.findall('programme'):
            channel = programme.get('channel')
            if channel in channel_ids:
                epg_data[channel].append({
                    'start': programme.get('start'),
                    'stop': programme.get('stop'),
                    'title': programme.find('title').text if programme.find('title') is not None else '',
                    'desc': programme.find('desc').text if programme.find('desc') is not None else ''
                })
        
        log(u'EPG parsed: %d channels, %d programmes' % (len(epg_data), sum(len(p) for p in epg_data.values())))
        return epg_data
        
    except Exception as e:
        log(u'ERROR parsing EPG: %s' % str(e))
        return {}

def generate_xmltv(channels, epg_data, output_file):
    """
    Generate XMLTV file for Kodi PVR
    """
    try:
        log(u'Generating XMLTV: %s' % output_file)
        
        root = ET.Element('tv')
        root.set('generator-info-name', 'Freeview.sk EPG Processor')

        for channel in channels:
            if channel.get('id') and channel.get('name'):
                log(u"Channel %s : %s" % (channel['id'], channel['name']))
                channel_elem = ET.SubElement(root, 'channel')
                channel_elem.set('id', channel['id'])
                display_name = ET.SubElement(channel_elem, 'display-name')
                display_name.text = channel['name']
        
        # Add programmes
        for channel_id, programmes in epg_data.items():
            log(u'Processing %s' % channel_id)
            for prog in programmes:
                programme_elem = ET.SubElement(root, 'programme')
                programme_elem.set('channel', channel_id)
                programme_elem.set('start', prog['start'])
                programme_elem.set('stop', prog['stop'])
                
                title_elem = ET.SubElement(programme_elem, 'title')
                title_elem.text = prog['title']
                
                if prog['desc']:
                    desc_elem = ET.SubElement(programme_elem, 'desc')
                    desc_elem.set('lang', 'cs')
                    desc_elem.text = prog['desc']
        
        # Write XML
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        log(u'XMLTV generated successfully: %s' % output_file)
        return True
        
    except Exception as e:
        log(u'ERROR generating XMLTV: %s' % str(e))
        traceback.print_exc()
        return False

def update_epg(channels):
    """
    Main function to update EPG
    Called by service.py or manually
    """
    log(u'========================================')
    log(u'EPG UPDATE STARTED')
    log(u'========================================')
    
    channel_ids = [i['id'] for i in channels if i.get('id') and i.get('name')]
    
    # This dictionary will hold all combined data from all sources
    merged_epg_data = {i: [] for i in channel_ids}
    
    for url in EPG_URLS:
        # Download
        gz_file = download_epg(url)
        if not gz_file:
            log(u'EPG update FAILED: Download error')
            return False
    
        # Extract
        xml_file = extract_epg(gz_file)
        if not xml_file:
            log(u'EPG update FAILED: Extraction error')
            return False
    
        # Parse & merge
        epg_data = parse_epg(channel_ids, xml_file)
        if not epg_data:
            log(u'EPG update FAILED: Parsing error')
            return False
        for cid, programmes in epg_data.items():
            if programmes:
                # Add new programmes to our master list for this channel
                merged_epg_data[cid].extend(programmes)
                
        # Cleanup
        try:
            os.remove(gz_file)
            os.remove(xml_file)
        except:
            pass
    
    # Generate XMLTV
    output_file = os.path.join(_addon_path, 'epg.xml')
    if not generate_xmltv(channels, merged_epg_data, output_file):
        log(u'EPG update FAILED: Generation error')
        return False
    
    log(u'========================================')
    log(u'EPG UPDATE COMPLETED SUCCESSFULLY')
    log(u'Output: %s' % output_file)
    log(u'========================================')
    
    return True
