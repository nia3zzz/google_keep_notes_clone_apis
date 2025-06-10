from django.urls import path
from ..views.user_views import create_or_get_user, login, logout

urlpatterns = [
    path("", create_or_get_user),
    path("login/", login),
    path("logout/", logout),
]
