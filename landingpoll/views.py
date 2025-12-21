import json
import random
import traceback
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# --- IMPORT MODEL ---
from .models import PollQuestion, PollOption

# Import model dari modul lain (sesuai kode aslimu)
from sports.models import Sports
from athletes.models import Athletes
from upcoming_event.models import UpcomingEvent
from article.models import Article
from forum_section.models import Forum, Discussion

# ==========================================
#  LANDING PAGE & WEB LOGIC
# ==========================================

def landing_page(request):
    """
    Landing Page utama (Home)
    """
    # --- Bagian Polling ---
    polls = list(PollQuestion.objects.all())
    poll = random.choice(polls) if polls else None
    is_admin = request.user.is_superuser
    edit_mode = False
    edit_poll_obj = None

    # --- Bagian data modul lain ---
    sports_list, athletes_list, events_list, article_list, forum_list, discussion_list = [], [], [], [], [], []

    try:
        sports_list = Sports.objects.all()[:4]
    except Exception as e:
        print("⚠️ Gagal load Sports:", e)

    try:
        article_list = Article.objects.order_by("created")[:3]
    except Exception as e:
        print("⚠️ Gagal load Article:", e)

    try:
        events_list = UpcomingEvent.objects.order_by("date")[:3]
    except Exception as e:
        print("⚠️ Gagal load Upcoming Event:", e)
    
    try:
        forum_list = Forum.objects.order_by("-date_created")[:3]
    except Exception as e:
        print("⚠️ Gagal load Forum:", e)

    try:
        discussion_list = Discussion.objects.order_by("-date_created")[:3]
    except Exception as e:
        print("⚠️ Gagal load Discussion:", e)

    try:
        athletes_list = Athletes.objects.order_by("athlete_name")[:4]
    except Exception as e:
        print("⚠️ Gagal load Athletes:", e)

    
    # Bagian proses form Polling (Add / Edit via WEB/AJAX)
    if request.method == "POST":
        try:
            #  TAMBAH POLLING VIA WEB
            if "add_poll" in request.POST and is_admin:
                question_text = request.POST.get("question")
                options = request.POST.getlist("options[]")

                poll_obj = PollQuestion.objects.create(question_text=question_text)
                for opt_text in options:
                    if opt_text.strip():
                        PollOption.objects.create(question=poll_obj, option_text=opt_text)

                # kalau request dari AJAX Web
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    html = f"""
                    <div class='poll-card animate-fade'>
                        <h3>{poll_obj.question_text}</h3>
                        <ul>
                            {''.join([
                                f"<li><span>{opt.option_text}</span> <span class='text-sm text-gray-600'>{opt.votes} votes</span></li>"
                                for opt in poll_obj.options.all()
                            ])}
                        </ul>
                        <div class="flex justify-center space-x-3 mt-3">
                            <form method="POST" action="">
                                <input type="hidden" name="poll_id" value="{poll_obj.id}">
                                <button type="submit" name="edit_poll" class="btn-edit bg-yellow-400 hover:bg-yellow-500 text-white px-3 py-1 rounded-lg">Edit</button>
                            </form>
                            <form method="POST" action="/delete_poll/{poll_obj.id}/">
                                <button type="submit" class="btn-delete bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg">Hapus</button>
                            </form>
                        </div>
                    </div>
                    """
                    return JsonResponse({
                        "status": "success",
                        "message": "Polling berhasil ditambahkan!",
                        "html": html,
                    })

                messages.success(request, "Polling berhasil ditambahkan!")
                return redirect("landingpoll:landing_page")

            # === SIMPAN HASIL EDIT POLLING VIA WEB ===
            elif "save_edit" in request.POST and is_admin:
                poll_id = request.POST.get("poll_id")
                question_text = request.POST.get("question")
                options = request.POST.getlist("options[]")

                poll_obj = get_object_or_404(PollQuestion, pk=poll_id)
                poll_obj.question_text = question_text
                poll_obj.save()

                # hapus opsi lama & tambahkan yang baru
                poll_obj.options.all().delete()
                for opt_text in options:
                    if opt_text.strip():
                        PollOption.objects.create(question=poll_obj, option_text=opt_text)

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({
                        "status": "success",
                        "message": "Polling berhasil diperbarui!",
                        "poll_id": poll_obj.id,
                        "question": poll_obj.question_text,
                        "options": list(poll_obj.options.values("option_text", "votes")),
                    })

                messages.success(request, "Polling berhasil diperbarui!")
                return redirect("landingpoll:landing_page")

        except Exception:
            traceback.print_exc()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "error",
                    "message": "Terjadi kesalahan server."
                }, status=500)

    
    # Kirim semua data ke template
    context = {
        "poll": poll,
        "polls": polls,
        "is_admin": is_admin,
        "edit_mode": edit_mode,
        "edit_poll_obj": edit_poll_obj,
        "sports_list": sports_list,
        "athletes_list": athletes_list,
        "events_list": events_list,
        "article_list": article_list,
        "forum_list": forum_list,
    }

    return render(request, "landing.html", context)


