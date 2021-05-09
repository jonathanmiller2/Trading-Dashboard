from django.urls import path

import trading_dashboard.asset_tracking.views

urlpatterns = [
    path('', trading_dashboard.asset_tracking.views.index),
]