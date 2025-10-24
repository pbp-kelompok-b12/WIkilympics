from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.urls import reverse
from athletes.forms import AthletesForm
from athletes.models import Athletes
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def show_main(request):
    athletes_list = Athletes.objects.all()
    
    sport_filter = request.GET.get('sport')  # filter berdasarkan sport
    country_filter = request.GET.get('country')  # filter berdasarkan country
    query = request.GET.get('q')  # search berdasarkan athlete_name

    if sport_filter and sport_filter != '':
        athletes_list = athletes_list.filter(sport=sport_filter)

    if country_filter and country_filter != '': 
        athletes_list = athletes_list.filter(country__icontains=country_filter)
    
    if query and query != '':
        athletes_list = athletes_list.filter(athlete_name__icontains=query)

    context = {
        'athletes_list': athletes_list,
        'selected_sport': sport_filter or '',
        'selected_country': country_filter or '',
        'search_query': query or '',
        'sports': dict(Athletes.SPORT_CHOICES),
    }

    return render(request, "athletes.html", context)

def create_athlete(request):
    form = AthletesForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('athletes:show_main')

    context = {
        'form': form
    }
    return render(request, "create_athlete.html", context)

def show_athlete(request, id):
    athlete = get_object_or_404(Athletes, pk=id)

    context = {
        'athlete': athlete
    }
    
    return render(request, "athlete_detail.html", context)

def show_json(request):
    athletes_list = Athletes.objects.all()    
    json_data = serializers.serialize("json", athletes_list)
    return HttpResponse(json_data, content_type="application/json")

def show_json_by_id(request, athlete_id):
    try:
        athlete = Athletes.objects.get(pk=athlete_id)
        data = {
            'id': str(athlete.id),
            'athlete_name': athlete.athlete_name,
            'athlete_photo': athlete.athlete_photo,
            'country': athlete.country,
            'country_flag': athlete.country_flag,
            'sport': athlete.sport,
            'biography': athlete.biography,
            'date_of_birth': athlete.date_of_birth.strftime('%Y-%m-%d') if athlete.date_of_birth else '',
            'height': str(athlete.height) if athlete.height else '',
            'weight': str(athlete.weight) if athlete.weight else '',
            'achievements': athlete.achievements,
        }
        return JsonResponse(data)
    except Athletes.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
   
def edit_athlete(request, id):
    athlete = get_object_or_404(Athletes, pk=id)
    form = AthletesForm(request.POST or None, instance=athlete)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('athletes:show_main')

    context = {
        'form': form
    }
    return render(request, "edit_athlete.html", context)

def delete_athlete(request, id):
    athlete = get_object_or_404(Athletes, pk=id)
    athlete.delete()
    return HttpResponseRedirect(reverse('athletes:show_main'))

@csrf_exempt
@require_POST
def create_athlete_entry_ajax(request):
    athlete_name = request.POST.get("athlete_name")
    athlete_photo = request.POST.get("athlete_photo")
    country = request.POST.get("country")
    country_flag = request.POST.get("country_flag")
    sport = request.POST.get("sport")
    biography = request.POST.get("biography")
    date_of_birth = request.POST.get("date_of_birth")
    height = request.POST.get("height")
    weight = request.POST.get("weight")
    achievements = request.POST.get("achievements")

    new_athlete = Athletes(
        athlete_name=athlete_name,
        athlete_photo=athlete_photo,
        country=country,
        country_flag=country_flag,
        sport=sport,
        biography=biography,
        date_of_birth=date_of_birth if date_of_birth else None,
        height=height if height else None,
        weight=weight if weight else None,
        achievements=achievements,
    )

    new_athlete.save()

    return HttpResponse(b"CREATED", status=201)

@csrf_exempt
def edit_athlete_entry_ajax(request, id):
    if request.method == 'POST':
        athlete = get_object_or_404(Athletes, pk=id)
        form = AthletesForm(request.POST, instance=athlete)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Athlete updated successfully!"})
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@csrf_exempt
def delete_athlete_entry_ajax(request, id):
    if request.method == 'POST':
        try:
            athlete = Athletes.objects.get(pk=id)
            athlete.delete()
            return JsonResponse({"status": "success", "message": "Athlete deleted successfully."})
        except Athletes.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Athlete not found."}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)