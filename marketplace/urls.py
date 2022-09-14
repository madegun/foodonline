from django.urls import path
from . import views


urlpatterns = [
  path('', views.marketplace, name='marketplace'),
  path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

  #add to cart URL
  path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),

  #decrease cart URL
  path('decrease_cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),
]
