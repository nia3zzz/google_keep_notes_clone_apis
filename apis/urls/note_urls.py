from django.urls import path
from ..views.note_views import (
    create_note,
    update_note,
    get_notes,
    add_remove_collaborator,
)

urlpatterns = [
    path("", create_note),
    path("<uuid:note_id>/", update_note),
    path("getnotes/", get_notes),
    path("collaborators/<uuid:note_id>/", add_remove_collaborator),
]
