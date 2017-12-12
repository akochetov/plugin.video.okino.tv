# -*- coding: utf-8 -*-
#class for search hits info
class SearchHit:
    _url = ''
    _title = ''
    _image = ''

    def __init__(self, url, title, image):
        self._url = url
        self._title = title
        self._image = image
    
        
    def url(self):
        return self._url
    def title(self):
        return self._title
    def image(self):
        return self._image

class Movie(SearchHit):
    _videourl = ''
    
    def videourl(self):
        return self._videourl

class Translations():
    _translations = []
    
    def __init__(self, hit, translations):
        for trn in translations:
            url = hit.url()
            i = url.rfind('/iframe')
            url2 = url[i:]
            url = url[0:i]
            i = url.rfind('/')
            url1 = url[0:i+1]
            url = url1 + trn[0] + url2
            self._translations.append(SearchHit(url=url,title='Перевод - '.decode('utf-8')+trn[1],image = hit.image()))
    
    def translations(self):
        return self._translations

class Series():
    _ref = ''
    _seasons = []
    
    def __init__(self, hit, seasons, ref):
        for season in seasons:
            s = Season(hit.url(),hit.title(),hit.image(),[],ref,int(season))
            self._seasons.append(s)
        self._ref = ref
    
    def seasons(self):
        return self._seasons    

class Season(Series,SearchHit):
    _episodes = []
    _season = 0
    
    def __init__(self, url, title, image, episodes, ref, season):
        self._title = title
        self._url = url
        self._image = image
        self._ref = ref
        self._season = season

        for episode in episodes:
            s = Episode(url,title,image,ref,int(season),int(episode[1]))
            self._episodes.append(s)

    def title(self):
        return 'Сезон '.decode('utf-8')+str(self._season)+'. '+self._title

    def url(self):
        return self._url+'?season='+str(self._season)+'&ref='+self._ref

    def episodes(self):
        return self._episodes

class Episode(Season):
    _episode = 0
    _season = 0
    
    def __init__(self, url, title, image, ref, season, episode):
        self._title = title
        self._url = url
        self._image = image
        self._ref = ref
        self._season = season
        self._episode = episode
    
    def title(self):
        return 'Сезон '.decode('utf-8')+str(self._season)+'. Серия '.decode('utf-8')+str(self._episode)+'. '+self._title
                
    def url(self):
        return self._url+'&episode='+str(self._episode)
    
    def translations(self):
        return self._translations
