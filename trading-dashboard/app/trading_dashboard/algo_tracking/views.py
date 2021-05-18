from decimal import *
import math
from django.utils import timezone
from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Algo, TradesOn, Asset, Balance


@login_required
def index(request):
    data = {}
    data['algos'] = Algo.objects.all()

    return render(request, 'algo_tracking/index.html', context=data)


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


def remove_algo(request):
    data = {}

    if request.method == 'POST':
        Algo.objects.filter(name__exact=request.POST['algo_name']).delete()
    
    data['algos'] = Algo.objects.all()

    return render(request, 'algo_tracking/index.html', context=data)


def trades_on(request):
    data = {}
    data['trades_on'] = TradesOn.objects.all()
    data['algo_list'] = Algo.objects.all()
    data['asset_list'] = Asset.objects.all().exclude(symbol__exact="USD")

    return render(request, 'algo_tracking/trades_on.html', context=data)

    
def add_trade_on(request):
    data = {}

    if request.method == 'POST':
        algo = Algo.objects.get(name__exact=request.POST['algo'])
        asset = Asset.objects.get(symbol__exact=request.POST['asset'])

        try:
            TradesOn.objects.create(algo=algo, asset=asset)
            Balance.objects.create(timestamp=timezone.now(), algo=algo, asset=asset, balance=0)
        except IntegrityError as e:
            data['error'] = 'That trade is already being tracked.'
    
    data['trades_on'] = TradesOn.objects.all()
    data['algo_list'] = Algo.objects.all()
    data['asset_list'] = Asset.objects.all().exclude(symbol__exact="USD")

    return render(request, 'algo_tracking/trades_on.html', context=data)


def remove_trade_on(request):
    data = {}

    if request.method == 'POST':
        TradesOn.objects.filter(algo=request.POST['algo'], asset=request.POST['asset']).delete()
    
    data['trades_on'] = TradesOn.objects.all()
    data['algo_list'] = Algo.objects.all()
    data['asset_list'] = Asset.objects.all().exclude(symbol__exact="USD")

    return render(request, 'algo_tracking/trades_on.html', context=data)