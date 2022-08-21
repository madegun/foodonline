from django.contrib import admin

from django.contrib import admin
from vendor.models import Vendor

class VendorAdmin(admin.ModelAdmin):
  list_display = ('user', 'vendor_name', 'is_approved', 'created_at')
  list_display_links = ('user', 'vendor_name')
  
  
# Register your models here.
admin.site.register(Vendor, VendorAdmin)
