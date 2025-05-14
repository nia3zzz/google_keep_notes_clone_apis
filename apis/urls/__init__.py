from django.urls import include, path

urlpatterns = [
    path("users/", include("apis.urls.user_urls")),
]
