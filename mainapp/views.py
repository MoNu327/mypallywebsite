# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from mainapp.forms import MediaUploadForm, PrayerRequestForm
from mainapp.models import MediaFile, PrayerRequest
import os

def index(request):
    return render(request, 'mainapp/index.html')

def home(request):
    # Fetch approved prayer requests to display on the page (newest first)
    prayers = PrayerRequest.objects.filter(approved=True).order_by('-submitted_at')[:10]
    
    if request.method == "POST":
        name = request.POST.get('name')
        message = request.POST.get('message')
        
        # Save to the database
        if name and message:
            # Create prayer request
            prayer = PrayerRequest.objects.create(
                name=name, 
                message=message,
                approved=True  # Set to False if you want manual approval
            )
            messages.success(request, 'Your prayer request has been submitted successfully!')
            return redirect('home')  # Redirect to avoid duplicate submissions
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'mainapp/home.html', {'prayers': prayers})

def administration(request):
    return render(request, 'mainapp/administration.html')

def contact(request):
    return render(request, 'mainapp/contact.html')

def gallery(request):
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Media uploaded successfully!')
            return redirect('gallery')  # Redirect after successful upload
        else:
            messages.error(request, 'Error uploading media. Please try again.')
    
    media_files = MediaFile.objects.all().order_by('-uploaded_at')
    form = MediaUploadForm()
    
    return render(request, 'mainapp/gallery.html', {'form': form, 'media_files': media_files})

@require_http_methods(["DELETE"])
def delete_gallery_media(request, media_id):
    """
    Delete a gallery media item
    """
    try:
        # Get the media object
        media = get_object_or_404(MediaFile, id=media_id)
        
        # Delete the physical file
        if media.file and hasattr(media.file, 'path') and os.path.isfile(media.file.path):
            try:
                os.remove(media.file.path)
            except OSError:
                pass  # File might already be deleted or inaccessible
        
        # Delete the database record
        media.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Media deleted successfully'
        })
        
    except MediaFile.DoesNotExist:
        return JsonResponse({'error': 'Media not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Failed to delete media'}, status=500)

@require_http_methods(["DELETE"])
@csrf_exempt
def delete_prayer(request, prayer_id):
    """
    Delete a prayer request
    """
    try:
        prayer = get_object_or_404(PrayerRequest, id=prayer_id)
        prayer_name = prayer.name
        prayer.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Prayer request from {prayer_name} has been deleted successfully'
        })
        
    except PrayerRequest.DoesNotExist:
        return JsonResponse({'error': 'Prayer request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Failed to delete prayer request'}, status=500)

def services(request):
    # Fetch approved prayer requests for services page
    prayers = PrayerRequest.objects.filter(approved=True).order_by('-submitted_at')[:10]
    
    if request.method == "POST":
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.approved = True  # Set to False if you want manual approval
            prayer.save()
            messages.success(request, 'Your prayer request has been submitted successfully!')
            return redirect('services')  # Redirect after submission
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PrayerRequestForm()
        
    return render(request, 'mainapp/services.html', {'form': form, 'prayers': prayers})

def history(request):
    return render(request, 'mainapp/history.html')

def events(request):
    return render(request, 'mainapp/events.html')

def manage_prayers(request):
    prayers = PrayerRequest.objects.all().order_by('-submitted_at')
        
    if request.method == "POST":
        prayer_id = request.POST.get("prayer_id")
        action = request.POST.get("action")
        
        if prayer_id and action:
            try:
                prayer = PrayerRequest.objects.get(id=prayer_id)
                
                if action == "approve":
                    prayer.approved = True
                    prayer.save()
                    messages.success(request, f'Prayer request from {prayer.name} has been approved.')
                elif action == "delete":
                    prayer.delete()
                    messages.success(request, 'Prayer request has been deleted.')
                elif action == "unapprove":
                    prayer.approved = False
                    prayer.save()
                    messages.success(request, f'Prayer request from {prayer.name} has been unapproved.')
                
            except PrayerRequest.DoesNotExist:
                messages.error(request, 'Prayer request not found.')
        
        return redirect("manage_prayers")
    
    return render(request, "admin/manage_prayers.html", {"prayers": prayers})

# Additional view for AJAX prayer submission (optional)
@csrf_exempt
def submit_prayer_ajax(request):
    """
    AJAX endpoint for submitting prayer requests
    """
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        name = request.POST.get('name')
        message = request.POST.get('message')
        
        if name and message:
            prayer = PrayerRequest.objects.create(
                name=name,
                message=message,
                approved=True  # Set to False for manual approval
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Prayer request submitted successfully!',
                'prayer': {
                    'id': prayer.id,
                    'name': prayer.name,
                    'message': prayer.message,
                    'submitted_at': prayer.submitted_at.strftime("%b %d, %Y")
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)