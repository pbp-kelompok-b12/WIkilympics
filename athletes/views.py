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
    
    sport_filter = request.GET.get('sport')
    country_filter = request.GET.get('country')
    query = request.GET.get('q')

    if sport_filter and sport_filter != '':
        athletes_list = athletes_list.filter(sport=sport_filter)

    if country_filter and country_filter != '': 
        athletes_list = athletes_list.filter(country__icontains=country_filter)
    
    if query and query != '':
        athletes_list = athletes_list.filter(athlete_name__icontains=query)

    sports_choices = Athletes.objects.values_list('sport', flat=True).distinct()
    
    context = {
        'athletes_list': athletes_list,
        'selected_sport': sport_filter or '',
        'selected_country': country_filter or '',
        'search_query': query or '',
        'sports': {sport: sport for sport in sports_choices},
    }

    return render(request, "athletes.html", context)

def create_athlete(request):
    form = AthletesForm(request.POST or None)
    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('athletes:show_main')
    context = {'form': form}
    return render(request, "create_athlete.html", context)

def show_athlete(request, id):
    athlete = get_object_or_404(Athletes, pk=id)
    context = {'athlete': athlete}
    return render(request, "athlete_detail.html", context)

def show_json(request):
    athletes_list = Athletes.objects.all()    
    return HttpResponse(serializers.serialize("json", athletes_list), content_type="application/json")

def show_json_by_id(request, athlete_id):
    try:
        athlete = Athletes.objects.get(pk=athlete_id)
        data = {
            'id': str(athlete.id),
            'athlete_name': athlete.athlete_name,
            'athlete_photo': athlete.athlete_photo,
            'country': athlete.country,
            'sport': athlete.sport,
            'biography': athlete.biography,
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
    context = {'form': form}
    return render(request, "edit_athlete.html", context)

def delete_athlete(request, id):
    athlete = get_object_or_404(Athletes, pk=id)
    athlete.delete()
    return HttpResponseRedirect(reverse('athletes:show_main'))

@csrf_exempt
@require_POST
def create_athlete_entry_ajax(request):
    if request.method == 'POST':
        try:
            athlete_name = request.POST.get("athlete_name")
            athlete_photo = request.POST.get("athlete_photo")
            country = request.POST.get("country")
            sport = request.POST.get("sport")
            biography = request.POST.get("biography")

            new_athlete = Athletes(
                athlete_name=athlete_name,
                athlete_photo=athlete_photo,
                country=country,
                sport=sport,
                biography=biography,
            )
            new_athlete.save()

            return JsonResponse({"status": "success", "message": "Athlete added successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

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