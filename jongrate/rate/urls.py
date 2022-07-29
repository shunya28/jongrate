from django.urls import path
from . import views

app_name = 'rate'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('data/', views.Data.as_view(), name='data'),
    path('rate/', views.Rate.as_view(), name='rate'),
    path('settings/', views.Settings.as_view(), name='settings'),
]
