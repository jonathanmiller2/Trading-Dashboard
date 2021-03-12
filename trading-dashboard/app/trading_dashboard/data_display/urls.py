from django.urls import path

import trading_dashboard.data_display.views

urlpatterns = [
    path('', trading_dashboard.data_display.views.index),
    path('get_newest_val', trading_dashboard.data_display.views.get_newest_val),
    path('get_historical_vals', trading_dashboard.data_display.views.get_historical_vals)
]