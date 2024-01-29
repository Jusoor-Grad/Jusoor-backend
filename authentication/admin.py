from re import U
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User



# Register your models here.
@admin.register(User)
class Admin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Personal info', {'fields': ('image',)}),
    )
    
