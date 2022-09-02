from django.shortcuts import render, get_object_or_404, redirect
from accounts.form import UserProfileForm
from django.contrib import messages

from accounts.models import UserProfile
from vendor.models import Vendor
from .form import VendorForm

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
# Create your views here.
def vProfile(request):
  profile = get_object_or_404(UserProfile, user=request.user)
  vendor = get_object_or_404(Vendor, user=request.user)

  #cek jika request method adalah POSt
  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
    vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
    if profile_form.is_valid() and vendor_form.is_valid():
      profile_form.save()
      vendor_form.save()
      messages.success(request, 'setting save updated')
      return redirect('vProfile')
    else:
      print(profile_form.errors)
      print(vendor_form.errors)
  else:
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)

  context = {
    'profile_form': profile_form,
    'vendor_form': vendor_form,
    'profile': profile,
    'vendor': vendor,
  }
  return render(request, 'vendor/vProfile.html', context)
