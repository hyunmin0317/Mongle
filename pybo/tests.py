import requests
import json
from jamo import h2j, j2hcj
from unicode import join_jamos

def search_error(query):
    url = "http://3.34.219.4:9200/seoul_sample/_search"
    headers = {'Content-Type':'application/json'}

    query = j2hcj(h2j(query))
    data = {
        "suggest": {
            "suggest": {
                "text": query,
                "term": {
                    "field": "Title.spell"
                }
            }
        }
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    word = response.json()['suggest']['suggest'][0]['options'][0]['text']
    return join_jamos(word)

print(search_error('시울'))