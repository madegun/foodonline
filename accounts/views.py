from email import message
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from accounts.utils import detectUser, send_email_verify

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

            #send verification email
            mail_subject = 'verification email'
            email_template = 'accounts/emails/account_verify_email.html'
            send_email_verify(request, user, mail_subject, email_template)

            messages.success(request,
                             'your account has been successfully created!')
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
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()

            #send verification email
            mail_subject = 'Verivication email'
            email_template = 'accounts/emails/account_verify_email.html'
            send_email_verify(request, user, mail_subject, email_template)

            vendor = v_form.save(commit=False)
            vendor.user = user
            #vendor_name = v_form.cleaned_data['vendor_name']
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            messages.success(
                request,
                'your account has been successfully created!, please wait for the approval.'
            )
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


#activate user email - is_active=True
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link!')
        return redirect('myAccount')


#logout user
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


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            #send verifikasi email link
            mail_subject = 'Please click link below to reset your password'
            email_template = 'accounts/emails/reset_email_password.html'
            send_email_verify(request, user, mail_subject, email_template)
            messages.success(
                request,
                'please check password link has been send to your email!')
            return redirect('login')
        else:
            messages.error(request, 'email account does not exist')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        

    if user is not None and default_token_generator.check_token(
                user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.info(request, 'your new password successfully')
            return redirect('login')
        else:
            messages.error(request,'password do not match')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
