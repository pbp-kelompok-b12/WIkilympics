from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.urls import reverse
from sports.forms import SportsForm
from sports.models import Sports
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import requests
from django.utils.html import strip_tags
import json

def show_main(request):
    sports_list = Sports.objects.all()
    
    category = request.GET.get('category')  # filter berdasarkan sport_type
    participation = request.GET.get('participation')  # filter berdasarkan participation_structure
    query = request.GET.get('q')           # search berdasarkan sport_name

    if category and category != '':
        sports_list = sports_list.filter(sport_type=category)

    if participation and participation != '': 
        sports_list = sports_list.filter(participation_structure=participation)
    
    if query and query != '':
        sports_list = sports_list.filter(sport_name__istartswith=query)

    context = {
        'sports_list': sports_list,
        'selected_category': category or '',
        'search_query': query or '',
        'categories': dict(Sports.SPORT_TYPE),
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
    json_data = serializers.serialize("json", sports_list)
    return HttpResponse(json_data, content_type="application/json")

def show_json_by_id(request, sports_id):
    try:
        sport = Sports.objects.get(pk=sports_id)
        data = {
            'id': str(sport.id),
            'sport_name': sport.sport_name,
            'sport_img': sport.sport_img,
            'sport_description': sport.sport_description,
            'participation_structure': sport.participation_structure,
            'sport_type': sport.sport_type,
            'country_of_origin': sport.country_of_origin,
            'country_flag_img': sport.country_flag_img,
            'first_year_played': sport.first_year_played,
            'history_description': sport.history_description,
            'equipment': sport.equipment,
        }
        return JsonResponse(data)
    except Sports.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
   
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

@csrf_exempt
@require_POST
def create_sport_entry_ajax(request):
    sport_name = request.POST.get("sport_name")
    sport_img = request.POST.get("sport_img")
    sport_description = request.POST.get("sport_description")
    participation_structure = request.POST.get("participation_structure")
    sport_type = request.POST.get("sport_type")
    country_of_origin = request.POST.get("country_of_origin")
    country_flag_img = request.POST.get("country_flag_img")
    first_year_played = request.POST.get("first_year_played")
    history_description = request.POST.get("history_description")
    equipment = request.POST.get("equipment")

    new_sport = Sports(
        sport_name=sport_name,
        sport_img=sport_img,
        sport_description=sport_description,
        participation_structure=participation_structure,
        sport_type=sport_type,
        country_of_origin=country_of_origin,
        country_flag_img=country_flag_img,
        first_year_played=first_year_played if first_year_played else 0,
        history_description=history_description,
        equipment=equipment,
    )

    new_sport.save()

    return HttpResponse(b"CREATED", status=201)

@csrf_exempt
def edit_sport_entry_ajax(request, id):
    if request.method == 'POST':
        sport = get_object_or_404(Sports, pk=id)
        form = SportsForm(request.POST, instance=sport)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "Sport updated successfully!"})
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@csrf_exempt
def delete_sport_entry_ajax(request, id):
    if request.method == 'POST':
        try:
            sport = Sports.objects.get(pk=id)
            sport.delete()
            return JsonResponse({"status": "success", "message": "Sport deleted successfully."})
        except Sports.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Sport not found."}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from .models import Sports # Ganti 'Sports' jika nama class model kamu berbeda

@csrf_exempt
def create_sport_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # 1. Ambil & Bersihkan Data String (Strip Tags untuk keamanan XSS)
        sport_name = strip_tags(data.get("sport_name", ""))
        sport_img = strip_tags(data.get("sport_img", ""))
        sport_description = strip_tags(data.get("sport_description", ""))
        country_of_origin = strip_tags(data.get("country_of_origin", ""))
        country_flag_img = strip_tags(data.get("country_flag_img", ""))
        history_description = strip_tags(data.get("history_description", ""))
        equipment = strip_tags(data.get("equipment", ""))
        
        # 2. Ambil Data Enum/Choice (Langsung string karena Flutter kirim string)
        participation_structure = data.get("participation_structure", "team")
        sport_type = data.get("sport_type", "ball_sport")

        # 3. Ambil Data Integer
        try:
            first_year_played = int(data.get("first_year_played", 0))
        except ValueError:
            first_year_played = 0

        # 4. Buat Object Baru
        # Catatan: Jika model kamu butuh 'user', tambahkan: user=request.user
        new_sport = Sports(
            sport_name=sport_name,
            sport_img=sport_img,
            sport_description=sport_description,
            participation_structure=participation_structure,
            sport_type=sport_type,
            country_of_origin=country_of_origin,
            country_flag_img=country_flag_img,
            first_year_played=first_year_played,
            history_description=history_description,
            equipment=equipment
        )

        new_sport.save()

        return JsonResponse({"status": "success"}, status=200)

    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def edit_sport_flutter(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            try:
                sport = Sports.objects.get(pk=id)
            except Sports.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Sport ID not found"}, status=404)

            sport.sport_name = strip_tags(data.get("sport_name", sport.sport_name))
            sport.sport_img = strip_tags(data.get("sport_img", sport.sport_img))
            sport.sport_description = strip_tags(data.get("sport_description", sport.sport_description))
            sport.country_of_origin = strip_tags(data.get("country_of_origin", sport.country_of_origin))
            sport.country_flag_img = strip_tags(data.get("country_flag_img", sport.country_flag_img))
            sport.history_description = strip_tags(data.get("history_description", sport.history_description))
            sport.equipment = strip_tags(data.get("equipment", sport.equipment))
            sport.participation_structure = data.get("participation_structure", sport.participation_structure)
            sport.sport_type = data.get("sport_type", sport.sport_type)

            if "first_year_played" in data:
                try:
                    sport.first_year_played = int(data["first_year_played"])
                except ValueError:
                    pass

            sport.save()

            return JsonResponse({
                "status": "success",
                "message": "Sport updated successfully",
                "id": str(sport.pk)
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=401)

@csrf_exempt
def delete_sport_flutter(request, id):
    if request.method == 'POST':
        try:
            # Cari sport berdasarkan UUID (pk)
            sport = Sports.objects.get(pk=id)
            
            # Hapus data
            sport.delete()

            return JsonResponse({"status": "success"}, status=200)
            
        except Sports.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Sport not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=401)