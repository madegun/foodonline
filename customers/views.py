from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.form import UserInfoForm, UserProfileForm
from accounts.models import UserProfile


# Create your views here.
@login_required(login_url='login') #decorator cek user login
def cusProfile(request):
  profile = get_object_or_404(UserProfile, user=request.user)
  print(profile.profile_picture.url)
  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
    user_form = UserInfoForm(request.POST, instance=request.user)
    if profile_form.is_valid() and user_form.is_valid():
      profile_form.save()
      user_form.save()
      messages.success(request, 'profile berhasil di update')
      return redirect('cusProfile')
    else:
      print(profile_form.errors)
      print(user_form.errors)
  else:
    profile_form = UserProfileForm(instance=profile)
    user_form = UserInfoForm(instance=request.user)

  context = {
    'profile_form': profile_form,
    'user_form': user_form,
    'profile': profile,
  }
  return render(request, 'customers/cusProfile.html', context)
