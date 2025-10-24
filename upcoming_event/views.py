from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import TemplateDoesNotExist
from .models import UpcomingEvent
from datetime import datetime
from django.db import models



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
