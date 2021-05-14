from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from trading_dashboard.asset_tracking.models import Asset

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
        Asset.objects.get(symbol__exact=request.POST['symbol']).delete()
    
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)