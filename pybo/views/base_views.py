import csv
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from ..models import Question
from xml.etree.ElementTree import fromstring, ElementTree
from elasticsearch import Elasticsearch, helpers
import jamotools
import urllib.request
import json
import requests
from pathlib import Path

url = "52.78.99.246"
index = "demo_data"

def covid19_data():
    seoul = {"JONGNOADD":"종로구", "JUNGGUADD":"중구", "YONGSANADD":"용산구", "SEONGDONGADD":"성동구", "GWANGJINADD":"광진구", "DDMADD":"동대문구", "JUNGNANGADD":"중랑구", "SEONGBUKADD":"성북구", "GANGBUKADD":"강북구", "DOBONGADD":"도봉구", "NOWONADD":"노원구", "EPADD":"은평구", "SDMADD":"서대문구", "MAPOADD":"마포구", "YANGCHEONADD":"양천구", "GANGSEOADD":"강서구", "GUROADD":"구로구", "GEUMCHEONADD":"금천구", "YDPADD":"영등포구", "DONGJAKADD":"동작구", "GWANAKADD":"관악구", "SEOCHOADD":"서초구", "GANGNAMADD":"강남구", "SONGPAADD":"송파구", "GANGDONGADD":"강동구", "ETCADD":"기타"}
    covid = {}

    url = 'http://openapi.seoul.go.kr:8088/547171685163686f35324270474f6e/xml/TbCorona19CountStatusJCG/1/1/'
    response = urllib.request.urlopen(url)
    xml_str = response.read().decode('utf-8')

    tree = ElementTree(fromstring(xml_str))
    root = tree.getroot()

    for row in root.iter("row"):
        for r in row:
            if r.tag in seoul:
                covid[seoul[r.tag]] = int(r.text)
    return covid

def date():
    for i in range(100):
        today = datetime.today() - timedelta(i)
        date = today
        url = 'http://openapi.seoul.go.kr:8088/547171685163686f35324270474f6e/xml/CardSubwayStatsNew/1/600/'+date.strftime("%Y%m%d")

        response = urllib.request.urlopen(url)
        xml_str = response.read().decode('utf-8')
        tree = ElementTree(fromstring(xml_str))
        root = tree.getroot()

        for row in root.iter("MESSAGE"):
            if row.text == '정상 처리되었습니다':
                return date

def station_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    f = open(str(BASE_DIR)+'/db/information.csv', 'r', encoding='cp949')
    rdr = csv.reader(f)

    info = {}
    data = []

    for line in rdr:
        data.append(line)
    f.close()

    for d in data:
        station = d[2].split()

        if station[0] == '서울특별시':
            info[d[1]] = station[1]

    return info

def subway_data():
    BASE_DIR = Path(__file__).resolve().parent.parent

    f = open(str(BASE_DIR)+'/db/subway.csv', 'r', encoding='utf-8-sig')
    rdr = csv.reader(f)

    data = []

    for line in rdr:
        data.append(line)
    f.close()
    return data

def update_station():
    url = 'http://openapi.seoul.go.kr:8088/547171685163686f35324270474f6e/xml/CardSubwayStatsNew/1/600/'+date().strftime("%Y%m%d")
    es = Elasticsearch(['http://15.165.109.114:9200/'])

    data = subway_data()
    staion_info = station_data()
    covid = covid19_data()
    docs = []
    stations = []

    response = urllib.request.urlopen(url)
    xml_str = response.read().decode('utf-8')
    tree = ElementTree(fromstring(xml_str))
    root = tree.getroot()

    for row in data:
        station = row[1]
        place_x = row[3]
        place_y = row[4]

        if place_x != '' and place_y != '':
            place_x = float(place_x)
            place_y = float(place_y)
            info = {"station": station, "place_x": place_x, "place_y": place_y}
            stations.append(info)

    for row in root.iter("row"):
        station = row.find('SUB_STA_NM').text

        for info in stations:
            if station == info['station']:
                if station in staion_info:
                    line = row.find('LINE_NUM').text
                    ride = int(row.find('RIDE_PASGR_NUM').text)
                    alight = int(row.find('ALIGHT_PASGR_NUM').text)
                    move = ride + alight
                    place_x = info['place_x']
                    place_y = info['place_y']
                    region = staion_info[station]

                    doc = {
                        "_index": "station-covid19",
                        "_id": station,
                        "_source": {
                            "line": line,
                            "region": region,
                            "confirmed": covid[region],
                            "station": station,
                            "location": {
                                "lat": place_x,
                                "lon": place_y
                            },
                            "ride": ride,
                            "alight": alight,
                            "move": move
                        }
                    }
                    docs.append(doc)

    res = helpers.bulk(es, docs)
    print("END")

