from django.urls import path

import trading_dashboard.algo_tracking.views

urlpatterns = [
    path('', trading_dashboard.algo_tracking.views.index),
    path('trades_on', trading_dashboard.algo_tracking.views.trades_on),
    path('add_trade_on', trading_dashboard.algo_tracking.views.add_trade_on),
    path('remove_trade_on', trading_dashboard.algo_tracking.views.remove_trade_on),
]