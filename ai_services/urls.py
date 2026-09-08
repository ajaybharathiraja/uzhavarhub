from django.urls import path
from . import views

app_name = 'ai_services'

urlpatterns = [
    path('api/integrated-strategy/', views.integrated_strategy_api, name='integrated_strategy_api'),
]
