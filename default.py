# -*- coding: utf-8 -*-

import urllib
try:
    from urllib.parse import parse_qs
except ImportError:
     from urlparse import parse_qs
from urllib import urlencode
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import okino

Addon = xbmcaddon.Addon(id='plugin.video.okino.tv')
__language__ = Addon.getLocalizedString

addon_icon = Addon.getAddonInfo('icon')
addon_fanart = Addon.getAddonInfo('fanart')
addon_path = Addon.getAddonInfo('path')
addon_type = Addon.getAddonInfo('type')
addon_id = Addon.getAddonInfo('id')
addon_author = Addon.getAddonInfo('author')
addon_name = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

base_url = sys.argv[0]
addon_handle = sys.argv[1]
args = {}
if len(sys.argv)>1:
    args = parse_qs(sys.argv[2][1:])
print("Parameters: "+str(args))

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

def doSearch(keyword):
    hits = okino.do_search(keyword)

    for hit in hits:
        li = xbmcgui.ListItem(hit[1], iconImage=hit[2], thumbnailImage=hit[2])
        print("Item url:" + hit[0])
        uri = build_url({
            'func': '_playItem',
            'mpath': hit[0]
        })
        li.setInfo(type='Video', infoLabels={'title': hit[1], 'plot': hit[1]})
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(addon_handle, uri, li, True)

    xbmcplugin.setContent(addon_handle, 'movies')
    xbmcplugin.endOfDirectory(addon_handle)

def _playItem(args):
    link = okino.do_getvideo(args['mpath'][0])
    item = xbmcgui.ListItem(path=link)
    xbmcplugin.setResolvedUrl(addon_handle, True, item)

def _doSearch(args):
    usearch = args.get('usearch', False)
    if usearch:
        doSearch(args['keyword'])
        return

    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading(u'Поиск')
    kbd.doModal()
    if kbd.isConfirmed():
        sts = kbd.getText()
        print("Entered text: "+sts)
        doSearch(urllib.quote(sts))

def run_settings(params):
    Addon.openSettings()

def mainScreen(params):
    li = xbmcgui.ListItem(u'Поиск', iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = build_url({
        'func': '_doSearch'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(addon_handle, uri, li, True)

    xbmcplugin.setContent(addon_handle, 'files')
    xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True, updateListing=False, cacheToDisc=True)

#main program
func = args.get('func', None)

if func is None:
    xbmc.log('[%s]: Primary input' % addon_id, 1)
    mainScreen(args)
else:
    globals()[func[0]](args)
    #try:
     #   globals()[func[0]](args)
    #except Exception as e: 
     #   xbmc.log('[%s]: Function "%s" not found. Exception: %s' % (addon_id, func, str(e)), 4)
      #  showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)

