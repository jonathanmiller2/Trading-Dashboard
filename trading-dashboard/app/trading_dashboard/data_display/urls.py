from django.urls import path

import trading_dashboard.data_display.views

urlpatterns = [
    path('', trading_dashboard.data_display.views.index),
    path('getval', trading_dashboard.data_display.views.getval)
]