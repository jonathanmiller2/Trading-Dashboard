from django.urls import path

import trading_dashboard.algo_tracking.views

urlpatterns = [
    path('', trading_dashboard.algo_tracking.views.index),
    path('add_algo', trading_dashboard.algo_tracking.views.add_algo),
    path('remove_algo', trading_dashboard.algo_tracking.views.remove_algo),
    path('trades_on', trading_dashboard.algo_tracking.views.trades_on),
    path('add_trade_on', trading_dashboard.algo_tracking.views.add_trade_on),
    path('remove_trade_on', trading_dashboard.algo_tracking.views.remove_trade_on),
]