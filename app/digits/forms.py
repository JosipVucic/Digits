from django import forms
from django.forms.fields import ImageField
from django.utils.translation import gettext_lazy as _


class ImageForm(forms.Form):
    """The form used for image upload, uses a single ImageField labeled as "image"."""
    image = ImageField(label=_("Image"))
