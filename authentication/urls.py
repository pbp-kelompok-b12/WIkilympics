from django.urls import path
from authentication.views import login, register, logout, get_user_status

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('status/', get_user_status, name="get_user_status"),
]