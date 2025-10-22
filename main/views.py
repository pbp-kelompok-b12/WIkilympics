#sources in case I forget:
#https://docs.djangoproject.com/en/5.2/ref/class-based-views/generic-display/



from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy #url finder, defers until its actually needed, sidenote: might switch back to reverse
from .models import Thread, Post
# Create your views here.

class ThreadListView(ListView):
    model = Thread

class ThreadDetailView(DetailView):
    model = Thread

class CreateThreadView(CreateView):
    model = Thread
    fields = ['title']
    success_url = reverse_lazy('thread_list')

class CreatePostView(CreateView):
    model = Post
    fields = ['content']
    
    def form_valid(self, form):
        form.instance.thread_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('thread_detail', kwargs = {'pk' : self.kwargs['pk']})
    
    
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
            return redirect('main:show_main')

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect('main:login')
