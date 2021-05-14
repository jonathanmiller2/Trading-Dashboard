from django.urls import path, include

import trading_dashboard.users.views

urlpatterns = [
    path('', trading_dashboard.users.views.index),
]