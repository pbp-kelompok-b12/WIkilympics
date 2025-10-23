from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import PollQuestion, PollOption
import random
import traceback


def landing_page(request):
    polls = list(PollQuestion.objects.all())
    poll = random.choice(polls) if polls else None
    # is_admin = request.user.is_authenticated and "admin" in request.user.username.lower()
    is_admin = request.user.is_superuser 


    edit_mode = False
    edit_poll_obj = None

    if request.method == "POST":
        try:
            # TAMBAH POLLING
            if "add_poll" in request.POST and is_admin:
                question_text = request.POST.get("question")
                options = request.POST.getlist("options[]")

                poll_obj = PollQuestion.objects.create(question_text=question_text)
                for opt_text in options:
                    if opt_text.strip():
                        PollOption.objects.create(question=poll_obj, option_text=opt_text)

                # AJAX response 
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    csrf_token = request.META.get("CSRF_COOKIE", "")
                    html = f"""
                    <div class='poll-card animate-fade'>
                        <h3>{poll_obj.question_text}</h3>
                        <ul>
                            {''.join([
                                f"<li>{opt.option_text} <span class='text-sm text-gray-600'>{opt.votes} votes</span></li>"
                                for opt in poll_obj.options.all()
                            ])}
                        </ul>
                        <div class='flex justify-center space-x-3'>
                            <form method='POST' action=''>
                                <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                                <input type='hidden' name='poll_id' value='{poll_obj.id}'>
                                <button type='submit' name='edit_poll' class='btn-edit'>Edit</button>
                            </form>
                            <form method='POST' action='/delete/{poll_obj.id}/'>
                                <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                                <button type='submit' class='btn-delete'>Hapus</button>
                            </form>
                        </div>
                    </div>
                    """
                    return JsonResponse({
                        "status": "success",
                        "message": "✅ Polling berhasil ditambahkan!",
                        "html": html,
                    })

                # kalau bukan AJAX
                messages.success(request, "✅ Polling berhasil ditambahkan!")
                return redirect("landingpoll:landing_page")

            # SIMPAN HASIL EDIT 
            elif "save_edit" in request.POST and is_admin:
                poll_id = request.POST.get("poll_id")
                question_text = request.POST.get("question")
                options = request.POST.getlist("options[]")

                poll_obj = get_object_or_404(PollQuestion, pk=poll_id)
                poll_obj.question_text = question_text
                poll_obj.save()

                # hapus opsi lama dan tambahkan yang baru
                poll_obj.options.all().delete()
                for opt_text in options:
                    if opt_text.strip():
                        PollOption.objects.create(question=poll_obj, option_text=opt_text)

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({
                        "status": "success",
                        "message": "✏️ Polling berhasil diperbarui!",
                        "poll_id": poll_obj.id,
                        "question": poll_obj.question_text,
                        "options": list(poll_obj.options.values("option_text", "votes")),
                    })

                messages.success(request, "✏️ Polling berhasil diperbarui!")
                return redirect("landingpoll:landing_page")

        except Exception as e:
            print("=== ERROR SAAT PROSES POLLING ===")
            traceback.print_exc()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "error",
                    "message": "Terjadi kesalahan server."
                }, status=500)

    context = {
        "poll": poll,
        "polls": polls,
        "is_admin": is_admin,
        "edit_mode": edit_mode,
        "edit_poll_obj": edit_poll_obj,
    }
    return render(request, "landing.html", context)


#  AJAX HAPUS POLLING 
def delete_poll(request, poll_id):
    if request.user.is_authenticated and request.user.is_superuser:
        poll = get_object_or_404(PollQuestion, pk=poll_id)
        poll.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "status": "success",
                "message": "🗑️ Polling berhasil dihapus!"
            })

        messages.success(request, "🗑️ Polling berhasil dihapus!")
        return redirect("landingpoll:landing_page")

    return JsonResponse({
        "status": "error",
        "message": "Kamu tidak punya izin untuk menghapus polling."
    }, status=403)


#  AJAX VOTE POLLING 
def vote_poll(request, option_id):
    option = get_object_or_404(PollOption, pk=option_id)
    option.votes += 1
    option.save()
    return JsonResponse({
        "success": True,
        "total_votes": option.question.total_votes()
    })