def update_covid():
    es = Elasticsearch(['http://3.34.219.4:9200/'])
    docs = []

    url = 'http://openapi.seoul.go.kr:8088/547171685163686f35324270474f6e/xml/TbCorona19CountStatus/1/400/'
    response = urllib.request.urlopen(url)
    xml_str = response.read().decode('utf-8')

    tree = ElementTree(fromstring(xml_str))
    root = tree.getroot()

    for row in root.iter("row"):
        date = row.find('S_DT').text
        today = int(row.find('N_HJ').text)
        confirmed = int(row.find('T_HJ').text)
        death = int(row.find('DEATH').text)
        recover = int(row.find('RECOVER').text)
        doc = {
            "_index": "covid19_logstash",
            "_id": date,
            "_source": {
                "date": date,
                "today": today,
                "confirmed": confirmed,
                "death": death,
                "recover": recover
            }
        }
        docs.append(doc)
    res = helpers.bulk(es, docs)
    print("END")


def home(request):
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준
    context = {'page': page, 'kw': kw, 'so': so}

    return render(request, "home.html", context)

def search_error(query):
    url = "http://3.34.219.4:9200/seoul_sample/_search"
    headers = {'Content-Type':'application/json'}

    query = jamotools.split_syllables(query)
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
    return jamotools.join_jamos(word)

def listAPI(n, so, kw):
    URL = "http://" + url +":9200/" + index + "/_search?size=" + str(n)

    if so == 'recent':
        URL += '&sort=ModDate:desc'
    else:
        URL += '&sort=Category.keyword:asc'

    if kw:
        URL += ('&q='+kw)

    data = requests.get(URL).json()['hits']['hits']
    list = []
    for d in data:
        a = d['_source']
        a['id'] = d['_id']
        list.append(a)
    return list

def detailAPI(id):
    URL = "http://" + url +":9200/" + index + "/_doc/" + id
    data = requests.get(URL).json()['_source']
    return data

def searchAPI(query):
    URL = "http://" + url + ":9200/" + index + "/_search?size=1000&q=" + query
    data = requests.get(URL).json()['hits']['hits']
    list = []
    for d in data:
        a = d['_source']
        a['id'] = d['_id']
        list.append(a)
    return list

def list(request):
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준
    reword = ''

    data_list = listAPI(10000, so, kw)

    if not data_list:
        reword = search_error(kw)
        data_list = listAPI(10000, so, search_error(kw))

    paginator = Paginator(data_list, 5)
    page_obj = paginator.get_page(page)
    length = format(len(data_list), ',')
    context = {"data_list":page_obj, 'page': page, 'kw': kw, 'so': so, 'reword':reword, 'length':length}

    return render(request, 'pybo/list.html', context)

def list_detail(request, id):
    data = detailAPI(id)
    context = {"data":data}
    return render(request, 'pybo/detail.html', context)

def category(request, category):
    page = request.GET.get('page', '1')  # 페이지
    kw = "Category:" + category
    so = request.GET.get('so', 'recent')  # 정렬기준

    data_list = listAPI(10000, so, kw)

    paginator = Paginator(data_list, 10)
    page_obj = paginator.get_page(page)
    context = {"data_list": page_obj, 'page': page, 'kw': kw, 'so': so}

    return render(request, 'pybo/list.html', context)

def seoul(request):
    update_station()
    URL = "http://" + url + ":9200/covid19_logstash/_search?sort=date:desc"
    data = requests.get(URL).json()['hits']['hits'][0]
    date1 = data['_source']['date']
    date2 = date().strftime("%Y.%m.%d.%H")
    context = {"date1": date1, "date2": date2}
    return render(request, 'pybo/seoul.html', context)

def subway(request):
    return render(request, 'pybo/subway.html')

def bike(request):
    return render(request, 'pybo/bike.html')

def covid19(request):
    update_covid()
    URL = "http://"+url+":9200/covid19_logstash/_search?sort=date:desc"
    data = requests.get(URL).json()['hits']['hits'][0]
    date = data['_source']['date']
    context = {"date":date, "url":url}
    return render(request, 'pybo/covid19.html', context)

# pybo 목록 출력
def indexs(request):
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어

    so = request.GET.get('so', 'recent')  # 정렬기준

    # 정렬
    if so == 'recommend':
        question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:  # recent
        question_list = Question.objects.order_by('-create_date')

    # 검색
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}
    return render(request, 'pybo/question_list.html', context)

# pybo 내용 출력
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)