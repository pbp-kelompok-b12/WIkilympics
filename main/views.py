#sources in case I forget:
#https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-display/


from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from .forms import *
# Create your views here.
from django.views.generic.edit import CreateView


@login_required(login_url="/login")
def edit_forum(request, id):
    forum = get_object_or_404(Forum, id=id)
    
    if forum.name != request.user and not request.user.is_superuser:
        return redirect('main:home') 
    
    if request.method == 'POST':
        form = CreateInForum(request.POST, instance=forum)
        if form.is_valid():
            form.save()
            return redirect('main:home')
    else:
        form = CreateInForum(instance=forum)
    
    return render(request, 'editForum.html', {'form': form})



@login_required(login_url="/login")
def edit_discussion(request, id):
    discussion = get_object_or_404(Discussion, id=id)
    
    if discussion.username != request.user and not request.user.is_superuser:
        return redirect('main:home')  
    
    if request.method == 'POST':
        form = CreateInDiscussion(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            return redirect('main:home')
    else:
        form = CreateInDiscussion(instance=discussion)
    
    return render(request, 'editDiscussion.html', {'form': form})


@login_required(login_url="/login")
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
 
def addInForum(request):
    form = CreateInForum()
    if request.method == 'POST':
        form = CreateInForum(request.POST)
        if form.is_valid():
            form_entry = form.save(commit=False)
            form_entry.name = request.user
            form_entry.save()
            return redirect('/')
    context ={'form':form}
    return render(request,'addInForum.html',context)


@login_required(login_url="/login")
def addInDiscussion(request):
    form = CreateInDiscussion()
    if request.method == 'POST':
        form = CreateInDiscussion(request.POST)
        if form.is_valid():
            form_entry = form.save(commit=False)
            form_entry.username = request.user
            form_entry.save()
            return redirect('/')
    context ={'form':form}
    return render(request,'addInDiscussion.html',context)
 
 
# legacy functions

@login_required(login_url="/login")
def show_main(request):
    context = {
    'npm': '240123456',
    'name': request.user.username,
    'class': 'PBP A',
    'last_login': request.COOKIES.get('last_login', 'Never')
}

    return render(request, "main.html", context)   

@require_POST
@login_required
def delete_discussion(request, id):
    discussion = get_object_or_404(Discussion, pk=id, username=request.user)
    discussion.delete()
    return redirect('main:home')

@require_POST

@login_required(login_url="/login")
def delete_forum(request, id):
    forum = get_object_or_404(Forum, pk=id,name=request.user )
    forum.delete()
    return redirect('main:home')
    
def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
        user = form.get_user()
        login(request, user)
        response = HttpResponseRedirect(reverse("main:show_main"))
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response
