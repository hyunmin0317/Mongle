import requests

URL = "http://3.39.23.241:9200/public_metadata/_search?size=10000"
data = requests.get(URL).json()['hits']['hits']
list = []
for a in data:
    d = a['_source']
    d['id'] = a['_id']
    print(d)

