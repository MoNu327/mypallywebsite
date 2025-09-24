from django.contrib import admin
from django.apps import apps
from django.utils.html import format_html
from .models import PrayerRequest, MediaFile, ContactMessage

# ===== Custom ModelAdmin classes =====

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_message', 'status', 'prayer_count', 'submitted_at', 'updated_at', 'approve_button')
    list_filter = ('approved', 'submitted_at')
    search_fields = ('name', 'message')
    readonly_fields = ('prayer_count', 'submitted_at', 'updated_at')

    def short_message(self, obj):
        return obj.get_short_message(50)
    short_message.short_description = 'Message'

    # Optional admin action button for approving prayer requests
    def approve_button(self, obj):
        if not obj.approved:
            return format_html(
                '<a class="button" href="{}">Approve</a>',
                f'/admin/mainapp/prayerrequest/{obj.id}/change/?_approve=true'
            )
        return 'Approved'
    approve_button.short_description = 'Approve'

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'file_link', 'file_extension', 'is_image', 'is_video', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('file',)
    readonly_fields = ('uploaded_at',)

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.filename())
        return '-'
    file_link.short_description = 'File Link'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


# ===== Auto-register any remaining models =====
app_models = apps.get_app_config('mainapp').get_models()

for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
