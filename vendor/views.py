from django.shortcuts import render, get_object_or_404, redirect
from accounts.form import UserProfileForm
from django.contrib import messages

from accounts.models import UserProfile
from menu.form import CategoryForm
from menu.models import Category, FoodItem
from vendor.models import Vendor
from .form import VendorForm

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor

from django.template.defaultfilters import slugify

#helper to get vendor
def get_vendor(request):
  vendor = Vendor.objects.get(user=request.user)
  return vendor

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


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menuBuilder(request):
  vendor = get_vendor(request)
  categories = Category.objects.filter(vendor=vendor).order_by('created_at')

  context = {
    'categories': categories,
  }
  return render(request, 'vendor/menu-builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def foodItemByCat(request, pk=None):
  vendor = get_vendor(request)
  category = get_object_or_404(Category, pk=pk)
  fooditems = FoodItem.objects.filter(vendor=vendor, category=category)

  context ={
    'category': category,
    'fooditems': fooditems,
  }

  return render(request, 'vendor/foodItemByCat.html', context)


#category CRUD
def addCat(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.save()

      category.slug = slugify(category_name)+'-'+str(category.id)
      category.save()
      messages.success(request, 'category berhasil ditambahkan')
      return redirect('menu-builder')
    else:
      print(form.errors)
  else:
    form = CategoryForm()
  context = {
    'form': form,
    }

  return render(request, 'vendor/addCat.html', context)



def edit_category(request, pk=None):
  category = get_object_or_404(Category, pk=pk)
  if request.method == 'POST':
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.save()

      category.slug = slugify(category_name)+'-'+str(category.id)
      category.save()
      messages.success(request, 'category berhasil ditambahkan')
      return redirect('menu-builder')
    else:
      print(form.errors)
  else:
    form = CategoryForm(instance=category)
  context = {
    'form': form,
    'category': category,
    }

  return render(request, 'vendor/edit-category.html', context)


def delete_category(request, pk=None):
  category = get_object_or_404(Category, pk=pk)
  category.delete()
  messages.success(request, 'category berhasil dihapus')
  return redirect('menu-builder')
