from django.urls import path
from . import views
from accounts import views as AccountViews


urlpatterns = [
  path('', AccountViews.vendorDashboard, name='customers'),
  path('profile/', views.cusProfile, name='cusProfile')
]
