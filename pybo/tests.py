import requests

url = "15.165.109.114"

def listAPI(n, so, kw):
    URL = "http://"+url+":9200/seoul_sample/_search?size="+str(n)

    if so == 'recent':
        URL += '&sort=Date:desc'
    else:
        URL += '&sort=Category.keyword:asc'

    if kw:
        URL += ('&q='+kw)

    data = requests.get(URL).json()['hits']['hits']
    return data

