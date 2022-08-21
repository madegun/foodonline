from django.shortcuts import render, redirect
from accounts.utils import detectUser

from vendor.form import VendorForm
from .form import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
    
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already registered')
        return redirect('dashboard')
    elif request.method == 'POST':
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
    if request.user.is_authenticated:
        messages.success(request, 'you are already registered')
        return redirect('dashboard')
    elif request.method == 'POST':
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

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('myAccount')
    
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'you are now login')
            return redirect('myAccount')
        else:
            messages.error(request, 'invalid login credential!')
            return redirect('login')
        
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'you are logged out.')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cusDashboard(request):
    return render(request, 'accounts/cusDashboard.html')


