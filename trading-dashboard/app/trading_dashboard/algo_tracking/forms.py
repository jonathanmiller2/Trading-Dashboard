from django import forms
from django.forms.models import ModelChoiceField
from .models import Algo
from trading_dashboard.asset_tracking.models import Asset

class AddsTradesOnForm(forms.Form):
    algo = ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control mr-2'}), 
                            queryset=Algo.objects.all().values_list("name", flat=True))

    asset = ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control mr-2'}), 
                            queryset=Asset.objects.all().exclude(symbol__exact="USD").values_list("symbol", flat=True))