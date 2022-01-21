from django.shortcuts import render

def seoul(request):
    return render(request, 'pybo/seoul.html')

def covid19(request):
    return render(request, 'pybo/covid19.html')