from django.urls import path

import trading_dashboard.randapi.views

urlpatterns = [
    path('', trading_dashboard.randapi.views.index),
    path('getval', trading_dashboard.randapi.views.getval)
]