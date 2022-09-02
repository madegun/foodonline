import os
from django.core.exceptions import ValidationError

def validation_image(value):
  ext = os.path.splitext(value.name)[1]
  print(ext)
  valid_extentions = ['.png','.jpg','.jpeg']
  if not ext.lower() in valid_extentions:
    raise ValidationError('file extention image tidak valid')
