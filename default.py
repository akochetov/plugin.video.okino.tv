#!/usr/bin/python

import urllib
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import get_video_url

Addon = xbmcaddon.Addon(id='plugin.video.okino.net')
__language__ = Addon.getLocalizedString

addon_icon = Addon.getAddonInfo('icon')
addon_fanart = Addon.getAddonInfo('fanart')
addon_path = Addon.getAddonInfo('path')
addon_type = Addon.getAddonInfo('type')
addon_id = Addon.getAddonInfo('id')
addon_author = Addon.getAddonInfo('author')
addon_name = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

hos = int(sys.argv[1])

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def showMessage(heading, message, times=3000, pics=addon_icon):
    try:
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (
        heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log('[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2)
        try:
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log('[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3)

def doSearch(params):
    hits = get_video_url.do_search(params['link'])

    i = 0
    for hit in hits:
        li = xbmcgui.ListItem(hit[1], iconImage=hit[2], thumbnailImage=hit[2])
        uri = construct_request({
            'func': 'openitem',
            'mpath': hit[0]
        })
        li.setInfo(type='Video', infoLabels={'title': hit[1], 'plot': hit[1]})
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        i = i + 1
        if len(hits) < i: i = 0
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(hos)

def playitem(params):
    link = get_video_url.do_getvideo(params['mpath'])
    item = xbmcgui.ListItem(path=link)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def _doSearch(params):
    usearch = params.get('usearch', False)
    if usearch:
        doSearch(params['keyword'])
        return

    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading('Поиск')
    kbd.doModal()
    if kbd.isConfirmed():
        sts = kbd.getText()
        doSearch(urllib.quote(sts))

def run_settings(params):
    Addon.openSettings()

def mainScreen(params):
    li = xbmcgui.ListItem('Поиск', iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = construct_request({
        'func': '_doSearch'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)

    xbmcplugin.setContent(hos, 'files')
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param


params = get_params(sys.argv[2])
try:
    func = params['func']
    del params['func']
except:
    func = None
    xbmc.log('[%s]: Primary input' % addon_id, 1)
    mainScreen(params)
if func != None:
    try:
        pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log('[%s]: Function "%s" not found' % (addon_id, func), 4)
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)

