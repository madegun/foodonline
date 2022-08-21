from django.shortcuts import render, redirect

from vendor.form import VendorForm
from .form import UserForm
from .models import User, UserProfile
from django.contrib import messages


# Create your views here.
def registerUser(request):
    if request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            #create user using form method
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # user.set_password(password)
            # user.save()
            # return redirect('registerUser')

            #create user using create user model method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'your account has been successfully created!')
            return redirect('registerUser')
        else:
           
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registeruser.html', context)

def registerVendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email=email,
                password = password,
            )
            user.role = User.VENDOR
            user.save()
            
            vendor = v_form.save(commit=False)
            vendor.user = user
            #vendor_name = v_form.cleaned_data['vendor_name']
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            messages.success(request, 'your account has been successfully created!, please wait for the approval.')
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)
        
    form = UserForm()
    v_form = VendorForm()
    
    context = {
        'form': form,
        'v_form': v_form,
    }
    return render(request, 'accounts/registerVendor.html', context)
