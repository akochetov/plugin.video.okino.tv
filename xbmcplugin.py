def addDirectoryItem(handle, url, listitem, isFolder = False, totalItems = -1):
       print('xbmcplugin.addDirectoryItem handle:%s url:%s listitem:%s, isFolder:%s, totalItmes %i' % (handle, url, listitem, str(isFolder),totalItems))
def setResolvedUrl(handle, succeeded, listitem):
    print('xbmcplugin.setResolvedUrl handle:%s succeded:%s listitem:%s' % (handle, str(succeeded), listitem))
def setContent(handle, content):
    print('xbmcplugin.setContent handle:%s content:%s' % (handle, content))
def endOfDirectory(handle, succeeded = True, updateListing=False, cacheToDisc=True):
    print('xbmcplugin.endOfDirectory handle:%s succeded:%s updateListing:%s cacheToDisc:%s' % (handle, str(succeeded), str(updateListing), str(cacheToDisc)))