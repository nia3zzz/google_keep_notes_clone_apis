from django.urls import path
from ..views.note_views import create_note, update_note

urlpatterns = [path("", create_note), path("<uuid:note_id>/", update_note)]
