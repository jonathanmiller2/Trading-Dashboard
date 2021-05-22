from django.urls import path

import trading_dashboard.asset_tracking.views

urlpatterns = [
    path('', trading_dashboard.asset_tracking.views.index),
    path('track_asset', trading_dashboard.asset_tracking.views.track_asset),
    path('untrack_asset', trading_dashboard.asset_tracking.views.untrack_asset),
    path('details', trading_dashboard.asset_tracking.views.details),
    path('get_rate_record', trading_dashboard.asset_tracking.views.get_rate_record),
]