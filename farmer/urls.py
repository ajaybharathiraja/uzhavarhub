from django.urls import path
from . import views

app_name = 'farmer'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('orders/', views.order_management, name='orders'),
    path('orders/update/<int:item_id>/', views.update_order_status, name='update_status'),
    path('earnings/', views.farmer_earnings, name='earnings'),
    path('settings/', views.farmer_settings, name='settings'),
]
