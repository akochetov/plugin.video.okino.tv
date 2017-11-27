class Item:
    def setProperty(self,property,value):
        print('xbmcgui.Item.setProperty property:%s value:%s' % (property, value))
    def setInfo(self, type, infoLabels):
        print('xbmcgui.Item.setInfo type:%s infoLabels:%s' % (type, infoLabels))

def ListItem(title="", path="", iconImage="", thumbnailImage=""):
    print('xbmcgui.ListItem title:%s path:%s iconImage:%s thumbnailImage:%s' % (title, path, iconImage, thumbnailImage))
    return Item()
def log(message,args):
    print('xbmcgui.log %s %s' % (message, str(args)));
        
