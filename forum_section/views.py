#sources in case I forget:
#https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-display/


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from .models import *
from .forms import *
# Create your views here.
from django.views.generic.edit import CreateView
from django.core import serializers


def show_json_forum(request):
    forum_list = Forum.objects.all()
    forums_data = []
    for forum in forum_list:
        forums_data.append({
            "model": "forum_section.forum",
            "pk": forum.pk,
            "fields": {
                "name": forum.name.id,
                "topic": forum.topic,
                "description": forum.description,
                "date_created": forum.date_created.isoformat(),
                "thumbnail": (forum.thumbnail or "").strip()
            }
        })
    return JsonResponse(forums_data, safe=False, content_type="application/json")

def show_json_discussion(request):
    discussion_list = Discussion.objects.all()
    # Serialize with username 
    discussions_data = []
    for discussion in discussion_list:
        discussions_data.append({
            "model": "forum_section.discussion",
            "pk": discussion.pk,
            "fields": {
                "username": discussion.username.username,  # Get actual username string
                "username_id": discussion.username.id,      # include user ID just incase
                "forum": discussion.forum.pk,
                "discuss": discussion.discuss,
                "date_created": discussion.date_created.isoformat()
            }
        })
    return JsonResponse(discussions_data, safe=False, content_type="application/json")

def get_username(request):
    # get current user
    if request.user.is_authenticated:
        return JsonResponse({
            "username": request.user.username,
            "authenticated": True
        })
    return JsonResponse({
        "username": None,
        "authenticated": False
    })

@csrf_exempt
def get_user_info(request):
    """Get current user's ID and superuser status"""
    if request.user.is_authenticated:
        return JsonResponse({
            "user_id": request.user.id,
            "username": request.user.username,
            "is_superuser": request.user.is_superuser,
            "authenticated": True
        })
    return JsonResponse({
        "user_id": None,
        "username": None,
        "is_superuser": False,
        "authenticated": False
    })

