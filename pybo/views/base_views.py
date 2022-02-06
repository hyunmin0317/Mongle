from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from ..models import Question
import requests

url = "15.164.94.101"

def listAPI(n, so, kw):
    URL = "http://"+url+":9200/public_metadata/_search?size="+str(n)

    if so == 'recent':
        URL += '&sort=Date:desc'
    else:
        URL += '&sort=Title.keyword:desc'

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
    URL = "http://"+url+":9200/public_metadata/_doc/"+id
    data = requests.get(URL).json()['_source']
    return data

def searchAPI(query):
    URL = "http://" + url + ":9200/public_metadata/_search?size=1000&q="+query
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

    # 검색
    # if kw:
    #     data_list = searchAPI(kw)

    paginator = Paginator(data_list, 10)
    page_obj = paginator.get_page(page)
    context = {"data_list":page_obj, 'page': page, 'kw': kw, 'so': so}

    return render(request, 'pybo/list.html', context)

def list_detail(request, id):
    data = detailAPI(id)
    context = {"data":data}
    return render(request, 'pybo/detail.html', context)


# pybo 목록 출력
def index(request):
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