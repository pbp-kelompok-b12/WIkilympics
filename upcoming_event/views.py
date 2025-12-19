from http.client import HTTPResponse
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import TemplateDoesNotExist
from .models import UpcomingEvent
from datetime import datetime
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags



def is_superuser(user):
    """Cek apakah user adalah admin/superuser"""
    return user.is_superuser


def daftar_event(request):
    """Tampilkan daftar semua event + fitur search dan filter sport"""
    try:
        events = UpcomingEvent.objects.all().order_by('date')

        # Ambil keyword search (nama / lokasi / penyelenggara)
        query = request.GET.get('q')
        if query:
            events = events.filter(
                models.Q(name__icontains=query) |
                models.Q(location__icontains=query) |
                models.Q(organizer__icontains=query)
            )

        # Filter berdasarkan cabang olahraga
        filter_sport = request.GET.get('sport')
        if filter_sport:
            events = events.filter(sport_branch__icontains=filter_sport)

        return render(request, "upcoming_event/daftar_event.html", {"events": events, "query": query})
    except TemplateDoesNotExist:
        return redirect("main:home")


def detail_event(request, event_id):
    """Tampilkan detail event"""
    try:
        event = get_object_or_404(UpcomingEvent, id=event_id)
        return render(request, "upcoming_event/detail_event.html", {"event": event})
    except TemplateDoesNotExist:
        return redirect("main:home")

def show_json(request):
    events = UpcomingEvent.objects.all().order_by("date")
    data = [
        {
            "id": e.id,
            "name": e.name,
            "date": e.date.strftime("%Y-%m-%d"),
            "location": e.location,
            "organizer": e.organizer,
            "sport_branch": e.sport_branch,
            "image_url": e.image_url,
            "description": e.description,
        }
        for e in events
    ]
    return JsonResponse(data, safe=False)

def get_event_json(request, id):
    """API JSON detail event"""
    try:
        event = UpcomingEvent.objects.get(pk=id)
        data = {
            "id": event.id,
            "name": event.name,
            "date": event.date.strftime("%d %B %Y"),
            "location": event.location,
            "organizer": event.organizer,
            "description": event.description,
            "sport_branch": event.sport_branch,
            "image_url": event.image_url,
        }
        return JsonResponse(data)
    except UpcomingEvent.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)


# ==========================
# CREATE / UPDATE / DELETE (ADMIN ONLY)
# ==========================

@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def add_event(request):
    """Tambah event baru (admin only)"""
    if request.method == "POST":
        try:
            name = request.POST.get("name")
            organizer = request.POST.get("organizer")
            date_str = request.POST.get("date")
            location = request.POST.get("location")
            sport_branch = request.POST.get("sport_branch")
            image_url = request.POST.get("image_url")
            description = request.POST.get("description") 
            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            event = UpcomingEvent.objects.create(
                name=name,
                organizer=organizer,
                date=date,
                location=location,
                sport_branch=sport_branch,
                image_url=image_url,
                description=description,
            )

            return JsonResponse({
                "success": True,
                "message": "Event berhasil ditambahkan!",
                "event": {
                    "id": event.id,
                    "name": event.name,
                    "organizer": event.organizer,
                    "date": event.date.strftime("%d %B %Y"),
                    "location": event.location,
                    "sport_branch": event.sport_branch,
                    "image_url": event.image_url,
                    "description": event.description,
                }
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    try:
        return render(request, "upcoming_event/add_event.html")
    except TemplateDoesNotExist:
        return redirect("main:home")


@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def edit_event(request, event_id):
    """Edit event (admin only)"""
    event = get_object_or_404(UpcomingEvent, id=event_id)

    if request.method == "POST":
        try:
            event.name = request.POST.get("name")
            event.organizer = request.POST.get("organizer")

            date_str = request.POST.get("date")
            if date_str:
                event.date = datetime.strptime(date_str, "%Y-%m-%d").date()

            event.location = request.POST.get("location")
            event.sport_branch = request.POST.get("sport_branch")
            event.image_url = request.POST.get("image_url")
            event.description = request.POST.get("description")
            event.save()

            return JsonResponse({
                "success": True,
                "message": "Event berhasil diperbarui!",
                "event": {
                    "id": event.id,
                    "name": event.name,
                    "organizer": event.organizer,
                    "date": event.date.strftime("%d %B %Y"),
                    "location": event.location,
                    "sport_branch": event.sport_branch,
                    "image_url": event.image_url,
                }
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    try:
        return render(request, "upcoming_event/edit_event.html", {"event": event})
    except TemplateDoesNotExist:
        return redirect("main:home")


@login_required(login_url='/login/')
@user_passes_test(is_superuser)
def delete_event(request, event_id):
    """Hapus event (admin only, AJAX-friendly)"""
    event = get_object_or_404(UpcomingEvent, id=event_id)

    if request.method == "POST":
        event.delete()
        # Kirim response JSON biar JS bisa langsung hapus dari tampilan
        return JsonResponse({"success": True, "message": "Event berhasil dihapus!"})

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)

    
@csrf_exempt
def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HTTPResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = request.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HTTPResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except request.RequestException as e:
        return HTTPResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def create_event_flutter(request):
    if request.method == 'POST':
        # 1. CEK APAKAH USER LOGIN DAN ADMIN
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "Anda harus login terlebih dahulu."
            }, status=401)
            
        if not request.user.is_superuser:
            return JsonResponse({
                "status": "error",
                "message": "Hanya admin yang diperbolehkan menambah event."
            }, status=403)

        try:
            # 2. Ambil data (JSON atau Form)
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            # 3. Buat event baru
            new_event = UpcomingEvent.objects.create(
                name=strip_tags(data.get("name")),
                organizer=strip_tags(data.get("organizer")),
                date=data.get("date"),
                location=strip_tags(data.get("location")),
                sport_branch=strip_tags(data.get("sport_branch")),
                image_url=data.get("image_url"),
                description=strip_tags(data.get("description")),
            )

            return JsonResponse({
                "status": "success",
                "message": "Event berhasil dibuat!"
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "error", 
                "message": str(e)
            }, status=400)
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def edit_event_flutter(request, event_id):
    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.is_superuser:
            return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)
        
        try:
            event = UpcomingEvent.objects.get(pk=event_id)
            
            # CEK: Kadang Flutter ngirim data lewat request.POST, kadang request.body
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            # Gunakan data.get("field", event.field) supaya kalau kosong nggak error
            event.name = data.get("name", event.name)
            event.organizer = data.get("organizer", event.organizer)
            
            # Pastikan format tanggal aman
            new_date = data.get("date")
            if new_date:
                event.date = new_date # Jika string dari Flutter sudah yyyy-MM-dd
                
            event.location = data.get("location", event.location)
            event.sport_branch = data.get("sport_branch", event.sport_branch)
            event.image_url = data.get("image_url", event.image_url)
            event.description = data.get("description", event.description)
            
            event.save()
            return JsonResponse({"status": "success", "message": "Event updated!"}, status=200)
            
        except UpcomingEvent.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)
        except Exception as e:
            # Print error ke terminal Django biar lo bisa liat error aslinya apa
            print(f"Error Update: {str(e)}") 
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def delete_event_flutter(request, event_id):
    if request.method == 'POST':
        # KEAMANAN: Cek apakah user login dan superuser
        if not request.user.is_authenticated or not request.user.is_superuser:
            return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)
            
        try:
            event = UpcomingEvent.objects.get(pk=event_id)
            event.delete() 
            return JsonResponse({"status": "success", "message": "Event deleted!"}, status=200)
        except UpcomingEvent.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)