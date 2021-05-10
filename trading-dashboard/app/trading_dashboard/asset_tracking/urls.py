from django.urls import path

import trading_dashboard.asset_tracking.views

urlpatterns = [
    path('', trading_dashboard.asset_tracking.views.index),
    path('track_asset', trading_dashboard.asset_tracking.views.track_asset),
    path('untrack_asset', trading_dashboard.asset_tracking.views.untrack_asset),
]