from django.urls import path
from ..views.note_views import create_note

urlpatterns = [path("", create_note)]
