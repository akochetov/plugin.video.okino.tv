import urllib
try:
    from urllib.request import Request
except ImportError:
    from urllib2 import Request
    
try:
    from urllib.parse import parse_qs
except ImportError:
     from urlparse import parse_qs
     
from urllib import urlencode
from urllib2 import urlopen
import re
import json

from okinoclasses import *
from crypt import get_chiper

#constants
#video quality list. we will be picking highest by default
video_quality = ['1080', '720', '640', '480', '320', '240']
#page to access when making search
url_search = 'https://mygid.org'
#some player id neeeded to get videos
mw_key = '1ffd4aa558cc51f5a9fc6888e7bc5cb4'
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'

#search
def do_search(keyword):
    hits = []
    post_fields = {'do': 'search',
                   'subaction': 'search',
                   'story': keyword.decode('utf-8').encode('cp1251')}

    headers = {'User-Agent':agent,
               #'Content-Type':'application/x-www-form-urlencoded ; charset=UTF-8',
               'Cache-Control':'max-age=0'}
    
    request = Request(url_search,urlencode(post_fields),headers)
    html = urlopen(request).read().decode('cp1251')
    
    #print(html.encode('utf-8'))

    hrefs=re.compile('<a class="short-poster img-box with-mask" href="([^"]+?)">').findall(html)    
    names=re.compile('<div class="short-title">([^"]+?)</div>').findall(html)
    pics=re.compile('<div class="short-in">[\S\s]+?<img src="([^"]+?)"').findall(html)

    for i,href in enumerate(hrefs):
        pic = pics[i]
        if pic[0]=='/':
            pic = url_search+'/'+pic
        hits.append(SearchHit(url=hrefs[i],title = names[i],image=pic))

    return(hits)

def getToken(expression,html):
    res = re.compile(expression).findall(html)
    if len(res)>0:
        return res[0]
    else:
        return ''

