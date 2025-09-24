from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from mainapp.forms import MediaUploadForm, PrayerRequestForm, ContactForm
from mainapp.models import MediaFile, PrayerRequest, ContactMessage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os


def home(request):
    # Get approved prayers for display
    prayers = PrayerRequest.objects.filter(approved=True).order_by('-submitted_at')[:10]
    
    if request.method == "POST":
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            try:
                prayer = form.save(commit=False)
                prayer.approved = True  # Auto-approve for home page
                prayer.save()
                messages.success(request, 'Your sacred message has been submitted successfully!')
                return redirect('home')
            except Exception as e:
                messages.error(request, 'An error occurred while submitting your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        form = PrayerRequestForm()  # Create empty form for GET requests
    
    # Debug: Print to console to verify form is being created
    print(f"Form object: {form}")
    print(f"Form fields: {form.fields if form else 'No form'}")
    
    context = {
        'prayers': prayers,
        'form': form,
    }
    
    return render(request, 'mainapp/home.html', context)


@require_POST
@csrf_exempt
def increment_prayer_count(request, prayer_id):
    """
    Increment prayer count for a specific prayer request
    """
    try:
        prayer = get_object_or_404(PrayerRequest, id=prayer_id)
        prayer.increment_prayer_count()
        
        return JsonResponse({
            'success': True,
            'prayer_count': prayer.prayer_count
        })
        
    except PrayerRequest.DoesNotExist:
        return JsonResponse({'error': 'Prayer request not found'}, status=404)
    except Exception as e:
        print(f"Error incrementing prayer count: {e}")
        return JsonResponse({'error': 'Failed to increment prayer count'}, status=500)


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
        print(f"Error deleting prayer: {e}")
        return JsonResponse({'error': 'Failed to delete prayer request'}, status=500)


def index(request):
    return render(request, 'mainapp/index.html')


def administration(request):
    return render(request, 'mainapp/administration.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message to the database
            contact_message = form.save()
            
            # Show success message
            messages.success(request, '✠ Blessed be your message! Our parish family will respond to you with Christian love and care. Peace be with you. ✠')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ContactForm()
    
    return render(request, 'mainapp/contact.html', {'form': form})


def gallery(request):
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Media uploaded successfully!')
            return redirect('gallery')
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
        media = get_object_or_404(MediaFile, id=media_id)
        
        # Delete the physical file
        if media.file and hasattr(media.file, 'path') and os.path.isfile(media.file.path):
            try:
                os.remove(media.file.path)
            except OSError:
                pass
        
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


def services(request):
    prayers = PrayerRequest.objects.filter(approved=True).order_by('-submitted_at')[:10]
    
    if request.method == "POST":
        form = PrayerRequestForm(request.POST)
        if form.is_valid():
            prayer = form.save(commit=False)
            prayer.approved = True
            prayer.save()
            messages.success(request, 'Your prayer request has been submitted successfully!')
            return redirect('services')
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


@csrf_exempt
def submit_prayer_ajax(request):
    """
    AJAX endpoint for submitting prayer requests
    """
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        name = request.POST.get('name')
        message = request.POST.get('message')
        
        if name and message:
            try:
                prayer = PrayerRequest.objects.create(
                    name=name,
                    message=message,
                    approved=True
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
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': 'An error occurred while submitting your prayer.'
                }, status=500)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)