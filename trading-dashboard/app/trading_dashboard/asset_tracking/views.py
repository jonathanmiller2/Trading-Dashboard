from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.db import IntegrityError, connection
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import Asset, ExchangeRate

import json
<<<<<<< HEAD
import pandas as pd
=======
>>>>>>> a0799a6f0cc5eb5bd9216e872f1b0e7305042370

@login_required
def index(request):
    data = {}
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)

@login_required
def track_asset(request):
    data = {}

    if request.method == 'POST':
        try:
            Asset.objects.create(symbol=request.POST['symbol'], source=request.POST['source'])
        except IntegrityError as e:
            data['error'] = 'That symbol is already being tracked.'
    
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)

@login_required
def untrack_asset(request):
    data = {}

    if request.method == 'POST':
        Asset.objects.filter(symbol__exact=request.POST['symbol']).delete()
    
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)

@login_required
def details(request):
    return render(request, 'asset_tracking/details.html')

def get_rate_record(request):
    #TODO: Group averages to reduce network wait time?
    period_hours = int(request.GET['period'])
    symbol = request.GET['asset']

    asset = Asset.objects.get(symbol=symbol)
    USD = Asset.objects.get(symbol='USD')

    query = ExchangeRate.objects.filter(timestamp__lte=datetime.now(), timestamp__gt=datetime.now()-timedelta(hours=period_hours), from_asset=USD, to_asset=asset).order_by('timestamp')

    if query.count() == 0:
        return HttpResponse('[]')

    df = pd.DataFrame.from_records(list(query.values('timestamp', 'rate')), columns=['timestamp', 'rate'], coerce_float=True)

    if period_hours >= 1000:
        #Group by day
        groupkey=pd.to_datetime(df.timestamp.dt.strftime('%Y-%m-%d'))
        res = df.groupby(groupkey).agg({'timestamp':'last', 'rate':'mean'}).to_json(date_format='iso', orient="values")

    elif period_hours >= 100:
        #Group by hour
        groupkey=pd.to_datetime(df.timestamp.dt.strftime('%Y-%m-%d %H'))
        res = df.groupby(groupkey).agg({'timestamp':'last', 'rate':'mean'}).to_json(date_format='iso', orient="values")
    
    else:
        res = df.to_json(date_format='iso', orient="values")

    return HttpResponse(res)
