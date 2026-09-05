from django.urls import path

app_name = 'marketplace'

from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('farmers/', views.farmer_list, name='farmer_list'),
]
