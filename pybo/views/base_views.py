from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from ..models import Question
import urllib.request
from xml.etree.ElementTree import fromstring, ElementTree
from elasticsearch import Elasticsearch, helpers
import requests

url = "52.78.99.246"
index = "seoul_sample"

def update():
    es = Elasticsearch(['http://3.34.219.4:9200/'])

    seoul = {"JONGNO": "종로구", "JUNGGU": "중구", "YONGSAN": "용산구", "SEONGDONG": "성동구", "GWANGJIN": "광진구", "DDM": "동대문구",
             "JUNGNANG": "중랑구", "SEONGBUK": "성북구", "GANGBUK": "강북구", "DOBONG": "도봉구", "NOWON": "노원구", "EP": "은평구",
             "SDM": "서대문구", "MAPO": "마포구", "YANGCHEON": "양천구", "GANGSEO": "강서구", "GURO": "구로구", "GEUMCHEON": "금천구",
             "YDP": "영등포구", "DONGJAK": "동작구", "GWANAK": "관악구", "SEOCHO": "서초구", "GANGNAM": "강남구", "SONGPA": "송파구",
             "GANGDONG": "강동구", "ETC": "기타"}
    seoul_add = {"JONGNOADD": "종로구", "JUNGGUADD": "중구", "YONGSANADD": "용산구", "SEONGDONGADD": "성동구",
                 "GWANGJINADD": "광진구", "DDMADD": "동대문구", "JUNGNANGADD": "중랑구", "SEONGBUKADD": "성북구",
                 "GANGBUKADD": "강북구", "DOBONGADD": "도봉구", "NOWONADD": "노원구", "EPADD": "은평구", "SDMADD": "서대문구",
                 "MAPOADD": "마포구", "YANGCHEONADD": "양천구", "GANGSEOADD": "강서구", "GUROADD": "구로구", "GEUMCHEONADD": "금천구",
                 "YDPADD": "영등포구", "DONGJAKADD": "동작구", "GWANAKADD": "관악구", "SEOCHOADD": "서초구", "GANGNAMADD": "강남구",
                 "SONGPAADD": "송파구", "GANGDONGADD": "강동구", "ETCADD": "기타"}

    covid = []
    covid_add = []
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

    url = 'http://openapi.seoul.go.kr:8088/547171685163686f35324270474f6e/xml/TbCorona19CountStatusJCG/1/1/'
    response = urllib.request.urlopen(url)
    xml_str = response.read().decode('utf-8')

    tree = ElementTree(fromstring(xml_str))
    root = tree.getroot()

    for row in root.iter("row"):
        for r in row:
            if r.tag in seoul:
                region = seoul[r.tag]

                doc = {
                    "_index": "seoul-covid19",
                    "_id": region,
                    "_source": {
                        "region": region,
                        "confirmed": int(r.text),
                    }
                }
                covid.append(doc)
            elif r.tag in seoul_add:
                region = seoul_add[r.tag]
                doc = {
                    "_index": "seoul-covid19-add",
                    "_id": r.tag,
                    "_source": {
                        "region": region,
                        "confirmed": int(r.text),
                    }
                }
                covid_add.append(doc)


    res = helpers.bulk(es, docs)
    res = helpers.bulk(es, covid)
    res = helpers.bulk(es, covid_add)
    print("END")


def home(request):
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준
    context = {'page': page, 'kw': kw, 'so': so}

    return render(request, "home.html", context)


def listAPI(n, so, kw):
    URL = "http://" + url +":9200/" + index + "/_search?size=" + str(n)

#  if so == 'recent':
#        URL += '&sort=ModDate:desc'
#    else:
#        URL += '&sort=Category.keyword:asc'

    if kw:
        URL += ('&q='+kw)

    data = requests.get(URL).json()['hits']['hits']
    list = []
    for d in data:
        a = d['_source']
        a['id'] = d['_id']
        list.append(a)
    list = list[1:]
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

    data_list = listAPI(10000, so, kw)

    paginator = Paginator(data_list, 5)
    page_obj = paginator.get_page(page)
    context = {"data_list":page_obj, 'page': page, 'kw': kw, 'so': so}

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
    return render(request, 'pybo/seoul.html')

def subway(request):
    return render(request, 'pybo/subway.html')

def bike(request):
    return render(request, 'pybo/bike.html')

def covid19(request):
    update()
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