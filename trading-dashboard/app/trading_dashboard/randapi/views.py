from django.shortcuts import render
from django.http import HttpResponse
import requests



def index(request):
    return render(request, 'index.html')

def getval(request):
    response = requests.get('https://randomapi.com/api/3c54fecc22a804fe5a8a8db54b6b50e7')
    val = response.json()
    return HttpResponse(val["results"][0]["val"])