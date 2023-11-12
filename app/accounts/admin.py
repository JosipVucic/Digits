from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

# Register your models here.
# Custom user model registered in case off future changes
admin.site.register(User, UserAdmin)
