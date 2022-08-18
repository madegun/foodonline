from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin



# Register your models here.
class CustomuserAdmin(UserAdmin):
  list_display = ('email','username', 'last_name', 'role', 'is_active')
  ordering = ('-date_joined',)
  filter_horizontal = ()
  list_filter = ()
  fieldsets = ()
  
admin.site.register(User, CustomuserAdmin)
admin.site.register(UserProfile)


