from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile, FarmerProfile

admin.site.register(User, UserAdmin)
admin.site.register(CustomerProfile)
admin.site.register(FarmerProfile)
