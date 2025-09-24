from django.contrib import admin
from .models import PrayerRequest  # Import the model

class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'message', 'approved', 'submitted_at')  # Display these fields
    list_filter = ('approved',)  # Add a filter for approval status
    search_fields = ('name', 'message')  # Enable search

admin.site.register(PrayerRequest, PrayerRequestAdmin)  # Register the model
