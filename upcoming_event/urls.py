from django.urls import path
from .views import proxy_image, create_event_flutter
from django.utils.html import strip_tags
from . import views

app_name = "upcoming_event"

urlpatterns = [
    path("", views.daftar_event, name="daftar_event"),

    # Tambah dan edit event 
    path("add/", views.add_event, name="add_event"),
    path("<int:event_id>/edit/", views.edit_event, name="edit_event"),
    path("<int:event_id>/delete/", views.delete_event, name="delete_event"),

    #  Lihat Detail (JS)
    path("get-event-json/<int:id>/", views.get_event_json, name="get_event_json"),

    # Detail satu event
    path("<int:event_id>/", views.detail_event, name="detail_event"),

    # json
    path('json/', views.show_json, name='show_json'),

    # tk
    path('proxy-image/', proxy_image, name='proxy_image'),
    path('create-event-flutter/', create_event_flutter, name='create_event_flutter'),
    path('edit-event-flutter/<int:event_id>/', views.edit_event_flutter, name='edit_event_flutter'),
    path('delete-event-flutter/<int:event_id>/', views.delete_event_flutter, name='delete_event_flutter'),
]
