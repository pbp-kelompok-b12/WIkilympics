from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.urls import reverse
from sports.forms import SportsForm
from sports.models import Sports

# Create your views here.

def show_main(request):
    sports_list = Sports.objects.all()

    context = {
        'sports_list': sports_list
    }

    return render(request, "sports.html", context)

def create_sport(request):
    form = SportsForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "create_sport.html", context)

def show_sport(request, id):
    sport = get_object_or_404(Sports, pk=id)

    context = {
        'sport': sport
    }
    
    return render(request, "sport_detail.html", context)

def show_json(request):
    sports_list = Sports.objects.all()
    # data = [
    #     {
    #         'id': str(sport.id),
    #         'sport_name': sport.sport_name,
    #         'sport_img': sport.sport_img,
    #         'sport_description': sport.sport_description,
    #         'participation_structure': sport.participation_structure,
    #         'sport_type': sport.sport_type,
    #         'country_of_origin': sport.country_of_origin,
    #         'country_flag_img': sport.country_flag_img,
    #         'first_year_played': sport.first_year_played,
    #         'history_description': sport.history_description,
    #         'equipment': sport.equipment
    #     }
    #     for sport in sports_list
    # ]

    # return JsonResponse(data, safe=False)
    
    json_data = serializers.serialize("json", sports_list)
    return HttpResponse(json_data, content_type="application/json")

def show_json_by_id(request, sports_id):
   try:
       sport_item = Sports.objects.get(pk=sports_id)
       json_data = serializers.serialize("json", [sport_item])
       return HttpResponse(json_data, content_type="application/json")
   except Sports.DoesNotExist:
       return HttpResponse(status=404)
   
def edit_sport(request, id):
    sport = get_object_or_404(Sports, pk=id)
    form = SportsForm(request.POST or None, instance=sport)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "edit_sport.html", context)

def delete_sport(request, id):
    sport = get_object_or_404(Sports, pk=id)
    sport.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

# TODO
# Lengkapi show_sports()