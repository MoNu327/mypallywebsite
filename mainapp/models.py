from django.db import models

class MediaFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']  # Newest first by default
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'

    def __str__(self):
        return self.file.name
    
    def filename(self):
        """Returns just the filename without path"""
        return self.file.name.split('/')[-1]
    
    def file_extension(self):
        """Returns the file extension"""
        return self.filename().split('.')[-1].lower() if '.' in self.filename() else ''
    
    def is_image(self):
        """Check if the file is an image"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return self.file_extension() in image_extensions
    
    def is_video(self):
        """Check if the file is a video"""
        video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']
        return self.file_extension() in video_extensions


class PrayerRequest(models.Model):
    PRAYER_STATUS = [
        (True, 'Approved'),
        (False, 'Pending Approval'),
    ]
    
    name = models.CharField(max_length=100)
    message = models.TextField()
    approved = models.BooleanField(default=False, choices=PRAYER_STATUS)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Track when prayer was approved/updated
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']  # Newest prayers first
        verbose_name = 'Prayer Request'
        verbose_name_plural = 'Prayer Requests'
        indexes = [
            models.Index(fields=['approved', 'submitted_at']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"Prayer from {self.name} ({'Approved' if self.approved else 'Pending'})"
    
    def get_short_message(self, length=100):
        """Return shortened message for display"""
        if len(self.message) <= length:
            return self.message
        return self.message[:length] + '...'
    
    @property
    def status(self):
        """Return human-readable status"""
        return 'Approved' if self.approved else 'Pending Approval'
    
    @classmethod
    def get_approved_prayers(cls, limit=10):
        """Get approved prayers with limit"""
        return cls.objects.filter(approved=True)[:limit]
    
    @classmethod
    def get_pending_prayers(cls):
        """Get prayers pending approval"""
        return cls.objects.filter(approved=False)