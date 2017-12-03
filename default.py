# -*- coding: utf-8 -*-

import urllib
try:
    from urllib.parse import parse_qs
except ImportError:
     from urlparse import parse_qs
from urllib import urlencode
import sys
import json

#kodi libs import
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

#okino custom lib import
import okino

#constants
settingLastSearches = 'lastsearches'
settingLastViewed = 'lastviewed'
maxLastSearches = 5
maxLastViewed = 5

_Addon = xbmcaddon.Addon(id='plugin.video.okino.tv')
__language__ = _Addon.getLocalizedString

addon_icon = _Addon.getAddonInfo('icon')
addon_fanart = _Addon.getAddonInfo('fanart')
addon_path = _Addon.getAddonInfo('path')
addon_type = _Addon.getAddonInfo('type')
addon_id = _Addon.getAddonInfo('id')
addon_author = _Addon.getAddonInfo('author')
addon_name = _Addon.getAddonInfo('name')
addon_version = _Addon.getAddonInfo('version')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = {}
if len(sys.argv)>1:
    args = parse_qs(sys.argv[2][1:])
print("Parameters: "+str(args))

#utility functions
def getSettingsList(settingId):
    value = urllib.unquote(_Addon.getSetting(settingId))#.decode('utf-8')
    
    if len(value)<3:#this means there are some \r\n or smt
        return []
    else:
        return json.loads(value)

def setSettingsList(settingId, value, maxElements = 0):
    if maxElements > 0:
        value = value[-maxElements:]
    _Addon.setSetting(settingId,urllib.quote(json.dumps(value)))#.encode('utf-8')))

def build_url(params):
    return '%s?%s' % (base_url, urllib.urlencode(params))

def showMessage(heading, message, times=3000, pics=addon_icon):
    try:
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (
        heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception as e:
        xbmc.log('[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2)
        try:
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception as e:
            xbmc.log('[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3)

#plugin functions
##########################################################

def doSearch(keyword):
    print('[%s]: doSearch: search by keyword - [%s]' % (addon_id, keyword))
    hits = okino.do_search(keyword)

    for hit in hits:
        print('[%s]: doSearch: hit [%s] image [%s] url [%s]' % (addon_id, hit[1].encode('utf-8'), hit[2].encode('utf-8'), hit[0].encode('utf-8')))
        li = xbmcgui.ListItem(hit[1], iconImage=hit[2], thumbnailImage=hit[2])
        
        uri = build_url({
            'func': 'playItem',
            'mtitle': hit[1].encode('utf-8'),
            'mimage': hit[2].encode('utf-8'),
            'mpath': hit[0].encode('utf-8')
        })
        
        li.setInfo(type='Video', infoLabels={'title': hit[1], 'plot': hit[1]})
        li.setProperty('fanart_image', addon_fanart)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(addon_handle, uri, li, False)

    xbmcplugin.setContent(addon_handle, 'movies')
    xbmcplugin.endOfDirectory(addon_handle)

def playItem(args):
    link = okino.do_getvideo(args['mpath'][0])
    
    #setSettingsList(settingLastViewed,'',maxLastViewed)
    #remember movie opened
    movies = getSettingsList(settingLastViewed)
    
    movie_exists = 0
    for movie in movies:
        margs = parse_qs(movie)
        if margs['mpath'][0] == args['mpath'][0]:
            movie_exists = 1
            break
    
    if movie_exists == 0:
        uri = build_url({            
            'mtitle': args['mtitle'][0].decode('utf-8').encode('utf-8'),
            'mimage': args['mimage'][0].decode('utf-8').encode('utf-8'),
            'mpath': args['mpath'][0].decode('utf-8').encode('utf-8'),
        })    
        movies.append(uri)
        setSettingsList(settingLastViewed,movies,maxLastViewed)
    
    item = xbmcgui.ListItem(path=link)
    xbmcplugin.setResolvedUrl(addon_handle, True, item)

def oldSearch(args):
    doSearch(args['mpath'][0])

def newSearch(args):
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading(u'Поиск')
    kbd.doModal()
    
    if kbd.isConfirmed():
        sts = kbd.getText()
        
        #remember search
        searches = getSettingsList(settingLastSearches)
    
        if sts.decode('utf-8') not in searches:#add search
            searches.append(sts)
            setSettingsList(settingLastSearches,searches,maxLastSearches)
        
        #now do the search
        doSearch(sts)

def run_settings(params):
    _Addon.openSettings()

def mainScreen(params):
    li = xbmcgui.ListItem(u'Поиск', iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = build_url({
        'func': 'mainSearch'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(addon_handle, uri, li, True)
    
    li = xbmcgui.ListItem(u'Последние просмотренные видео', iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = build_url({
        'func': 'mainLastViewed'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(addon_handle, uri, li, True)

    xbmcplugin.setContent(addon_handle, 'files')
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True, updateListing=False, cacheToDisc=True)

def mainSearch(params):
    li = xbmcgui.ListItem(u'Новый поиск', iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = build_url({
        'func': 'newSearch'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(addon_handle, uri, li, True)
    
    #read and list previous searches
    searches = getSettingsList(settingLastSearches)
    for search in searches:
        li = xbmcgui.ListItem('['+search+']', iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = build_url({
            'func': 'oldSearch',
            'mpath': search.encode('utf-8')
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(addon_handle, uri, li, True)   
    
    xbmcplugin.setContent(addon_handle, 'files')
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True, updateListing=False, cacheToDisc=True)

def mainLastViewed(params):
    #read and list previous viewed movies
    movies = getSettingsList(settingLastViewed)
    for movie in movies:

        args = parse_qs(movie[len(base_url)+1:])

        li = xbmcgui.ListItem(args['mtitle'][0],args['mimage'][0], thumbnailImage=args['mimage'][0])
        
        uri = build_url({
            'func': 'playItem',
            'mtitle': args['mtitle'][0].encode('utf-8'),
            'mimage': args['mimage'][0].encode('utf-8'),
            'mpath': args['mpath'][0].encode('utf-8')
        })
        
        li.setInfo(type='Video', infoLabels={'title': args['mtitle'][0], 'plot': args['mtitle'][0]})
        li.setProperty('fanart_image', addon_fanart)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(addon_handle, uri, li, False) 
    
    xbmcplugin.setContent(addon_handle, 'files')
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True, updateListing=False, cacheToDisc=True)

#main program
func = args.get('func', None)

if func is None:
    xbmc.log('[%s]: Primary input' % addon_id, 1)
    mainScreen(args)
else:
    globals()[func[0]](args)