def do_getvideo(hit,justPlay=False):
    if hit.url().find('/iframe')<0:
        headers = {
            'User-Agent': agent,
            'Connection': 'keep-alive',
            'Cache-Control':'max-age=0'}
        # getting movie page
        #print('Requesting movie page: '+movie_page_url)
        request = Request(hit.url(), headers=headers)
        html = urlopen(request).read().decode('cp1251')
        #print(html)
        iframe = re.compile('<iframe src="([^"]+?)"').findall(html)[0]
    else:
        iframe = hit.url()

    # getting movie player page
    url = iframe
    headers = {
        'User-Agent': agent,
        #'Cookie': '_moon_session=M2gvbXJOZFlHMnZTMjRUQXJpUzlyNFF2U1h4VUptVnE1dE0wUFl4RUtmWnQxa0hvL3hGYWI0MnBWZlhnTnozSmMyenZjZHlKVWhjQ2tuQkd3TGJqUXZlNW83OFp3SXU2NlMwVXhJbVgxZktlOGFneWlmRXdZdCtnVmo5YkxZN1JBcml3MjlicVFiTVhPdUVvcXlxSmp3SThuU0VKb1F2RkFlTnVSeFIzeDJnKzYvVEV4VklZWjQ2OXdlNk51dU1lLS1nZzFIOTZ5Ny9hbFNsbWNVTVhqR0NBPT0%3D--0fc05515225f7f5246e62e8fb2292568d5a45864; _364966110049=1; _364966110050=1512852760407',
        'Referer': hit.url()}
    request = Request(url, headers=headers)
    response = urlopen(request)
    html = response.read().decode('utf-8')#response.headers.get_content_charset())
    #print(html)

    #parse out parameters
    video_token = getToken('video_token: \'([^\']+?)\'',html)
    user_token = getToken('user_token: \'([^"]+?)\'',html)
    if len(user_token)==0:
        user_token = getToken('serial_token: \'([^"]+?)\'',html)    
    mw_pid = getToken('partner_id: ([^"]+?),',html)
    p_domain_id = getToken('domain_id: ([^"]+?),',html)
    host = getToken('host: \'([^"]+?)\'',html)
    proto = getToken('proto: \'([^"]+?)\'',html)
    port = getToken('port: ([^"]+?),',html)
    window_data = getToken('window\[\'([^"]+?)\'\] = \'[^"]+?\';',html)
    post_data = getToken('window\[[^"]+?\] = \'([^"]+?)\';',html)
   
    #create return value (video), for now from base class
    video = Movie(iframe,hit.title(),hit.image())
    
    if not justPlay:
        #parse out series related parameters
        seasons = getToken('seasons: ([^"]+?),\n',html)
        episodes = getToken('episodes: ([^"]+?),\n',html)
        translations = getToken('translations: (.+?),\n',html)
        ref = getToken('encodeURIComponent\(\'(.+?)\'\),',html)
        
        if hit.url().find('/iframe')<0 and len(translations)>5 and len(seasons)>5:
            print('Returning translations: '+str(translations.encode('utf-8')))
            video = Translations(video,json.loads(translations))
            return video
            
        if len(seasons)>5:#more than 'null'
            #get season and episode from movie url
            url = hit.url()
            i = url.find('?')
            if i>0:
                url = url[i+1:]
            
            params = parse_qs(url)
            print("Episodes data: "+episodes)

            #video = Series(video,json.loads(seasons),ref)
            #check if current search hit is a specific season
            if ('season' in params) and ('episode' not in params):
                print('Returning video: '+str(hit))
                video = Season(hit.url(),hit.title(),hit.image(),json.loads(episodes),ref,int(params['season'][0]))
                return video

    #get script fetching data for POST requests
    script = getToken('<script src="(/assets/video-[^"]+?.js)">',html)
    script_host = getToken('(https://[^"]+?)/',iframe)

    print('fetching script from: '+script_host+script)
    request = Request(script_host+script, headers=headers)
    response = urlopen(request)
    html = response.read()
    #print(html)
    
    e = getToken('var e="([^"]+?)"',html)
    d = getToken('\["{}"\]="([^"]+?)"'.format(window_data),html)
    n = getToken('navigator.userAgent},n="([^"]+?)"',html)

    print('window_data:{},mw_pid:{},p_domain_id:{},video_token:{},e:{},n:{},d:{}'.format(window_data,mw_pid,p_domain_id,video_token,e,n,d))
    q = get_chiper(int(mw_pid),int(p_domain_id),video_token,e,n,d,agent)
    print(q)
    
    url = "http://" + host + "/vs"
    print('Requesting manifests: '+url)
    post_fields = {'q': q}

    headers = {
               'User-Agent':agent,
               'X-Requested-With': 'XMLHttpRequest',
               'Host':host,
               'Referer': iframe,
               'DNT':1,
               'Cache-Control':'no-cache'}

    request = Request(url, urlencode(post_fields).encode(), headers=headers)
    response = urlopen(request)
    mans = json.loads(response.read().decode())#response.headers.get_content_charset()))

    print(mans['m3u8'])

    headers = {
               #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
               'User-Agent':agent,
               'X-Requested-With': 'XMLHttpRequest',
               #'Cookie': 'quality=720',
               'Referer': iframe,
               'Connection':'keep-alive',
               'Accept':'*/*',
               'Accept-Language':'en-US,en;q=0.7,ru;q=0.3',
               'Accept-Encoding':'gzip, deflate',
               'Host':host,
               'DNT':1}

    # if (mans['mans']['manifest_f4m'] != None):
    #    request = Request(mans['mans']['manifest_f4m'], headers=headers)
    #    html = urlopen(request).read().decode()
    #    print(html)

    request = Request(mans['m3u8'], headers=headers)
    response = urlopen(request)
    html = response.read().decode()#response.headers.get_content_charset())
    print(html)
    stream = re.compile('[\S\s]+(http[s]?://[^"]+)').findall(html)[0][:-12]

    print('Stream to play: '+stream)

    #request = Request(stream, headers=headers)
    #html = urlopen(request).read().decode()
    #print(html)
    
    video._url = stream
    return video


