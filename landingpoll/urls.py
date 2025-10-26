from django.urls import path
from . import views

app_name = 'landingpoll'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('vote/<int:option_id>/', views.vote_poll, name='vote_poll'),
    path('delete/<int:poll_id>/', views.delete_poll, name='delete_poll'),
]
