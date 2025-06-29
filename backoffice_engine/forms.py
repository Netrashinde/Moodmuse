from backoffice_engine.models import *
from django import forms

class register_form(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['name', 'email', 'password','contact','address']


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['name', 'contact']


class DetectedEmotionForm(forms.ModelForm):
    class Meta:
        model = DetectedEmotion
        fields = ['user', 'photos']