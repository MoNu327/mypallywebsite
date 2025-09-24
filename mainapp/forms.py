from django import forms
from .models import MediaFile

class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ('file',)
from django import forms
from .models import PrayerRequest

class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['name', 'message', 'approved']
