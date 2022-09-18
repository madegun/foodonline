from django.shortcuts import render, get_object_or_404, redirect
from accounts.form import UserProfileForm
from django.contrib import messages

from accounts.models import UserProfile
from menu.form import CategoryForm, FoodItemForm
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
@login_required(login_url='login')
@user_passes_test(check_role_vendor)

def addCat(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.save()
      category.slug = slugify(category_name)+'-'+str(category.id) #setelah category di save diatas, kemudian slug + id
      category.save() #simpan lagi database dgn slug

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


@login_required(login_url='login')
@user_passes_test(check_role_vendor)

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

@login_required(login_url='login')
@user_passes_test(check_role_vendor)

def delete_category(request, pk=None):
  category = get_object_or_404(Category, pk=pk)
  category.delete()
  messages.success(request, 'category berhasil dihapus')
  return redirect('menu-builder')


def add_food(request):
  if request.method == 'POST':
    form = FoodItemForm(request.POST, request.FILES)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food = form.save(commit=False)
      food.vendor = get_vendor(request)
      food.slug = slugify(food_title)
      form.save()
      messages.success(request, 'add food berhasil ditambahkan.')
      return redirect('foodItemByCat', food.category.id)
    else:
      print(form.errors)
  else:
    form = FoodItemForm()
    #tampilkan category terhadap user only
    #modif form sebelum ke context
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
      'form': form,
    }
  return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)

def edit_food(request, pk=None):
  food = get_object_or_404(FoodItem, pk=pk)
  if request.method == 'POST':
    form = FoodItemForm(request.POST, request.FILES, instance=food)
    if form.is_valid():
      foodtitle = form.cleaned_data['food_title']
      food = form.save(commit=False)
      food.vendor = get_vendor(request)
      food.slug = slugify(foodtitle)
      form.save()
      messages.success(request, 'Food item berhasil di update.')
      return redirect('foodItemByCat', food.category.id)
    else:
      print(form.errors)
  else:
    form = FoodItemForm(instance=food)
    #tampilkan category terhadap user only
    #modif form sebelum ke context
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
      'form': form,
      'food': food,
    }
  return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)

def delete_food(request, pk=None):
  food = get_object_or_404(FoodItem, pk=pk)
  food.delete()
  messages.success(request, 'Food item berhasil di hapus.')
  return redirect('foodItemByCat', food.category.id)
