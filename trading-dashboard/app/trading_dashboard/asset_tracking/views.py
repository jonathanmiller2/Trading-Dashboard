from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.db import IntegrityError, connection
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import Asset, ExchangeRate

import json

@login_required
def index(request):
    data = {}
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)


def track_asset(request):
    data = {}

    if request.method == 'POST':
        try:
            Asset.objects.create(symbol=request.POST['symbol'], source=request.POST['source'])
        except IntegrityError as e:
            data['error'] = 'That symbol is already being tracked.'
    
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)


def untrack_asset(request):
    data = {}

    if request.method == 'POST':
        Asset.objects.filter(symbol__exact=request.POST['symbol']).delete()
    
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)

def details(request):
    return render(request, 'asset_tracking/details.html')

def get_rate_record(request):
    #TODO: Group averages to reduce network wait time?
    period = int(request.GET['period'])
    symbol = request.GET['asset']

    asset = Asset.objects.get(symbol=symbol)
    USD = Asset.objects.get(symbol='USD')

    query = ExchangeRate.objects.filter(timestamp__lte=datetime.now(), timestamp__gt=datetime.now()-timedelta(hours=period), from_asset=USD, to_asset=asset).order_by('timestamp')
    data = serializers.serialize('json', query)
    return HttpResponse(data)