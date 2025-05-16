from django.urls import path
from ..views.user_views import create_user, login

urlpatterns = [path("", create_user), path("login/", login)]
