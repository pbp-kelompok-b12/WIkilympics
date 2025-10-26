#sources in case I forget:
#https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-display/


from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import *
from .forms import *
# Create your views here.
from django.views.generic.edit import CreateView


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
