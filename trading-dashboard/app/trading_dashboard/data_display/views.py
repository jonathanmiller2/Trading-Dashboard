from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from datetime import datetime, timedelta
import requests, json

from trading_dashboard.data_display.models import Randseries


def index(request):
    return render(request, 'index.html')

def get_newest_val(request):
    data = serializers.serialize('json', Randseries.objects.order_by('-timestamp')[:1])
    return HttpResponse(data)

def get_historical_vals(request):
    period = int(request.GET['period'])
    query = Randseries.objects.filter(timestamp__lte=datetime.now(), timestamp__gt=datetime.now()-timedelta(hours=period)).order_by('timestamp')
    data = serializers.serialize('json', query)
    return HttpResponse(data)