# urls.py
from django.urls import path
from mainapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('gallery/', views.gallery, name='gallery'),
    path('administration/', views.administration, name='administration'),
    path('contact/', views.contact_view, name='contact'),  # Using contact_view function
    path('history/', views.history, name='history'),
    path('events/', views.events, name='events'),
    path('manage-prayers/', views.manage_prayers, name='manage_prayers'),
    
    # AJAX endpoints
    path('delete-prayer/<int:prayer_id>/', views.delete_prayer, name='delete_prayer'),
    path('increment-prayer/<int:prayer_id>/', views.increment_prayer_count, name='increment_prayer'),
    path('delete-gallery-media/<int:media_id>/', views.delete_gallery_media, name='delete_gallery_media'),
    path('submit-prayer-ajax/', views.submit_prayer_ajax, name='submit_prayer_ajax'),
]