from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
  path('', AccountViews.vendorDashboard, name='vendor'),
  path('profile/', views.vProfile, name='vProfile'),
  path('menu-builder/', views.menuBuilder, name='menu-builder'),
  path('menu-builder/category/<int:pk>/', views.foodItemByCat, name='foodItemByCat'),

  #category CRUD
  path('menu-builder/category/add', views.addCat, name='addCat'),
  path('menu-builder/category/edit/<int:pk>', views.edit_category, name='edit_category'),
  path('menu-builder/category/delete/<int:pk>', views.delete_category, name='delete_category'),

  #food CRUD
  path('menu-builder/food/add', views.add_food, name='add_food'),
  path('menu-builder/food/edit/<int:pk>', views.edit_food, name='edit_food'),
  path('menu-builder/food/delete/<int:pk>', views.delete_food, name='delete_food'),

]
