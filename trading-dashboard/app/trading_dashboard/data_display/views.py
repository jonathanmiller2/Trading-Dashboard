from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from datetime import datetime, timedelta
import requests, json


def index(request):
    return render(request, 'data_display/index.html')

def get_historical_vals(request):

    #TODO: https://stackoverflow.com/questions/30465013/django-group-by-hour

    #period = int(request.GET['period'])
    #symbol = request.GET['symbol']
#
    #query = Ticker.objects.filter(symbol=symbol, timestamp__lte=datetime.now(), timestamp__gt=datetime.now()-timedelta(hours=period)).order_by('timestamp')
    #data = serializers.serialize('json', query)
    #return HttpResponse(data)

    return {}