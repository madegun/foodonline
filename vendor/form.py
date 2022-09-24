from django import forms

from accounts.validators import validation_image
from .models import Vendor, OpeningHour

class VendorForm(forms.ModelForm):
  vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info rounded'}),validators=[validation_image])
  class Meta:
    model = Vendor
    fields=['vendor_name','vendor_license']


class OpeningHourForm(forms.ModelForm):
  class Meta:
    model = OpeningHour
    fields=['day', 'from_hour', 'to_hour', 'is_closed']


