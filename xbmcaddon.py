import os

class Addon:
    _id = ""
    def __init__(self,id=""):
        self._id = id
        
    getLocalizedString = ""
                
    def getAddonInfo(self,key):
        print('xbmcaddon.Addon.getAddonInfo id:%s key:%s' % (self._id, key))
        
    def setSetting(self,settingId,value):
        print('xbmcaddon.Addon.setSetting settingId:%s value:%s' % (settingId, value))
        
        file = open(settingId+'.txt','w')
        file.write(value)
        file.close()
        
    def getSetting(self,settingId):       
        if not os.path.isfile(settingId+'.txt'):
            return ''
        
        file = open(settingId+'.txt','r')
        value = file.read()
        file.close()
        
        print('xbmcaddon.Addon.getSetting settingId:%s value:%s' % (settingId, str(value)))
        
        return value