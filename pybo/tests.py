import requests

URL = "http://3.39.23.241:9200/public_metadata/_search?size=10000"
data = requests.get(URL).json()['hits']['hits']
list = []
for d in data:
    list.append(d['_source'])
