# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 18.11.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import io
import os
import sys
import requests
import datetime
import time
import xbmc
import xml.etree.ElementTree as ET
from dateutil.tz import tzutc, tzlocal

sys.path.append(os.path.join (os.path.dirname(__file__), 'resources', 'providers'))

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'}
EPG_URL = "https://raw.githubusercontent.com/370network/skylink-xmltv/refs/heads/main/a3b_a1.xml"

def ts(dt):
    return int(time.mktime(dt.timetuple())) * 1000

def get_epg(channels, from_date, days=7, recalculate=True):

    result = {}

    ids = {}
    for channel in channels:
        if channel['id'].isnumeric():
            if u'0' != channel['id']:
                # non zero number = skylink id
                ids[channel['id']] = channel['name']
        else:
            ids[channel['id']] = channel['name']

    xbmc.log("EPG CHANNELS: " + str(ids), xbmc.LOGINFO);

    if recalculate:
        from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=datetime.timezone.utc)
        to_date = from_date + datetime.timedelta(days=days)
    else:
        to_date = from_date + datetime.timedelta(days=days)

    # Try fetching XMLTV
    session = requests.Session()
    resp = session.get(EPG_URL, timeout=10, headers=HEADERS)
    if resp.status_code == 200 and resp.text.strip():
        root = ET.fromstring(resp.content)
        # build map of xmltv channel id -> display-name
        xml_channels = {}
        for ch in root.findall('channel'):
            id = ch.get('id')
            name = ch.find('display-name')
            if name is not None:
                xml_channels[id] = name.text.strip()
            else:
                xml_channels[id] = id
        # parse programmes
        for prog in root.findall('programme'):
            chref = prog.get('channel')
            # decide target channel id in addon
            target = None
            if chref in ids:
                target = chref
            else:
                continue
            
            # extract fields
            title_el = prog.find('title')
            desc_el = prog.find('desc')
            start = prog.get('start')
            stop = prog.get('stop')
            
            # xmltv times are YYYYMMDDHHMMSS +/-HHMM, handle basic case
            fmt = '%Y%m%d%H%M%S%z' if len(start) > 14 else '%Y%m%d%H%M%S'
            dt_start = datetime.datetime.strptime(start.replace(' ', ''), fmt).astimezone(datetime.timezone.utc)
            fmt = '%Y%m%d%H%M%S%z' if len(stop) > 14 else '%Y%m%d%H%M%S'
            dt_stop = datetime.datetime.strptime(stop.replace(' ', ''), fmt).astimezone(datetime.timezone.utc)

            if dt_start >= from_date and dt_start <= to_date:
                item = {}
                if title_el is not None and title_el.text:
                    item['title'] = title_el.text.strip()
                if desc_el is not None and desc_el.text:
                    item['description'] = desc_el.text.strip()
                if dt_start is not None and dt_stop is not None:
                    item['dtstart'] = dt_start
                    item['dtend'] = dt_stop
                # append to result
                if target not in result:
                    result[target] = []
                result[target].append(item)

    xbmc.log("EPG ITEMS FOUND: " + str(len(result)), xbmc.LOGINFO);
    return result


def generate_plot(epg, now, chtitle, items_left = 3):

    def get_plot_line(start, title):
        time = start.strftime('%H:%M')
        try:
            time = time.decode('UTF-8')
        except AttributeError:
            pass
        return '[B]' + time + '[/B] ' + title + '[CR]'

    plot = u''
    nowutc = now.replace(tzinfo=tzlocal())
    tomorrowutc = nowutc + datetime.timedelta(days=1)
    for program in epg:
        start = now
        if 'start' in program and program['start']:
            start = datetime.datetime.utcfromtimestamp(program['start']).replace(tzinfo=tzutc()).astimezone(tzlocal())
        else:
            start = program['dtstart'].astimezone(tzlocal())
        
        show_item = False
        if 'duration' in program and program['duration']:
            show_item = start + datetime.timedelta(minutes=program['duration']) > nowutc
        else:
            show_item = program['dtend'] > nowutc and len(plot) == 0 and program['dtstart'] < tomorrowutc
        
        if show_item:
            plot += get_plot_line(start, program['title'] if 'title' in program else chtitle)
            items_left -= 1
            if items_left == 0:
                break

    plot = plot[:-4]
    return plot

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    if text is not None:
        return "".join(html_escape_table.get(c, c) for c in text)
    return ""
    
def generate_xmltv(channels, epg, path):
    now = datetime.datetime.now()
    with io.open(path, 'w', encoding='utf8') as file:
        file.write(u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        file.write(u'<tv>\n')

        for channel in channels:
            #print(channel)
            file.write(u'<channel id="%s">\n' % channel['id'])
            file.write(u'<display-name>%s</display-name>\n' % channel['name'])
            file.write(u'</channel>\n')

        for channel in epg:
            for program in epg[channel]:
                begin = now
                
                if 'start' in program and program['start']:
                    begin = datetime.datetime.utcfromtimestamp(program['start'])
                else:
                    begin = program['dtstart']
                end = begin
                if 'duration' in program and program['duration']:
                    end = begin + datetime.timedelta(minutes=program['duration'])
                else:
                    end = program['dtend']
                
                file.write(u'<programme channel="%s" start="%s" stop="%s">\n' % (
                    channel, begin.strftime('%Y%m%d%H%M%S'), end.strftime('%Y%m%d%H%M%S')))
                if 'title' in program:
                    file.write(u'<title>%s</title>\n' % html_escape(program['title']))
                if 'description' in program and program['description'] != '':
                    file.write(u'<desc>%s</desc>\n' % html_escape(program['description']))
                if 'cover' in program:
                    file.write(u'<icon src="%s"/>\n' % html_escape(program['cover']))
                if 'genres' in program and len(program['genres']) > 0:
                    file.write('<category>%s</category>\n' % ', '.join(program['genres']))
                file.write(u'</programme>\n')
        file.write(u'</tv>\n')

