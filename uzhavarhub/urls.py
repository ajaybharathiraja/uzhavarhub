from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('farmer/', include('farmer.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('reviews/', include('reviews.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('ai/', include('ai_services.urls')),
    path('', include('core.urls')),
]
