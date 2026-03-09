import xbmc

def setup_adaptive(li, uheaders, manifest_type):
    KODI_MAJOR = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])
    
    if KODI_MAJOR < 19:
        li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    else:
        li.setProperty('inputstream','inputstream.adaptive') #kodi 19+
    
    if uheaders is not None:
        li.setProperty('inputstream.adaptive.stream_headers', uheaders)
    
    if KODI_MAJOR >= 20 and uheaders is not None:
        li.setProperty('inputstream.adaptive.manifest_headers', uheaders)
 
    if KODI_MAJOR >= 22 and uheaders is not None:
        li.setProperty('inputstream.adaptive.common_headers', uheaders)
 
    if KODI_MAJOR < 22 and manifest_type is not None:
        li.setProperty('inputstream.adaptive.manifest_type', manifest_type)
