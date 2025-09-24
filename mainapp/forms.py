from django import forms
from .models import MediaFile, ContactMessage, PrayerRequest


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*'
            })
        }


class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['name', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your blessed name',
                'required': True,
                'id': 'id_name',
                'maxlength': '100'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your sacred message or prayer intention...',
                'rows': 5,
                'required': True,
                'maxlength': '500',
                'id': 'id_message'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        if len(name.strip()) < 2:
            raise forms.ValidationError("Please enter a valid name.")
        return name.strip()

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message:
            raise forms.ValidationError("Message is required.")
        message = message.strip()
        if len(message) < 10:
            raise forms.ValidationError("Please provide a more detailed message (at least 10 characters).")
        if len(message) > 500:
            raise forms.ValidationError("Message must be less than 500 characters.")
        return message


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Blessed Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Sacred Email',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message Subject',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your thoughts, prayer requests, or inquiries with our parish family...',
                'required': True
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        if len(name.strip()) < 2:
            raise forms.ValidationError("Please enter a valid name.")
        return name.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email.strip().lower()

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message:
            raise forms.ValidationError("Message is required.")
        message = message.strip()
        if len(message) < 2:
            raise forms.ValidationError("Please provide a more detailed message.")
        return message