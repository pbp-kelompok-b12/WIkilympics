from django.urls import path
from main.views import register, login_user, logout_user

app_name = 'main'

urlpatterns = [
    path('register/', register, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout'),
]