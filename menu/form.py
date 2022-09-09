from django import forms

from accounts.validators import validation_image
from .models import Category, FoodItem


class CategoryForm(forms.ModelForm):
  class Meta:
    model= Category
    fields=['category_name', 'description']

class FoodItemForm(forms.ModelForm):
  image = forms.FileField(widget=forms.FileInput(attrs={'class':"btn btn-info rounded w-100"}), validators=[validation_image])
  class Meta:
    model = FoodItem
    fields = ['category','food_title', 'description','price','image','is_available']


