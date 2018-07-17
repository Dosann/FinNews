
import requests
from lxml import etree
import json

def GetProxies(to_file = True):
    response = requests.get('https://free-proxy-list.net/')
    html = etree.HTML(response.text)
    tbody = html.xpath('//tbody')[0]
    proxies = []
    for tr in tbody:
        proxies.append('%s:%s'%(tr[0].text, tr[1].text))

    if to_file:
        with open('./finnews_spider/proxies.json', 'wt') as f:
            f.write(json.dumps(proxies))
    else:
        return proxies