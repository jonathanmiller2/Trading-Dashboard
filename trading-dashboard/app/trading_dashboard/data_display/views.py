from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from datetime import datetime, timedelta
import requests, json
from django.apps import apps


def index(request):
    return render(request, 'index.html')

def get_newest_val(request):
    ticker = request.GET['ticker']
    
    ticker_model = apps.get_model(app_label='data_display', model_name='Ticker_'+ticker)
    data = serializers.serialize('json', ticker_model.objects.order_by('-timestamp')[:1])
    return HttpResponse(data)

def get_historical_vals(request):
    period = int(request.GET['period'])
    ticker = request.GET['ticker']

    ticker_model = apps.get_model(app_label='data_display', model_name='Ticker_'+ticker)
    query = ticker_model.objects.filter(timestamp__lte=datetime.now(), timestamp__gt=datetime.now()-timedelta(hours=period)).order_by('timestamp')
    data = serializers.serialize('json', query)
    return HttpResponse(data)