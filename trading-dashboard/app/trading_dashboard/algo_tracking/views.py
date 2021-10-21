from decimal import *
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.db import IntegrityError, connection
from django.contrib.auth.decorators import login_required
from .models import Algo, TradesOn, Asset, Balance

import json
import pandas as pd

@login_required
def index(request):
    data = {}
    data['algos'] = Algo.objects.all()

    return render(request, 'algo_tracking/index.html', context=data)

@login_required
def add_algo(request):
    data = {}

    if request.method == 'POST':
        try:
            new_algo = Algo.objects.create(name=request.POST['algo_name'])
            USD = Asset.objects.get(symbol__iexact='USD')
            Balance.objects.create(timestamp=timezone.now(), algo=new_algo, asset=USD, balance=request.POST['algo_startvalue'])

        except IntegrityError as e:
            print(e)
            data['error'] = 'That trade is already being tracked.'

    data['algos'] = Algo.objects.all()

    return render(request, 'algo_tracking/index.html', context=data)

@login_required
def remove_algo(request):
    data = {}

    if request.method == 'POST':
        Algo.objects.filter(name__exact=request.POST['algo_name']).delete()
    
    data['algos'] = Algo.objects.all()

    return render(request, 'algo_tracking/index.html', context=data)

@login_required
def trades_on(request):
    data = {}
    data['trades_on'] = TradesOn.objects.all()
    data['algo_list'] = Algo.objects.all()
    data['asset_list'] = Asset.objects.all().exclude(symbol__exact="USD")

    return render(request, 'algo_tracking/trades_on.html', context=data)

@login_required
def add_trade_on(request):
    data = {}

    if request.method == 'POST':
        algo = Algo.objects.get(name__exact=request.POST['algo'])
        asset = Asset.objects.get(symbol__exact=request.POST['asset'])

        try:
            TradesOn.objects.create(algo=algo, asset=asset)
        except IntegrityError as e:
            data['error'] = 'That trade is already being tracked.'
    
    data['trades_on'] = TradesOn.objects.all()
    data['algo_list'] = Algo.objects.all()
    data['asset_list'] = Asset.objects.all().exclude(symbol__exact="USD")

    return render(request, 'algo_tracking/trades_on.html', context=data)

@login_required
def remove_trade_on(request):
    data = {}

    if request.method == 'POST':
        TradesOn.objects.filter(algo=request.POST['algo'], asset=request.POST['asset']).delete()
    
    data['trades_on'] = TradesOn.objects.all()
    data['algo_list'] = Algo.objects.all()
    data['asset_list'] = Asset.objects.all().exclude(symbol__exact="USD")

    return render(request, 'algo_tracking/trades_on.html', context=data)

@login_required
def details(request):
    return render(request, 'algo_tracking/details.html')

def get_balance_record(request):
    algo = request.GET['algo']
    period_hours = int(request.GET['period'])
    period_delta = request.GET['period'] + " hours"

    cursor = connection.cursor()
    cursor.callproc("get_total_balance", [algo, "USD", period_delta, 1])
    balances = cursor.fetchall()
    cursor.close()
    connection.close()

    if len(balances) == 0:
        return HttpResponse('[]')

    df = pd.DataFrame.from_records(balances, columns=['Time', 'Balance'], coerce_float=True)

    if period_hours >= 1000:
        #Group by day
        groupkey=pd.to_datetime(df.Time.dt.strftime('%Y-%m-%d'))
        res = df.groupby(groupkey).agg({'Time':'last', 'Balance':'mean'}).to_json(date_format='iso', orient="values")

    elif period_hours >= 100:
        #Group by hour
        groupkey=pd.to_datetime(df.Time.dt.strftime('%Y-%m-%d %H'))
        res = df.groupby(groupkey).agg({'Time':'last', 'Balance':'mean'}).to_json(date_format='iso', orient="values")
    
    else:
        res = df.to_json(date_format='iso', orient="values")

    return HttpResponse(res)

