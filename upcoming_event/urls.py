from django.urls import path
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
]
