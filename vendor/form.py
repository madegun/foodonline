from django import forms

from accounts.validators import validation_image
from .models import Vendor

class VendorForm(forms.ModelForm):
  vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info rounded'}),validators=[validation_image])
  class Meta:
    model = Vendor
    fields=['vendor_name','vendor_license']


