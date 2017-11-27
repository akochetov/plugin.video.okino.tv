import urllib
try:
    from urllib.request import Request
except ImportError:
    from urllib2 import Request
from urllib import urlencode
from urllib2 import urlopen
import re
import json

video_quality = ['1080', '720', '640', '480', '320', '240']
url_search = 'http://okino.tv'
mw_key = '1ffd4aa558cc51f5a9fc6888e7bc5cb4'

#search
def do_search(keyword):
    hits = []
    post_fields = {'do': 'search',
                   'subaction': 'search',
                   'story': keyword.encode('cp1251')}

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    
    request = Request(url_search, urlencode(post_fields).encode(),headers)
    html = urlopen(request).read().decode('cp1251')

    hrefs=re.compile('<a class="m-link[\S\s]+?href="([^"]+?)"').findall(html)
    names=re.compile('<div class="movie">[\S\s]+?<div class="m-title">([^"]+?)</div>').findall(html)
    pics=re.compile('<div class="movie">[\S\s]+?<img src="([^"]+?)"').findall(html)

    for i,href in enumerate(hrefs):
        hits.append([hrefs[i],names[i],pics[i]])

    return(hits)

def do_getvideo(movie_page_url):
    # getting movie page
    request = Request(movie_page_url)
    html = urlopen(request).read().decode('cp1251')
    iframe = re.compile('<iframe src="([^"]+?)"').findall(html)[0]

    # getting movie player page
    url = iframe
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Referer': movie_page_url}
    request = Request(url, headers=headers)
    response = urlopen(request)
    html = response.read().decode()#response.headers.get_content_charset())

    #parse out parameters
    video_id = re.compile('video/([^"]+?)/iframe').findall(iframe)[0]
    video_token = re.compile('video_token: \'([^\']+?)\'').findall(html)[0]
    user_token = re.compile('user_token: \'([^"]+?)\'').findall(html)[0]
    mw_pid = re.compile('partner_id: ([^"]+?),').findall(html)[0]
    p_domain_id = re.compile('domain_id: ([^"]+?),').findall(html)[0]
    host = re.compile('host: \'([^"]+?)\'').findall(html)[0]
    proto = re.compile('proto: \'([^"]+?)\'').findall(html)[0]
    port = re.compile('port: ([^"]+?),').findall(html)[0]

    # getting mp4
    url = proto + host + ":" + port + "/manifests/video/" + video_id + "/all"
    post_fields = {'mw_key': mw_key,
                   'mw_pid': mw_pid,
                   'ad_attr': '0',
                   'p_domain_id': p_domain_id,
                   'iframe_version': '2.1'}

    headers = {'X-Access-Level': user_token,
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'}

    request = Request(url, urlencode(post_fields).encode(), headers=headers)
    response = urlopen(request)
    mans = json.loads(response.read().decode())#response.headers.get_content_charset()))

    print(mans['mans']['manifest_f4m'])
    print(mans['mans']['manifest_m3u8'])
    print(mans['mans']['manifest_mp4'])

    headers = {'Referer': iframe,
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'}

    # if (mans['mans']['manifest_f4m'] != None):
    #    request = Request(mans['mans']['manifest_f4m'], headers=headers)
    #    html = urlopen(request).read().decode()
    #    print(html)

    stream = ''
    if (mans['mans']['manifest_mp4'] != None):
        request = Request(mans['mans']['manifest_mp4'], headers=headers)
        response = urlopen(request)
        html = response.read().decode()#response.headers.get_content_charset())
        stream_json = json.loads(html)

        for q in video_quality:
            if q in stream_json:
                stream = stream_json[q]
                break
    else:
        request = Request(mans['mans']['manifest_m3u8'], headers=headers)
        response = urlopen(request)
        html = response.read().decode()#response.headers.get_content_charset())
        print(html)
        stream = re.compile('[\S\s]+(http://[^"]+)').findall(html)[0]

        # request = Request(stream_pl, headers=headers)
        # html = urlopen(request).read().decode()
        # print(html)
    return(stream)


