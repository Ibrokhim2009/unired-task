from django.urls import path
from core.views import jsonrpc_view

urlpatterns = [
    path('api/', jsonrpc_view, name='jsonrpc'),
]