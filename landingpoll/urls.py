from django.urls import path
from . import views

app_name = 'landingpoll'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('vote/<int:option_id>/', views.vote_poll, name='vote_poll'),
    path('landingpoll/delete/<int:poll_id>/', views.delete_poll, name='delete_poll'),
    
    path('polls/json/', views.polls_api, name='polls_api'),
    path('landingpoll/create/', views.create_poll_flutter, name='create_poll_flutter'),
    path('landingpoll/edit/<int:poll_id>/', views.edit_poll_flutter, name='edit_poll_flutter'),
]