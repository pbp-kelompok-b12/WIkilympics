from django.urls import path
from main.views import *
from django.contrib import admin

app_name = 'main'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='home'),
    path('add-forum/',addInForum,name='addInForum'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('add-discussion/',addInDiscussion,name='addInDiscussion'),
]