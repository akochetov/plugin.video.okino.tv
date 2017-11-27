class Addon:
    _id = ""
    def __init__(self,id=""):
        self._id = id
        
    getLocalizedString = ""
                
    def getAddonInfo(self,key):
        print('xbmcaddon.Addon.getAddonInfo id:%s key:%s' % (self._id, key))