# Hapus polling (Admin only)
@csrf_exempt
def delete_poll(request, poll_id):
    if request.user.is_authenticated and request.user.is_superuser:
        poll = get_object_or_404(PollQuestion, pk=poll_id)
        poll.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.method == "POST":
            return JsonResponse({"status": "success", "message": "Polling berhasil dihapus!"})

        messages.success(request, "Polling berhasil dihapus!")
        return redirect("landingpoll:landing_page")

    return JsonResponse({"status": "error", "message": "Tidak punya izin."}, status=403)

# Vote polling (User)
def vote_poll(request, option_id):
    option = get_object_or_404(PollOption, pk=option_id)
    option.votes += 1
    option.save()
    return JsonResponse({
        "success": True,
        "total_votes": option.question.total_votes()
    })

# API Polling untuk Flutter (READ)
def polls_api(request):
    data = []
    for q in PollQuestion.objects.prefetch_related('options').all():
        data.append({
            "id": q.id,
            "question_text": q.question_text,
            "options": [
                {
                    "id": o.id,
                    "option_text": o.option_text,
                    "votes": o.votes,
                }
                for o in q.options.all()
            ]
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def create_poll_flutter(request):
    if request.method == 'POST':
        try:
            # --- LOGIKA CERDAS BACA DATA ---
            # Coba baca dari JSON Body dulu
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                # Kalau gagal (body kosong/bukan json), baca dari request.POST (Form Data)
                data = request.POST

            print(f"DEBUG CREATE DATA: {data}") # Cek di terminal

            question_text = data.get('question')
            raw_options = data.get('options')

            # Handle format options
            if isinstance(raw_options, str):
                try:
                    options_list = json.loads(raw_options)
                except:
                    # Fallback kalau stringnya bukan json valid, anggap list satu item?
                    # Atau mungkin data dikirim raw.
                    options_list = [raw_options] 
            else:
                options_list = raw_options

            # Pastikan options_list adalah list
            if not isinstance(options_list, list):
                 # Coba ambil list kalau dikirim via form-data dengan nama sama (options[])
                 options_list = request.POST.getlist('options') 
                 if not options_list and raw_options: 
                     # Last resort
                     options_list = [str(raw_options)]

            if not question_text or not options_list:
                return JsonResponse({"status": "error", "message": "Data incomplete"}, status=400)

            # Simpan
            new_poll = PollQuestion.objects.create(question_text=question_text)
            for opt_text in options_list:
                PollOption.objects.create(question=new_poll, option_text=opt_text, votes=0)

            return JsonResponse({"status": "success", "message": "Poll created"}, status=200)

        except Exception as e:
            print(f"ERROR CREATE FLUTTER: {e}")
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)


@csrf_exempt
def edit_poll_flutter(request, poll_id):
    if request.method == 'POST':
        try:
            poll = PollQuestion.objects.get(pk=poll_id)
            
            # --- LOGIKA CERDAS BACA DATA ---
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = request.POST
            
            print(f"DEBUG EDIT DATA: {data}")

            new_question_text = data.get('question')
            raw_options = data.get('options')

            if isinstance(raw_options, str):
                try:
                    new_options_list = json.loads(raw_options)
                except:
                    new_options_list = [raw_options]
            else:
                new_options_list = raw_options
            
            if not isinstance(new_options_list, list):
                 new_options_list = request.POST.getlist('options')

            # Update Question
            if new_question_text:
                poll.question_text = new_question_text
                poll.save()

            # Update Options
            if new_options_list:
                poll.options.all().delete()
                for opt_text in new_options_list:
                    PollOption.objects.create(question=poll, option_text=opt_text, votes=0)

            return JsonResponse({"status": "success", "message": "Poll updated"}, status=200)

        except PollQuestion.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Poll not found"}, status=404)
        except Exception as e:
            print(f"ERROR EDIT FLUTTER: {e}")
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)