@csrf_exempt
def edit_discussion_json(request, pk):
    """Edit an existing discussion (only creator or superuser)"""
    if request.method == 'POST':
        try:
            discussion = get_object_or_404(Discussion, pk=pk)
            
            # Get user_id and is_superuser from POST data (from Flutter app)
            user_id = None
            is_superuser = False
            
            try:
                user_id = int(request.POST.get('user_id'))
                is_superuser = request.POST.get('is_superuser', 'false').lower() == 'true'
            except (TypeError, ValueError):
                pass
            
            # If no user_id from POST, try session auth
            if user_id is None and request.user.is_authenticated:
                user_id = request.user.id
                is_superuser = request.user.is_superuser
            
            if user_id is None:
                return JsonResponse({
                    "status": "error",
                    "message": "Not authenticated"
                }, status=401)
            
            # Check permissions
            can_edit = (discussion.username.id == user_id) or is_superuser
            
            if not can_edit:
                return JsonResponse({
                    "status": "error",
                    "message": "You do not have permission to edit this discussion"
                }, status=403)
            
            discuss = request.POST.get('discuss')
            
            if not discuss:
                return JsonResponse({
                    "status": "error",
                    "message": "Discussion content is required"
                }, status=400)
            
            # Update discussion
            discussion.discuss = discuss
            discussion.save()
            
            return JsonResponse({
                "status": "success",
                "message": "Discussion updated successfully",
                "pk": discussion.pk
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)

@csrf_exempt
def delete_discussion_json(request, pk):
    if request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        try:
            discussion = get_object_or_404(Discussion, pk=pk)
            
            user_id = None
            is_superuser = False
            
            if request.user.is_authenticated:
                user_id = request.user.id
                is_superuser = request.user.is_superuser
            else:
                try:
                    user_id = int(request.POST.get('user_id'))
                    is_superuser = request.POST.get('is_superuser', 'false').lower() == 'true'
                except (TypeError, ValueError):
                    pass
            
            if user_id is None:
                return JsonResponse({
                    "status": "error",
                    "message": "Not authenticated"
                }, status=401)
            
            # check permissions
            can_delete = (discussion.username.id == user_id) or is_superuser
            
            if not can_delete:
                return JsonResponse({
                    "status": "error",
                    "message": "You do not have permission to delete this discussion"
                }, status=403)
            
            discussion.delete()
            return JsonResponse({
                "status": "success",
                "message": "Discussion deleted successfully"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)

@csrf_exempt
def edit_forum_json(request, pk):
    if request.method == 'POST':
        try:
            forum = get_object_or_404(Forum, pk=pk)
            user_id = None
            is_superuser = False
            
            try:
                user_id = int(request.POST.get('user_id'))
                is_superuser = request.POST.get('is_superuser', 'false').lower() == 'true'
            except (TypeError, ValueError):
                pass
            if user_id is None and request.user.is_authenticated:
                user_id = request.user.id
                is_superuser = request.user.is_superuser
            
            if user_id is None:
                return JsonResponse({
                    "status": "error",
                    "message": "Not authenticated"
                }, status=401)
            
            can_edit = (forum.name.id == user_id) or is_superuser
            
            if not can_edit:
                return JsonResponse({
                    "status": "error",
                    "message": "You do not have permission to edit this forum"
                }, status=403)
            
            topic = request.POST.get('topic')
            description = request.POST.get('description')
            thumbnail = request.POST.get('thumbnail', '').strip()
            
            if not topic or not description:
                return JsonResponse({
                    "status": "error",
                    "message": "Topic and description are required"
                }, status=400)
            
            forum.topic = topic
            forum.description = description
            forum.thumbnail = thumbnail
            forum.save()
            
            return JsonResponse({
                "status": "success",
                "message": "Forum updated successfully",
                "pk": forum.pk
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)

@csrf_exempt
def delete_forum_json(request, pk):
    if request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        try:
            forum = get_object_or_404(Forum, pk=pk)
            
            user_id = None
            is_superuser = False
            
            if request.user.is_authenticated:
                user_id = request.user.id
                is_superuser = request.user.is_superuser
            else:
                try:
                    user_id = int(request.POST.get('user_id'))
                    is_superuser = request.POST.get('is_superuser', 'false').lower() == 'true'
                except (TypeError, ValueError):
                    pass
            
            if user_id is None:
                return JsonResponse({
                    "status": "error",
                    "message": "Not authenticated"
                }, status=401)
           
            can_delete = (forum.name == user_id) or is_superuser
            
            if not can_delete:
                return JsonResponse({
                    "status": "error",
                    "message": "You do not have permission to delete this forum"
                }, status=403)
            
            Discussion.objects.filter(forum=forum).delete()
            forum.delete()
            
            return JsonResponse({
                "status": "success",
                "message": "Forum deleted successfully"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)

@csrf_exempt
def add_forum_json(request):
    if request.method == 'POST':
        try:
            topic = request.POST.get('topic')
            description = request.POST.get('description')
            thumbnail = request.POST.get('thumbnail', '').strip()
            user = None
            
            if request.user.is_authenticated:
                user = request.user
            else:
                try:
                    user_id = int(request.POST.get('user_id'))
                    user = get_object_or_404(User, id=user_id)
                except (TypeError, ValueError):
                    pass
            
            if user is None:
                return JsonResponse({
                    "status": "error",
                    "message": "Not authenticated"
                }, status=401)
            
            if not topic or not description:
                return JsonResponse({
                    "status": "error",
                    "message": "Topic and description are required"
                }, status=400)
            
            forum = Forum.objects.create(
                name=user,
                topic=topic,
                description=description,
                thumbnail=thumbnail
            )
            
            return JsonResponse({
                "status": "success",
                "message": "Forum created successfully",
                "pk": forum.pk
            }, status=201)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=405)

@csrf_exempt
def add_discussion_json(request):
    if request.method == 'POST':
        try:
            forum_id = request.POST.get('forum')
            discuss = request.POST.get('discuss')
            username = request.POST.get('username') 
            
            if not forum_id or not discuss:
                return JsonResponse({
                    "status": "error", 
                    "message": "Missing forum or discussion content"
                }, status=400)
            
            user = None
            if request.user.is_authenticated:
                user = request.user
            elif username:
                from django.contrib.auth.models import User
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({
                        "status": "error", 
                        "message": "User not found"
                    }, status=400)
            else:
                return JsonResponse({
                    "status": "error", 
                    "message": "User not authenticated and username not provided"
                }, status=401)
            
            forum = get_object_or_404(Forum, pk=forum_id)
            discussion = Discussion.objects.create(
                username=user,
                forum=forum,
                discuss=discuss
            )
            return JsonResponse({
                "status": "success", 
                "message": "Discussion added successfully",
                "id": discussion.pk
            }, status=201)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({
                "status": "error", 
                "message": str(e)
            }, status=400)
    
    return JsonResponse({
        "status": "error", 
        "message": "Invalid request method"
    }, status=405)

# @login_required(login_url="/login")
@login_required(login_url='main:login_user')
def edit_forum(request, id):
    forum = get_object_or_404(Forum, id=id)
    
    if forum.name != request.user and not request.user.is_superuser:
        return redirect('forum_section:home') 
    
    if request.method == 'POST':
        form = ForumForm(request.POST, instance=forum)
        if form.is_valid():
            form.save()
            return redirect('forum_section:home') 
    else:
        form = ForumForm(instance=forum)
    
    return render(request, 'editForum.html', {'form': form, 'forum': forum})



# @login_required
@login_required(login_url='main:login_user')
def edit_discussion(request, id):
    discussion = get_object_or_404(Discussion, pk=id)

    if request.method == "POST":
        form = DiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            discussion.discuss = form.cleaned_data.get('discuss')
            discussion.save(update_fields=['discuss'])
            return redirect('forum_section:home')
    else:
        form = DiscussionForm(instance=discussion)

    return render(request, "editDiscussion.html", {"form": form, "discussion": discussion})


# @login_required(login_url="/login")
@login_required(login_url='main:login_user')
def home(request):
    forums = Forum.objects.all()
    count=forums.count()
    discussions=[]
    for i in forums:
        discussions.append(i.discussion_set.all())
 
    context={'forums':forums,
              'count':count,
              'discussions':discussions}
    return render(request,'home.html',context)



# @login_required(login_url="/login")
@login_required(login_url='main:login_user')
def addInForum(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum_entry = form.save(commit=False)
            forum_entry.name = request.user
            forum_entry.save()
            return JsonResponse({"success": True, "message": "Forum added successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Form is not valid."})
    else:
        form = ForumForm()

    return render(request, "addInForum.html", {"form": form})


# @login_required(login_url="/login")
@login_required(login_url='main:login_user')
def addInDiscussion(request, id):
    forum = get_object_or_404(Forum, id=id)
    form = DiscussionForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        form_entry = form.save(commit=False)
        form_entry.username = request.user
        form_entry.forum = forum
        form_entry.save()
        return redirect('forum_section:home')

    context = {
        'form': form,
        'forum': forum
    }

    return render(request, "addInDiscussion.html", context)

 
 
# legacy functions

# @login_required(login_url="/login")
@login_required(login_url='main:login_user')
def show_main(request):
    context = {
    'npm': '240123456',
    'name': request.user.username,
    'class': 'PBP A',
    'last_login': request.COOKIES.get('last_login', 'Never')
}

    return render(request, "main.html", context)   

@require_POST
# @login_required
@login_required(login_url='main:login_user')
def delete_discussion(request, id):
    discussion = get_object_or_404(Discussion, pk=id, username=request.user)
    discussion.delete()
    return redirect('forum_section:home')

@require_POST

# @login_required(login_url="/login")
@login_required(login_url='main:login_user')
def delete_forum(request, id):
    forum = get_object_or_404(Forum, pk=id, name=request.user)
    forum.delete()
    return JsonResponse({"success": True})

    
def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('forum_section:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
        user = form.get_user()
        login(request, user)
        response = HttpResponseRedirect(reverse("forum_section:show_main"))
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('forum_section:login'))
    response.delete_cookie('last_login')
    return response
