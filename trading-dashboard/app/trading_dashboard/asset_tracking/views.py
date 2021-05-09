from django.shortcuts import render
from django.http import HttpResponse
from trading_dashboard.asset_tracking.models import Asset


def index(request):
    data = {}
    data['assets'] = Asset.objects.all()

    return render(request, 'asset_tracking/index.html', context=data)
