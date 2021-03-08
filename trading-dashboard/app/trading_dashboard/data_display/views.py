from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
import requests, json

from trading_dashboard.data_display.models import Randseries


def index(request):
    return render(request, 'index.html')

def getval(request):
    data = serializers.serialize('json', Randseries.objects.order_by('-timestamp')[:1])

    return HttpResponse(data)